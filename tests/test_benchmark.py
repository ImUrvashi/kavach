"""The benchmark runner, with fake Timbre and fake Prisma (no network, no credits)."""
import asyncio
import io

import numpy as np
import pytest
import soundfile as sf

from app import benchmark, config, demo_audio
from app.benchmark import (all_calls, chart_svg, phone_quality, run_all, run_call,
                           summarize, to_markdown)
from app.demo_audio import RATE
from app.mock_calls import CALLS
from app.unseen_calls import UNSEEN
from app.warnings_text import SCAM_NAMES


def fake_wav(seconds=0.05):
    t = np.arange(int(seconds * 48000)) / 48000
    buf = io.BytesIO()
    sf.write(buf, 0.3 * np.sin(2 * np.pi * 440 * t), 48000, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@pytest.fixture
def fast(monkeypatch):
    for name in ("DEMO_LEAD_S", "DEMO_GAP_S", "DEMO_TAIL_S"):
        monkeypatch.setattr(config, name, 0.02)
    monkeypatch.setattr(benchmark, "SETTLE_S", 0.05)

    async def fake_synth(text, lang, use_clone=True, voice=None):
        return fake_wav()

    monkeypatch.setattr(demo_audio, "synthesize", fake_synth)


def make_fake_prisma(mishear=None):
    """A fake Prisma that 'hears' each scripted line after a few frames.
    `mishear` maps (lang, script) to replacement lines, to simulate misses."""
    class FakePrisma:
        script = None

        def __init__(self, lang):
            self.lang, self.frames, self.closed = lang, 0, False

        async def connect(self):
            pass

        async def send_frame(self, frame):
            self.frames += 1

        async def events(self):
            lines = (mishear or {}).get((self.lang, FakePrisma.script)) or benchmark.call_spec(self.lang, FakePrisma.script)[0]
            for i, line in enumerate(lines):
                while self.frames < (i + 1) * 2 and not self.closed:
                    await asyncio.sleep(0.005)
                if self.closed:
                    return
                yield {"type": "transcript", "text": line, "latency": 120}
            while not self.closed:
                await asyncio.sleep(0.01)

        async def close(self):
            self.closed = True
    return FakePrisma


def test_all_calls_lists_27_in_order():
    calls = all_calls()
    assert len(calls) == 27
    assert calls[0] == ("hi-IN", "scam") and calls[-1] == ("kn-IN", "legit_refund")
    assert all_calls("en-IN", "upi") == [("en-IN", "upi")]


def test_phone_quality_band_limits_and_keeps_length():
    t = np.arange(RATE) / RATE
    low = (8000 * np.sin(2 * np.pi * 100 * t)).astype("<i2")      # 100 Hz: below the phone band
    voice = (8000 * np.sin(2 * np.pi * 1000 * t)).astype("<i2")   # 1 kHz: inside it
    out_low, out_voice = phone_quality(low + voice), phone_quality(voice)
    assert len(out_low) == RATE and out_low.dtype == np.dtype("<i2")
    assert np.abs(out_low - out_voice).mean() < 400               # the 100 Hz tone is gone
    assert np.array_equal(phone_quality(voice), phone_quality(voice))  # same seed, same result


def test_run_call_scores_a_scam(fast):
    Fake = make_fake_prisma()
    Fake.script = "family"
    r = asyncio.run(run_call("hi-IN", "family", session_cls=Fake))
    assert r["kind"] == "scam" and r["warned"] and r["correct"]
    assert r["detected_type"] == "emergency" and r["type_correct"]
    assert r["median_latency_ms"] == 120 and len(r["transcript"]) == 4


def test_run_call_genuine_stays_quiet(fast):
    Fake = make_fake_prisma()
    Fake.script = "legit_refund"
    r = asyncio.run(run_call("hi-IN", "legit_refund", session_cls=Fake))
    assert r["kind"] == "genuine" and not r["warned"] and r["correct"]


def test_summary_markdown_and_chart(fast):
    # Simulate a miss: Prisma garbles the Hinglish job call so no sign is heard.
    garbled = {("en-IN", "job"): ["hello", "theek hai", "okay"]}
    results = []
    for lang, script in [("hi-IN", "upi"), ("en-IN", "job"), ("kn-IN", "legit")]:
        Fake = make_fake_prisma(garbled)
        Fake.script = script
        results.append(asyncio.run(run_call(lang, script, session_cls=Fake)))
    s = summarize(results)
    assert (s["scams"], s["scams_caught"], s["genuine"], s["false_alarms"]) == (2, 1, 1, 0)
    assert s["by_language"]["Hinglish"]["scams_caught"] == 0
    md = to_markdown(results, s, noise=False)
    assert "Kavach warned on 1 of 2 scam calls and 0 of 1 genuine calls" in md and "❌" in md
    svg = chart_svg(results, s)
    assert svg.startswith("<svg") and svg.count("<path") == 3 and "✕" in svg


def test_errors_are_reported_not_crashed(fast, monkeypatch):
    async def no_audio(*a, **k):
        return None
    monkeypatch.setattr(demo_audio, "synthesize", no_audio)
    results = asyncio.run(run_all([("hi-IN", "scam")], session_cls=make_fake_prisma()))
    assert "error" in results[0]
    assert summarize(results)["errors"]


def test_rescore_uses_the_saved_transcript_only(fast):
    Fake = make_fake_prisma()
    Fake.script = "upi"
    r = asyncio.run(run_call("hi-IN", "upi", session_cls=Fake))
    again = benchmark.rescore(r)                       # no Timbre, no Prisma
    assert again["rescored"] and again["max_risk"] == r["max_risk"] and again["warned"] == r["warned"]
    assert again["transcript"][-1]["text"] == r["transcript"][-1]["text"]
    assert benchmark.rescore({"error": "x"}) == {"error": "x"}


def test_held_out_set_is_separate_and_well_formed():
    calls = all_calls(unseen=True)
    assert len(calls) == 15
    assert all(c in UNSEEN for c in calls) and not set(UNSEEN) & set(CALLS)
    scams = [c for c in calls if UNSEEN[c]["expected"]]
    assert len(scams) == 9 and all(UNSEEN[c]["expected"] in SCAM_NAMES for c in scams)
    assert calls[0] == ("hi-IN", "trai_sim") and calls[-1] == ("kn-IN", "ok_branch_kyc")  # scams first
    demo_lines = {line for lines in CALLS.values() for line in lines}
    assert not demo_lines & {line for u in UNSEEN.values() for line in u["lines"]}  # no copied lines


def test_run_call_on_a_held_out_call(fast):
    # Only the plumbing is checked here. Whether Kavach warns on held-out calls
    # is the benchmark's job; asserting it in a test would turn them into tuning data.
    Fake = make_fake_prisma()
    Fake.script = "ok_delivery_otp"
    r = asyncio.run(run_call("en-IN", "ok_delivery_otp", session_cls=Fake))
    assert r["kind"] == "genuine" and r["short"] == "delivery OTP ✓" and r["expected_type"] is None
    assert len(r["transcript"]) == 3
    s = summarize([r])
    assert "held-out" in to_markdown([r], s, noise=False) and "held-out" in chart_svg([r], s)
