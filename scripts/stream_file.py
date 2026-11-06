"""Stream a recorded (synthetic) call through Prisma and the scam detector.

Usage:
    python scripts/stream_file.py call.wav --lang hi-IN

Prints each transcript with the running risk score, then a summary. The audio
is sent at real-time speed, as Gnani's realtime API requires, so a 60-second
file takes about 60 seconds. This is the building block for the benchmark.
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402
from app.detector import ScamDetector  # noqa: E402
from app.stt import GnaniSTTSession  # noqa: E402


def load_pcm16(path: str) -> bytes:
    audio, sr = sf.read(path, dtype="float32", always_2d=True)
    audio = audio.mean(axis=1)  # mono
    if sr != config.SAMPLE_RATE:
        n_out = int(len(audio) * config.SAMPLE_RATE / sr)
        audio = np.interp(np.linspace(0, len(audio) - 1, n_out), np.arange(len(audio)), audio)
    audio = np.clip(audio, -1, 1)
    return (audio * 32767).astype("<i2").tobytes()


async def run(path: str, lang: str, tail_s: float = 3.0) -> dict:
    pcm = load_pcm16(path)
    frames = [pcm[i:i + config.FRAME_BYTES] for i in range(0, len(pcm), config.FRAME_BYTES)]
    frames[-1] = frames[-1].ljust(config.FRAME_BYTES, b"\0")
    frame_s = config.FRAME_BYTES / 2 / config.SAMPLE_RATE  # 32 ms

    stt = GnaniSTTSession(lang)
    await stt.connect()
    det = ScamDetector()
    t0 = time.monotonic()

    async def send():
        for f in frames + [bytes(config.FRAME_BYTES)] * int(tail_s / frame_s):  # trailing silence flushes VAD
            await stt.send_frame(f)
            await asyncio.sleep(frame_s)

    async def receive():
        async for ev in stt.events():
            if ev.get("type") == "transcript" and ev.get("text", "").strip():
                t = time.monotonic() - t0
                r = det.update(ev["text"], t)
                flags = ",".join(sorted({m.category for m in r.matches})) or "-"
                print(f"[{t:5.1f}s] risk {r.risk:3d}  {ev['text']}   ({flags})")
            elif ev.get("type") == "error":
                print("Prisma error:", ev.get("message"))

    recv_task = asyncio.create_task(receive())
    await send()
    await asyncio.sleep(1.5)
    recv_task.cancel()
    await stt.close()
    return det.summary(time.monotonic() - t0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--lang", default="hi-IN", choices=["hi-IN", "en-IN", "kn-IN"])
    args = ap.parse_args()
    if not config.GNANI_API_KEY:
        sys.exit("Add GNANI_API_KEY to .env first.")
    summary = asyncio.run(run(args.audio, args.lang))
    print(json.dumps(summary, indent=2, ensure_ascii=False))
