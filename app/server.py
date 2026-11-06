"""Kavach backend.

Browser mic --(PCM16 16 kHz frames over /ws)--> this server --> Gnani Prisma
Prisma transcripts --> ScamDetector --> UI updates + Timbre spoken warnings

Demo calls with a key take the same path, except the audio comes from a
scripted call spoken by Timbre (demo_audio.py) instead of the mic.

The browser cannot set the custom headers Gnani needs, and the API key must
never reach the browser, so all Gnani traffic goes through here.
"""
import asyncio
import base64
import json
import logging
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .demo_audio import build_demo_call, pcm_to_wav, to_frames
from .detector import LEVEL_NAMES, ScamDetector
from .stt import GnaniSTTSession, MockSTTSession
from .tts import load_voice_embedding, synthesize
from .ask_caller import ask_for
from .warnings_text import SCAM_NAMES, warning_for, warnings_to_speak

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("kavach")

app = FastAPI(title="Kavach")
STATIC = config.ROOT / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")

SILENCE = bytes(config.FRAME_BYTES)


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


@app.get("/config")
async def get_config():
    return {
        "mock": config.MOCK_MODE,
        "has_key": bool(config.GNANI_API_KEY),
        "cloned_voice": load_voice_embedding() is not None,
        # Names of the scams Kavach knows, listed on the start screen.
        "scams": [name for kind, name in SCAM_NAMES.items() if kind != "generic"],
    }


@app.websocket("/ws")
async def call_socket(ws: WebSocket, lang: str = "hi-IN", demo: int = 0, script: str = "scam"):
    await ws.accept()
    # Three kinds of call:
    #   live        the browser's mic → Prisma
    #   audio demo  demo=1 with a key: a scripted call spoken by Timbre → Prisma
    #   text demo   no key: the scripted lines go straight to the detector
    text_demo = config.MOCK_MODE
    audio_demo = demo == 1 and not text_demo
    detector = ScamDetector()
    state = {"muted": False, "active": True}
    speaking_tasks: set[asyncio.Task] = set()
    t0 = time.monotonic()

    async def send(msg: dict):
        try:
            await ws.send_json(msg)
        except Exception:
            state["active"] = False

    demo_pcm = None
    if audio_demo:
        await send({"type": "preparing"})  # the first time, Timbre takes a few seconds per line
        demo_pcm = await build_demo_call(lang, script)
        if demo_pcm is None:
            log.warning("Timbre could not make the demo call audio; using the text-only demo")
            await send({"type": "notice", "message": "Couldn't make the demo call's audio, so this is a text-only demo."})
            audio_demo, text_demo = False, True

    stt = MockSTTSession(lang, script) if text_demo else GnaniSTTSession(lang)

    try:
        await stt.connect()
    except Exception as e:
        log.exception("Could not connect to Prisma")
        await send({"type": "error", "message": f"Could not connect to Gnani Prisma: {e}. "
                                                "Check GNANI_API_KEY in .env and your credits."})
        await ws.close()
        return

    t0 = time.monotonic()  # the call's clock starts now, after any preparation
    await send({"type": "ready", "mock": text_demo, "audio_demo": audio_demo, "lang": lang})

    # One warning at a time, in the order they were triggered: asyncio.Lock
    # wakes waiters first-come first-served, so a slow (uncached) clip can
    # never let a later warning overtake it.
    speak_lock = asyncio.Lock()

    async def speak_warning(scam_type: str, final: bool):
        async with speak_lock:
            await _speak(scam_type, final)

    async def _speak(scam_type: str, final: bool):
        wlang, spoken, display = warning_for(lang, scam_type, final)
        audio = await synthesize(spoken, wlang)
        await send({
            "type": "warning",
            "final": final,
            "scam_type": scam_type,
            "scam_name": SCAM_NAMES.get(scam_type, SCAM_NAMES["generic"]),
            "text": display,
            "ask": ask_for(lang, scam_type),  # "Ask the caller" questions for the screen
            "audio": base64.b64encode(audio).decode() if audio else None,
            "t": round(time.monotonic() - t0, 1),
        })

    async def pump_audio():
        buf = bytearray()
        while state["active"]:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                break
            if msg.get("bytes"):
                buf.extend(msg["bytes"])
                while len(buf) >= config.FRAME_BYTES:
                    frame = bytes(buf[:config.FRAME_BYTES])
                    del buf[:config.FRAME_BYTES]
                    # While Kavach is speaking, send silence so Prisma does not
                    # transcribe our own warning (and the timing stays real-time).
                    await stt.send_frame(SILENCE if state["muted"] else frame)
            elif msg.get("text"):
                data = json.loads(msg["text"])
                if data.get("type") == "playback":
                    state["muted"] = data.get("state") == "start"
                elif data.get("type") == "stop":
                    break

    async def pump_transcripts():
        async for ev in stt.events():
            kind = ev.get("type")
            if kind == "transcript" and ev.get("text", "").strip():
                t = time.monotonic() - t0
                prev_level = detector.level
                r = detector.update(ev["text"], t)
                await send({
                    "type": "transcript",
                    "text": ev["text"],
                    "t": round(t, 1),
                    "latency_ms": ev.get("latency"),
                    "risk": r.risk,
                    "level": r.level,
                    "level_name": LEVEL_NAMES[r.level],
                    "scam_type": r.scam_type,
                    "matches": [m.__dict__ for m in r.matches],
                    "new_categories": r.new_categories,
                })
                # Level 2: tailored warning. Level 3: firm "hang up now".
                # A jump straight to level 3 speaks both, tailored first.
                for final in warnings_to_speak(prev_level, r.level):
                    task = asyncio.create_task(speak_warning(r.scam_type, final))
                    speaking_tasks.add(task)
                    task.add_done_callback(speaking_tasks.discard)
            elif kind == "error":
                await send({"type": "error", "message": f"Prisma: {ev.get('message')}"})

    async def pump_demo():
        """Audio demo: send the browser the recording to play, stream the same
        recording to Prisma at real-time speed, then end the call."""
        await send({"type": "demo_audio", "audio": base64.b64encode(pcm_to_wav(demo_pcm)).decode()})
        frame_s = config.FRAME_BYTES / 2 / config.SAMPLE_RATE  # 32 ms
        start = time.monotonic()
        for i, frame in enumerate(to_frames(demo_pcm)):
            if not state["active"]:
                return
            # Never muted: a demo has no mic, so Kavach can't hear its own warning.
            await stt.send_frame(frame)
            wait = start + (i + 1) * frame_s - time.monotonic()  # keep to real time, without drift
            if wait > 0:
                await asyncio.sleep(wait)
        await asyncio.sleep(1.5)  # Prisma returns the last sentence
        if speaking_tasks:  # let any warning still being made reach the page before the report
            await asyncio.wait(set(speaking_tasks), timeout=10)

    audio_task = asyncio.create_task(pump_audio())
    text_task = asyncio.create_task(pump_transcripts())
    tasks = {audio_task, text_task}
    if audio_demo:
        tasks.add(asyncio.create_task(pump_demo()))
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    except WebSocketDisconnect:
        pass
    finally:
        for task in tasks:
            task.cancel()
        await stt.close()
        summary = detector.summary(time.monotonic() - t0)
        summary["scam_name"] = SCAM_NAMES.get(summary["scam_type"]) if detector.level >= 2 else None
        log.info("Call summary: %s", summary)
        await send({"type": "summary", **summary})
        try:
            await ws.close()
        except Exception:
            pass
