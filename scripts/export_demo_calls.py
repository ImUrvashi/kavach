"""Save the demo calls as WAV files you can play from a phone or speaker.

Usage:
    python scripts/export_demo_calls.py                      # every demo call, every language
    python scripts/export_demo_calls.py --lang hi-IN --script family

Each call is spoken by Timbre (a stock voice, never the cloned family voice),
exactly as the audio demo plays it, and saved to cache/demo_calls/ as
<language>_<script>.wav (16 kHz). Uses Timbre credits only for lines not
already saved.

Uses:
- Play one from a second phone near the laptop in live mode, for a realistic
  demo video without an actor.
- Feed them to scripts/stream_file.py for the Day 3 benchmark.
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402
from app.demo_audio import RATE, build_demo_call, pcm_to_wav  # noqa: E402
from app.mock_calls import CALLS  # noqa: E402


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["hi-IN", "en-IN", "kn-IN"])
    ap.add_argument("--script", help="e.g. scam, family, upi, job, investment, customer_care, legit")
    args = ap.parse_args()
    if not config.GNANI_API_KEY:
        sys.exit("Add GNANI_API_KEY to .env first.")
    out = config.ROOT / "cache" / "demo_calls"
    out.mkdir(parents=True, exist_ok=True)
    for lang, script in sorted(CALLS):
        if (args.lang and lang != args.lang) or (args.script and script != args.script):
            continue
        pcm = await build_demo_call(lang, script)
        if pcm is None:
            print(f"[FAILED] {lang} {script}")
            continue
        path = out / f"{lang}_{script}.wav"
        path.write_bytes(pcm_to_wav(pcm))
        print(f"[ok] {path.name}  {len(pcm) / RATE:.1f} s")
    print(f"\nSaved in {out}")


if __name__ == "__main__":
    asyncio.run(main())
