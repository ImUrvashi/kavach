import pytest

from app.detector import ScamDetector
from app.mock_calls import CALLS
from app.warnings_text import warning_for


def run(lines):
    d = ScamDetector()
    for i, line in enumerate(lines):
        d.update(line, t=i * 5.0)
    return d


@pytest.mark.parametrize("lang", ["hi-IN", "en-IN", "kn-IN"])
def test_scam_calls_reach_warning(lang):
    d = run(CALLS[(lang, "scam")])
    assert d.max_risk >= 70, d.summary(30)
    assert d.level >= 2
    assert d.scam_type() == "digital_arrest"


@pytest.mark.parametrize("lang", ["hi-IN", "en-IN", "kn-IN"])
def test_legit_calls_stay_quiet(lang):
    d = run(CALLS[(lang, "legit")])
    assert d.max_risk < 40, d.summary(30)
    assert d.level == 0


def test_protective_advice_is_not_a_credential_request():
    d = ScamDetector()
    r = d.update("बैंक कभी भी ओटीपी नहीं मांगता, ओटीपी किसी को मत बताइए।", 0)
    cats = {m.category for m in r.matches}
    assert "credential" not in cats and "secrecy" not in cats
    assert "protective" in cats
    assert r.risk == 0


def test_credential_request_hinglish():
    d = ScamDetector()
    r = d.update("Sir apna OTP bata dijiye, verification ke liye", 0)
    assert "credential" in {m.category for m in r.matches}


@pytest.mark.parametrize("text,category", [
    # Live Prisma (en-IN) writes Hinglish "pe" as "pay", as in
    # "aapke naam pay fedex parcel receive hua hai" (live test, Nov 6).
    ("video call pay rahiye, kisi ko mat bataiye", "secrecy"),
    ("video call pe rahiye", "secrecy"),
    ("video call per rahiye", "secrecy"),
    ("is link pay click kijiye", "remote"),
    ("is link par click karo", "remote"),
])
def test_hinglish_pe_spellings(text, category):
    r = ScamDetector().update(text, 0)
    assert category in {m.category for m in r.matches}


def test_live_prisma_hinglish_parcel_line():
    # Exact transcript from the first live test.
    d = ScamDetector()
    d.update("this is inspector rathore from crime branch", 0)
    r = d.update("aapke naam pay fedex parcel receive hua hai and we have found drugs in it", 5)
    assert r.risk == 75 and r.level == 2


def test_level_never_drops_within_call():
    d = run(CALLS[("hi-IN", "scam")])
    level = d.level
    d.update("बैंक कभी भी ओटीपी नहीं मांगता", 99)
    assert d.level == level


def test_match_offsets_point_at_original_text():
    d = ScamDetector()
    text = "Aapka FedEx Parcel seize hua hai"
    r = d.update(text, 0)
    for m in r.matches:
        assert text[m.start:m.end] == m.text


def test_warning_text_and_display():
    lang, spoken, display = warning_for("en-IN", "digital_arrest")
    assert lang == "hi" and spoken == display
    _, spoken, display = warning_for("kn-IN", "x", final=True)
    assert "1930" in display and "1930" not in spoken
