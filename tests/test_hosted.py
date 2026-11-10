"""The hosted demo's guard rails: the access code and the call time limit.

With an access code set, nothing may spend Gnani credits without it: live
calls are refused, demo calls fall back to the text demo, and warnings come
only from saved clips. Everything here is offline.
"""
import pytest
from fastapi.testclient import TestClient

from app import config, server


def boom(*a, **k):
    raise AssertionError("must not touch Gnani without the access code")


@pytest.fixture
def hosted(monkeypatch):
    """A keyed server with an access code, where every Gnani path explodes."""
    monkeypatch.setattr(config, "GNANI_API_KEY", "k")
    monkeypatch.setattr(config, "MOCK_MODE", False)
    monkeypatch.setattr(config, "ACCESS_CODE", "open-sesame")
    monkeypatch.setattr(config, "MOCK_LINE_INTERVAL_S", 0.01)
    monkeypatch.setattr(server, "synthesize", boom)
    monkeypatch.setattr(server, "build_demo_call", boom)
    monkeypatch.setattr(server, "GnaniSTTSession", boom)
    clips = []

    async def fake_cached(text, lang, use_clone=True):
        clips.append(text)
        return b"RIFF-saved"

    monkeypatch.setattr(server, "cached_clip", fake_cached)
    return TestClient(server.app), clips


def test_access_code_check(monkeypatch):
    monkeypatch.setattr(config, "MOCK_MODE", False)
    monkeypatch.setattr(config, "ACCESS_CODE", "open-sesame")
    assert server.access_ok("open-sesame") and server.access_ok("  open-sesame ")
    assert not server.access_ok("") and not server.access_ok("open")
    monkeypatch.setattr(config, "ACCESS_CODE", "")
    assert server.access_ok("")  # no code set: open, as when run locally


def test_config_tells_the_page_a_code_is_needed(hosted):
    client, _ = hosted
    assert client.get("/config").json()["access_required"] is True


def test_live_call_without_code_is_refused(hosted):
    client, _ = hosted
    with client.websocket_connect("/ws?demo=0&lang=hi-IN") as ws:
        msg = ws.receive_json()
    assert msg["type"] == "error" and "access code" in msg["message"]


def test_demo_without_code_is_the_text_demo_and_uses_saved_clips_only(hosted):
    client, clips = hosted
    with client.websocket_connect("/ws?demo=1&lang=hi-IN&script=family&code=wrong") as ws:
        msgs = []
        while not any(m["type"] == "warning" for m in msgs):
            msgs.append(ws.receive_json())
        ws.send_json({"type": "stop"})
        while (m := ws.receive_json())["type"] != "summary":
            pass
    ready = next(m for m in msgs if m["type"] == "ready")
    assert ready["mock"] is True and ready["audio_demo"] is False
    assert any(m["type"] == "notice" and "text demo" in m["message"] for m in msgs)
    assert clips  # the warning's audio came from cached_clip, never Timbre


def test_call_ends_at_the_time_limit(monkeypatch):
    monkeypatch.setattr(config, "MAX_CALL_S", 0.3)
    monkeypatch.setattr(config, "MOCK_LINE_INTERVAL_S", 5)  # the call itself would run much longer
    with TestClient(server.app).websocket_connect("/ws?demo=1&lang=hi-IN&script=scam") as ws:
        msgs = []
        while not msgs or msgs[-1]["type"] != "summary":
            msgs.append(ws.receive_json())
    assert any(m["type"] == "notice" and "ends calls after" in m["message"] for m in msgs)


def test_text_demo_ends_by_itself_with_its_report(monkeypatch):
    """No Stop is sent: the scripted call ends after its last line, and the
    report (with both warnings already delivered) still arrives."""
    monkeypatch.setattr(config, "MOCK_LINE_INTERVAL_S", 0.01)

    async def fake_synthesize(text, lang, use_clone=True):
        return b"RIFF-fake"

    monkeypatch.setattr(server, "synthesize", fake_synthesize)
    with TestClient(server.app).websocket_connect("/ws?demo=1&lang=hi-IN&script=scam") as ws:
        msgs = []
        while not msgs or msgs[-1]["type"] != "summary":
            msgs.append(ws.receive_json())
    kinds = [m["type"] for m in msgs]
    assert kinds.count("warning") == 2 and kinds[-1] == "summary"
    assert msgs[-1]["max_risk"] == 100
