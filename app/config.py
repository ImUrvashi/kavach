"""Kavach configuration. Values come from the .env file (see .env.example)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

GNANI_API_KEY = os.getenv("GNANI_API_KEY", "").strip()

# With no API key, Kavach runs in demo mode with scripted calls (no mic, no Gnani calls).
MOCK_MODE = os.getenv("KAVACH_MOCK", "0") == "1" or not GNANI_API_KEY
MOCK_LINE_INTERVAL_S = float(os.getenv("KAVACH_MOCK_INTERVAL", "3.5"))

# Prisma speech-to-text (realtime WebSocket)
STT_URL = os.getenv("GNANI_STT_URL", "wss://api.vachana.ai/stt/v3/stream")
STT_MODEL = os.getenv("GNANI_STT_MODEL", "")  # empty = Prisma v2.5 (default); or "prisma-v3.0"
SAMPLE_RATE = 16000
FRAME_BYTES = 1024  # Gnani requires exactly 1024-byte frames (512 samples of 16-bit PCM)
SESSION_ROTATE_S = 14 * 60  # Gnani caps a session at 15 minutes; reconnect just before
USE_WORD_BOOST = os.getenv("KAVACH_WORD_BOOST", "1") == "1"

# Timbre text-to-speech
TTS_URL = os.getenv("GNANI_TTS_URL", "https://api.vachana.ai/api/v1/tts/inference")
TTS_MODEL = os.getenv("GNANI_TTS_MODEL", "timbre-v2.5")
TTS_VOICE = {
    "hi": os.getenv("GNANI_TTS_VOICE_HI", "Nalini"),
    "kn": os.getenv("GNANI_TTS_VOICE_KN", "Nalini"),
}
TTS_SPEED = float(os.getenv("GNANI_TTS_SPEED", "0.9"))  # a little slower = calmer
VC_MODEL = os.getenv("GNANI_VC_MODEL", "vachana-vc-v1")
VOICE_EMBEDDING_PATH = ROOT / os.getenv("KAVACH_VOICE_EMBEDDING", "voice/embedding.json")
TTS_CACHE_DIR = ROOT / "cache" / "tts"

# Audible demo calls (with a key): the scripted caller is spoken by Timbre and
# streamed through Prisma. Pick a different stock voice for the caller in .env
# (for example a male voice from Gnani's voice catalogue); it defaults to the
# warning voice. The caller never uses the cloned family voice.
DEMO_CALLER_VOICE = {
    "hi": os.getenv("GNANI_DEMO_VOICE_HI") or TTS_VOICE["hi"],
    "kn": os.getenv("GNANI_DEMO_VOICE_KN") or TTS_VOICE["kn"],
    "en": os.getenv("GNANI_DEMO_VOICE_EN") or TTS_VOICE["hi"],
}
DEMO_LEAD_S = 0.6   # silence before the caller starts
DEMO_GAP_S = 0.9    # pause between the caller's sentences (Prisma needs 0.5 s to end a sentence)
DEMO_TAIL_S = 2.5   # silence at the end, so Prisma returns the last sentence

# Risk thresholds (0-100)
LEVEL_CAUTION = 40
LEVEL_WARN = 70
LEVEL_ALERT = 85
