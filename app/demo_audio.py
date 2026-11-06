"""Audible demo calls: a scripted call, spoken by Timbre, as one recording.

With an API key, a demo call runs through the real pipeline: each scripted
line of the caller is spoken by Timbre, the lines are joined with short
pauses into one 16 kHz recording, and the server streams that recording to
Prisma frame by frame at real-time speed, exactly as if it came from the
mic. The browser plays the same recording so you hear the "caller". The
transcript and risk score are therefore real Prisma output, not the script.

Each line's clip is saved by tts.py, so a demo call costs Timbre credits only
the first time; Prisma is used for the length of the call every time.
"""
import io

import numpy as np
import soundfile as sf

from . import config
from .mock_calls import get_call
from .tts import synthesize

RATE = config.SAMPLE_RATE  # 16 kHz, what Prisma expects
TTS_LANG = {"hi-IN": "hi", "en-IN": "en", "kn-IN": "kn"}


def wav_to_pcm16k(wav: bytes) -> np.ndarray:
    """Any WAV (Timbre sends 48 kHz) → mono 16 kHz signed 16-bit samples."""
    audio, sr = sf.read(io.BytesIO(wav), dtype="float32", always_2d=True)
    audio = audio.mean(axis=1)
    if sr != RATE:
        if sr % RATE == 0:
            # 48 kHz → 16 kHz: average each group of 3 samples (also removes
            # sound too high-pitched for 16 kHz, like the browser's worklet does).
            k = sr // RATE
            audio = audio[: len(audio) // k * k].reshape(-1, k).mean(axis=1)
        else:
            n = int(len(audio) * RATE / sr)
            audio = np.interp(np.linspace(0, len(audio) - 1, n), np.arange(len(audio)), audio)
    return (np.clip(audio, -1, 1) * 32767).astype("<i2")


def pcm_to_wav(pcm: np.ndarray) -> bytes:
    """16 kHz samples → WAV bytes the browser can play."""
    buf = io.BytesIO()
    sf.write(buf, pcm, RATE, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def silence(seconds: float) -> np.ndarray:
    return np.zeros(int(seconds * RATE), dtype="<i2")


async def build_demo_call(stt_lang: str, script: str) -> np.ndarray | None:
    """The whole scripted call as one 16 kHz recording, or None if Timbre fails.

    Layout: a short lead-in, each line followed by a pause, and a longer tail
    so Prisma returns the last sentence.
    """
    lang = TTS_LANG.get(stt_lang, "hi")
    parts = [silence(config.DEMO_LEAD_S)]
    for line in get_call(stt_lang, script):
        wav = await synthesize(line, lang, use_clone=False, voice=config.DEMO_CALLER_VOICE.get(lang))
        if wav is None and lang == "en":
            # If Timbre won't read English, the Hindi voice can read Hinglish.
            wav = await synthesize(line, "hi", use_clone=False, voice=config.DEMO_CALLER_VOICE.get("hi"))
        if wav is None:
            return None
        parts += [wav_to_pcm16k(wav), silence(config.DEMO_GAP_S)]
    parts.append(silence(config.DEMO_TAIL_S))
    return np.concatenate(parts)


def to_frames(pcm: np.ndarray) -> list[bytes]:
    """Cut into Prisma's exact 1,024-byte frames, padding the last one with silence."""
    raw = pcm.astype("<i2").tobytes()
    raw += bytes(-len(raw) % config.FRAME_BYTES)
    return [raw[i:i + config.FRAME_BYTES] for i in range(0, len(raw), config.FRAME_BYTES)]
