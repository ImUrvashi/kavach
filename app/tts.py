"""Text-to-speech with Gnani Timbre, optionally in a cloned family voice.

Warnings are fixed sentences, so every clip is cached on disk after the first
call. Run scripts/prewarm_warnings.py once and warnings play instantly during
a call and cost no extra credits.
"""
import asyncio
import hashlib
import json
import logging
import weakref

import httpx

from . import config

log = logging.getLogger("kavach.tts")

# Timbre allows only ONE active request per account at a time; a second one
# gets "429 RATE_LIMITED". So requests wait their turn in a queue (one lock per
# event loop), and a 429 from elsewhere (say, another Kavach window) is retried
# after a short, growing wait. Found by the first full benchmark run (WORKLOG #27).
RETRIES = 4
RETRY_WAIT_S = 1.5
_LOCKS: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock]" = weakref.WeakKeyDictionary()


def _timbre_lock() -> asyncio.Lock:
    loop = asyncio.get_running_loop()
    lock = _LOCKS.get(loop)
    if lock is None:
        lock = _LOCKS[loop] = asyncio.Lock()
    return lock


async def _post(payload: dict) -> httpx.Response:
    """Send one request to Timbre, one at a time, retrying while Timbre is busy."""
    async with _timbre_lock():
        for attempt in range(RETRIES):
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(config.TTS_URL, json=payload,
                                      headers={"X-API-Key-ID": config.GNANI_API_KEY})
            if r.status_code != 429 or attempt == RETRIES - 1:
                return r
            wait = RETRY_WAIT_S * (attempt + 1)
            log.warning("Timbre busy (429); retrying in %.1f s", wait)
            await asyncio.sleep(wait)


def load_voice_embedding() -> dict | None:
    p = config.VOICE_EMBEDDING_PATH
    if p.exists():
        return json.loads(p.read_text())
    return None


TTS_LANGUAGE = {"hi": "hi-IN", "kn": "kn-IN", "en": "en-IN"}


def _payload(text: str, lang: str, embedding: dict | None, voice: str | None = None) -> dict:
    if embedding:
        return {
            "text": text,
            "model": config.VC_MODEL,
            "audio_config": {"sample_rate": 44100, "num_channels": 1, "sample_width": 2,
                             "encoding": "linear_pcm", "container": "wav"},
            "speaker_embedding": embedding,
        }
    return {
        "text": text,
        "voice": voice or config.TTS_VOICE.get(lang, "Nalini"),
        "model": config.TTS_MODEL,
        "language": TTS_LANGUAGE.get(lang, "hi-IN"),
        "speed": config.TTS_SPEED,
        "audio_config": {"sample_rate": 48000, "num_channels": 1, "sample_width": 2,
                         "encoding": "linear_pcm", "container": "wav"},
    }


def _cache_path(payload: dict):
    key = hashlib.sha1(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]
    return config.TTS_CACHE_DIR / f"{key}.wav"


async def synthesize(text: str, lang: str, use_clone: bool = True, voice: str | None = None) -> bytes | None:
    """Returns WAV bytes, or None if there is no API key or the request fails.

    `lang` is "hi", "kn" or "en". `voice` picks a stock voice other than the
    warning voice (used for the caller in demo calls, which never uses the
    cloned family voice).
    """
    embedding = load_voice_embedding() if use_clone else None
    payload = _payload(text, lang, embedding, voice)
    path = _cache_path(payload)
    if path.exists():
        return path.read_bytes()
    if not config.GNANI_API_KEY:
        return None
    try:
        r = await _post(payload)
        if r.status_code != 200:
            log.error("Timbre error %s: %s", r.status_code, r.text[:300])
            if embedding:  # fall back to a stock voice rather than staying silent
                return await synthesize(text, lang, use_clone=False)
            return None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(r.content)
        return r.content
    except httpx.HTTPError as e:
        log.error("Timbre request failed: %s", e)
        return None
