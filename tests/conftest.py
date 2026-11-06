"""Shared test setup.

Tests must never call Gnani (no network, no credits), even when a real key is
in .env. So every test runs as if there were no key: demo calls are
text-only and Timbre is never contacted. A test that needs the keyed path
(the audio demo) turns it back on itself and fakes Timbre and Prisma.
"""
import pytest

from app import config


@pytest.fixture(autouse=True)
def no_gnani(monkeypatch):
    monkeypatch.setattr(config, "GNANI_API_KEY", "")
    monkeypatch.setattr(config, "MOCK_MODE", True)
