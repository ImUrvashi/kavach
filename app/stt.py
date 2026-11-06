"""Speech-to-text sessions: Gnani Prisma (realtime WebSocket) and a demo-mode mock.

Both expose the same interface:
    await session.connect()
    await session.send_frame(frame_bytes)   # exactly 1024 bytes of 16 kHz PCM16 mono
    async for event in session.events(): ...  # dicts like {"type": "transcript", "text": ...}
    await session.close()
"""
import asyncio
import json
import logging
import time

from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import ConnectionClosed

from . import config
from .lexicon import BOOST_WORDS
from .mock_calls import get_call

log = logging.getLogger("kavach.stt")


class GnaniSTTSession:
    def __init__(self, lang_code: str):
        self.lang_code = lang_code
        self.ws = None
        self.started_at = 0.0
        self._closed = False
        self._lock = asyncio.Lock()

    def _headers(self) -> dict:
        h = {
            "x-api-key-id": config.GNANI_API_KEY,
            # The reference docs name this header `lang_code`, the quick start uses
            # `language_code`. Sending both is harmless.
            "lang_code": self.lang_code,
            "language_code": self.lang_code,
            "x-sample-rate": str(config.SAMPLE_RATE),
            "x-format": "verbatim",  # word boosting needs verbatim
            # VAD tuned for a phone on speakerphone in a room:
            "x-vad-threshold": "0.6",
            "x-min-speech-ms": "200",
            "x-min-silence-ms": "500",
            # Scammers talk in long monologues; force a transcript every 12 s so we never wait.
            "x-max-speech-s": "12",
        }
        if config.STT_MODEL:
            h["model"] = config.STT_MODEL
        if config.USE_WORD_BOOST:
            words = BOOST_WORDS.get(self.lang_code[:2], BOOST_WORDS["en"])
            h["x-bias-list"] = json.dumps(words)  # ASCII-safe \u escapes for Indic words
            h["x-bias-score"] = "1.0"
        return h

    async def connect(self):
        self.ws = await ws_connect(config.STT_URL, additional_headers=self._headers(),
                                   max_size=None, open_timeout=15)
        self.started_at = time.monotonic()
        log.info("Connected to Prisma (%s)", self.lang_code)

    async def _reconnect(self, old):
        async with self._lock:
            if self._closed or self.ws is not old:
                return  # someone else already reconnected
            log.info("Reconnecting to Prisma")
            await self.connect()
            try:
                await old.close()
            except Exception:
                pass

    async def send_frame(self, frame: bytes):
        if self._closed or self.ws is None:
            return
        if time.monotonic() - self.started_at > config.SESSION_ROTATE_S:
            await self._reconnect(self.ws)  # stay under Gnani's 15-minute session cap
        try:
            await self.ws.send(frame)
        except ConnectionClosed:
            pass  # events() notices and reconnects; dropping a 32 ms frame is fine

    async def events(self):
        while not self._closed:
            ws = self.ws
            try:
                async for raw in ws:
                    if isinstance(raw, bytes):
                        continue
                    try:
                        yield json.loads(raw)
                    except json.JSONDecodeError:
                        log.warning("Non-JSON message from Prisma: %r", raw[:200])
            except ConnectionClosed as e:
                log.info("Prisma connection closed: %s", e)
            if self._closed:
                break
            if self.ws is ws:
                await asyncio.sleep(0.5)
                await self._reconnect(ws)

    async def close(self):
        self._closed = True
        if self.ws is not None:
            try:
                await self.ws.close()
            except Exception:
                pass


class MockSTTSession:
    """Demo mode: ignores audio and 'hears' a scripted synthetic call."""

    def __init__(self, lang_code: str, script: str = "scam"):
        self.lines = get_call(lang_code, script)
        self._closed = False

    async def connect(self):
        pass

    async def send_frame(self, frame: bytes):
        pass

    async def events(self):
        yield {"type": "connected", "message": "Demo mode"}
        for i, line in enumerate(self.lines):
            await asyncio.sleep(config.MOCK_LINE_INTERVAL_S)
            if self._closed:
                return
            yield {"type": "transcript", "text": line, "segment_index": i, "latency": 0}
        while not self._closed:
            await asyncio.sleep(0.5)

    async def close(self):
        self._closed = True
