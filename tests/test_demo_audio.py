"""Audible demo calls: building the recording, and the server streaming it
through Prisma. Timbre and Prisma are faked, so no network and no credits."""
import asyncio
import io

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from app import config, demo_audio, server
from app.demo_audio import RATE, build_demo_call, to_frames, wav_to_pcm16k
from app.mock_calls import get_call


def fake_wav(seconds=0.1, rate=48000):
    t = np.arange(int(seconds * rate)) / rate
    buf = io.BytesIO()
    sf.write(buf, 0.3 * np.sin(2 * np.pi * 440 * t), rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def test_wav_is_converted_to_16k_mono():
    pcm = wav_to_pcm16k(fake_wav(0.5, 48000))
    assert pcm.dtype == np.dtype("<i2")
    assert abs(len(pcm) - 8000) <= 1


def test_frames_are_exactly_1024_bytes():
    frames = to_frames(np.zeros(1000, dtype="<i2"))   # 2,000 bytes → 2 frames, last one padded
    assert len(frames) == 2 and all(len(f) == config.FRAME_BYTES for f in frames)


@pytest.fixture
def quick_timing(monkeypatch):
    monkeypatch.setattr(config, "DEMO_LEAD_S", 0.1)
    monkeypatch.setattr(config, "DEMO_GAP_S", 0.1)
    monkeypatch.setattr(config, "DEMO_TAIL_S", 0.1)


def test_demo_call_is_lines_joined_with_pauses(monkeypatch, quick_timing):
    calls = []

    async def fake_synth(text, lang, use_clone=True, voice=None):
        calls.append((lang, use_clone))
        return fake_wav(0.2)

    monkeypatch.setattr(demo_audio, "synthesize", fake_synth)
    pcm = asyncio.run(build_demo_call("hi-IN", "scam"))
    n = len(get_call("hi-IN", "scam"))
    assert len(pcm) == int(0.1 * RATE) + n * (int(0.2 * RATE) + int(0.1 * RATE)) + int(0.1 * RATE)
    assert all(c == ("hi", False) for c in calls)    # Hindi voice, never the cloned family voice


def test_hinglish_falls_back_to_the_hindi_voice(monkeypatch, quick_timing):
    async def fake_synth(text, lang, use_clone=True, voice=None):
        return None if lang == "en" else fake_wav(0.1)

    monkeypatch.setattr(demo_audio, "synthesize", fake_synth)
    assert asyncio.run(build_demo_call("en-IN", "scam")) is not None


def test_demo_call_fails_cleanly_without_audio(monkeypatch, quick_timing):
    async def no_audio(*a, **k):
        return None

    monkeypatch.setattr(demo_audio, "synthesize", no_audio)
    assert asyncio.run(build_demo_call("hi-IN", "scam")) is None


class FakePrisma:
    """Stands in for Gnani Prisma: counts the frames it is sent and 'hears'
    one scripted line for every few frames received."""
    last = None

    def __init__(self, lang):
        self.lang, self.frames, self.closed = lang, 0, False
        FakePrisma.last = self

    async def connect(self):
        pass

    async def send_frame(self, frame):
        assert len(frame) == config.FRAME_BYTES
        self.frames += 1

    async def events(self):
        for i, line in enumerate(get_call(self.lang, "scam")):
            while self.frames < (i + 1) * 3 and not self.closed:
                await asyncio.sleep(0.01)
            if self.closed:
                return
            yield {"type": "transcript", "text": line, "latency": 100}
        while not self.closed:
            await asyncio.sleep(0.05)

    async def close(self):
        self.closed = True


def test_audio_demo_streams_through_prisma_and_ends_by_itself(monkeypatch, quick_timing):
    monkeypatch.setattr(config, "MOCK_MODE", False)
    monkeypatch.setattr(server, "GnaniSTTSession", FakePrisma)

    async def fake_synth(text, lang, use_clone=True, voice=None):
        return fake_wav(0.1)

    monkeypatch.setattr(demo_audio, "synthesize", fake_synth)   # the caller's lines
    monkeypatch.setattr(server, "synthesize", fake_synth)       # Kavach's warnings

    seen = []
    with TestClient(server.app).websocket_connect("/ws?lang=hi-IN&script=scam&demo=1") as ws:
        while True:                       # no "stop" is sent: the call must end on its own
            msg = ws.receive_json()
            seen.append(msg)
            if msg["type"] == "summary":
                break

    types = [m["type"] for m in seen]
    assert types[0] == "preparing"
    ready = next(m for m in seen if m["type"] == "ready")
    assert ready["audio_demo"] is True and ready["mock"] is False
    assert "demo_audio" in types and "transcript" in types and "warning" in types
    pcm = asyncio.run(build_demo_call("hi-IN", "scam"))
    assert FakePrisma.last.frames == len(to_frames(pcm))     # the whole recording reached "Prisma"
    assert seen[-1]["scam_name"] == "Fake police / digital arrest scam"
