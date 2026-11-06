"""Create a voice-clone embedding so Kavach warns in a family member's voice.

Usage:
    python scripts/clone_voice.py path/to/reference.wav

Record 10-20 seconds of the family member speaking naturally in a quiet room
(WAV or MP3). Use your own voice or a family member's, and only with their
clear consent. Never clone anyone else's voice.
"""
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402

URL = "https://api.vachana.ai/api/v1/tts/voice-clone/embeddings"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if not config.GNANI_API_KEY:
        sys.exit("Add GNANI_API_KEY to .env first.")
    ref = Path(sys.argv[1])
    with ref.open("rb") as f:
        r = httpx.post(URL, headers={"X-API-Key-ID": config.GNANI_API_KEY},
                       files={"audio_file": (ref.name, f)}, timeout=60)
    if r.status_code != 200:
        sys.exit(f"Gnani returned {r.status_code}: {r.text[:300]}")
    emb = r.json()
    config.VOICE_EMBEDDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.VOICE_EMBEDDING_PATH.write_text(json.dumps(emb))
    print(f"Saved voice embedding to {config.VOICE_EMBEDDING_PATH}")
    print("Now run: python scripts/prewarm_warnings.py")


if __name__ == "__main__":
    main()
