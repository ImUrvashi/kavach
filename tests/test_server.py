"""End-to-end checks of the warning flow through the /ws socket in demo mode.

Timbre is replaced by a fake so these tests never call Gnani or spend credits,
even when a real key is in .env.
"""
import asyncio

import pytest
from fastapi.testclient import TestClient

from app import config, mock_calls, server
from app.warnings_text import WARNINGS, warnings_to_speak

JUMP_LINE = "Main CBI se bol raha hoon, aapke naam pe arrest warrant hai, paise safe account mein transfer kijiye"


@pytest.mark.parametrize("prev,new,expected", [
    (0, 1, []),
    (0, 2, [False]),
    (1, 2, [False]),
    (2, 3, [True]),
    (0, 3, [False, True]),  # one sentence jumps straight to alert: both, tailored first
    (1, 3, [False, True]),
    (3, 3, []),
])
def test_warnings_to_speak(prev, new, expected):
    assert warnings_to_speak(prev, new) == expected


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(config, "MOCK_LINE_INTERVAL_S", 0.01)
    monkeypatch.setitem(mock_calls.CALLS, ("en-IN", "jump"), [JUMP_LINE])
    finals = {table["final"] for table in WARNINGS.values()}

    async def fake_synthesize(text, lang, use_clone=True):
        # Make the tailored clip slow (as if not cached) so a fast final clip
        # would overtake it if warnings were not serialised.
        await asyncio.sleep(0 if text in finals else 0.3)
        return b"RIFF-fake"

    monkeypatch.setattr(server, "synthesize", fake_synthesize)
    return TestClient(server.app)


def collect_warnings(client, query, n):
    warnings, transcripts = [], []
    with client.websocket_connect(f"/ws?demo=1&{query}") as ws:
        while len(warnings) < n:
            msg = ws.receive_json()
            if msg["type"] == "warning":
                warnings.append(msg)
            elif msg["type"] == "transcript":
                transcripts.append(msg)
        ws.send_json({"type": "stop"})
        while (msg := ws.receive_json())["type"] != "summary":
            pass
    return warnings, transcripts


def test_jump_straight_to_alert_speaks_both_warnings_in_order(client):
    warnings, transcripts = collect_warnings(client, "lang=en-IN&script=jump", 2)
    assert len(transcripts) == 1 and transcripts[0]["level"] == 3
    assert [w["final"] for w in warnings] == [False, True]
    assert "1930" in warnings[1]["text"]


def test_gradual_scam_call_speaks_tailored_then_final(client):
    warnings, _ = collect_warnings(client, "lang=hi-IN&script=scam", 2)
    assert [w["final"] for w in warnings] == [False, True]
    assert warnings[0]["scam_type"] == "digital_arrest"


def test_warning_carries_scam_name_and_questions(client):
    warnings, _ = collect_warnings(client, "lang=hi-IN&script=family", 1)
    w = warnings[0]
    assert w["scam_type"] == "emergency"
    assert w["scam_name"] == "Family emergency scam"
    assert len(w["ask"]) == 2 and w["ask"][0]["en"] == "Tell me something only you would know."


def test_config_lists_the_scams_for_the_start_screen(client):
    scams = client.get("/config").json()["scams"]
    assert len(scams) == 13 and "Family emergency scam" in scams and "Possible scam" not in scams
