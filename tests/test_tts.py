"""Timbre requests go one at a time and retry when Timbre says it's busy.
httpx is faked, so nothing reaches Gnani."""
import asyncio

from app import config, tts


class FakeResponse:
    def __init__(self, status, content=b"RIFF-fake"):
        self.status_code, self.content, self.text = status, content, "busy" if status == 429 else ""


def test_requests_are_queued_and_429_is_retried(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "GNANI_API_KEY", "test-key")
    monkeypatch.setattr(config, "TTS_CACHE_DIR", tmp_path)
    monkeypatch.setattr(tts, "RETRY_WAIT_S", 0.01)
    state = {"active": 0, "max_active": 0, "calls": 0}

    class FakeClient:
        def __init__(self, timeout):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, json, headers):
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
            state["calls"] += 1
            await asyncio.sleep(0.01)
            state["active"] -= 1
            return FakeResponse(429 if state["calls"] == 1 else 200)   # busy once, then fine

    monkeypatch.setattr(tts.httpx, "AsyncClient", FakeClient)

    async def three_at_once():
        return await asyncio.gather(*(tts.synthesize(f"line {i}", "hi", use_clone=False) for i in range(3)))

    clips = asyncio.run(three_at_once())
    assert all(c == b"RIFF-fake" for c in clips)     # all three succeed
    assert state["max_active"] == 1                  # never two requests at once
    assert state["calls"] == 4                       # one 429, retried
