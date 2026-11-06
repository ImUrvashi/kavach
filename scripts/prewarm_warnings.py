"""Generate every warning clip once so warnings play instantly during calls.

Usage:
    python scripts/prewarm_warnings.py          # uses the cloned voice if voice/embedding.json exists
    python scripts/prewarm_warnings.py --stock  # stock Timbre voices only

Clips are saved in cache/tts/ and also copied to cache/listen/ with readable
names so you can play them and check how they sound.
"""
import asyncio
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402
from app.tts import _cache_path, _payload, load_voice_embedding, synthesize  # noqa: E402
from app.warnings_text import all_warnings  # noqa: E402


async def main():
    if not config.GNANI_API_KEY:
        sys.exit("Add GNANI_API_KEY to .env first.")
    use_clone = "--stock" not in sys.argv
    emb = load_voice_embedding() if use_clone else None
    listen = config.ROOT / "cache" / "listen"
    listen.mkdir(parents=True, exist_ok=True)
    ok = 0
    for lang, key, text in all_warnings():
        audio = await synthesize(text, lang, use_clone=use_clone)
        status = "ok" if audio else "FAILED"
        print(f"[{status}] {lang} {key}")
        if audio:
            ok += 1
            src = _cache_path(_payload(text, lang, emb))
            if src.exists():
                shutil.copy(src, listen / f"{lang}_{key}{'_clone' if emb else ''}.wav")
    print(f"\n{ok} clips ready. Listen to them in {listen}")


if __name__ == "__main__":
    asyncio.run(main())
