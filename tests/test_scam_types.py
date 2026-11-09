"""Checks for the five scam types added on Nov 6, the "Ask the caller" card,
and that every kind of scam has a warning, a name and questions."""
import pytest

from app.ask_caller import ASK, QUESTIONS, ask_for
from app.detector import ScamDetector
from app.mock_calls import CALLS, EXPECTED_TYPE, LEGIT_SCRIPTS, SCAM_SCRIPTS
from app.warnings_text import SCAM_NAMES, WARNINGS

LANGS = ["hi-IN", "en-IN", "kn-IN"]


def run(lines):
    d = ScamDetector()
    for i, line in enumerate(lines):
        d.update(line, t=i * 5.0)
    return d


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("script", SCAM_SCRIPTS)
def test_every_scam_script_is_caught_and_named(lang, script):
    d = run(CALLS[(lang, script)])
    assert d.level >= 2, d.summary(30)
    assert d.scam_type() == EXPECTED_TYPE[script]


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("script", LEGIT_SCRIPTS)
def test_genuine_look_alikes_stay_quiet(lang, script):
    d = run(CALLS[(lang, script)])
    assert d.max_risk < 40, d.summary(30)
    assert d.level == 0


@pytest.mark.parametrize("text,category", [
    ("Papa ko mat batana", "secrecy"),                     # secrecy now covers any "X ko mat batana"
    ("पापा को मत बताना", "secrecy"),
    ("ಅಮ್ಮನಿಗೆ ಹೇಳಬೇಡಿ", "secrecy"),
    ("Beta ka accident ho gaya, hospital mein hai", "emergency"),
    ("QR scan kijiye, paise aa jayenge", "upi_receive"),
    ("Part time job hai, ghar baithe kamaiye", "job"),
    ("Guaranteed 30 percent return milega", "investment"),
    ("Main customer care se bol raha hoon", "customer_care"),
    ("pehle das hazaar rupaye invest kijiye", "payment"),
])
def test_new_patterns(text, category):
    r = ScamDetector().update(text, 0)
    assert category in {m.category for m in r.matches}


def test_hindi_customer_is_not_customs():
    # "कस्टम" (customs) used to match inside "कस्टमर" (customer).
    r = ScamDetector().update("मैं अमेज़न कस्टमर केयर से बोल रही हूँ", 0)
    assert "authority" not in {m.category for m in r.matches}
    r = ScamDetector().update("कस्टम विभाग से बोल रहा हूँ", 0)
    assert "authority" in {m.category for m in r.matches}


def test_son_arrested_is_a_family_emergency_not_digital_arrest():
    d = run(["Papa, police ne mujhe pakad liya hai, jail mein daal denge", "jaldi paise bhej do"])
    assert d.scam_type() == "emergency"


def test_safety_advice_still_cancels_secrecy():
    r = ScamDetector().update("बैंक कभी भी ओटीपी नहीं मांगता, ओटीपी किसी को मत बताइए।", 0)
    assert r.risk == 0


SCAM_KINDS = set(WARNINGS["hi"]) - {"final"}


def test_every_scam_kind_has_warnings_names_and_questions():
    assert set(WARNINGS["kn"]) == set(WARNINGS["hi"])
    assert SCAM_KINDS == set(SCAM_NAMES) == set(ASK)
    for qs in ASK.values():
        assert 2 <= len(qs) <= 3 and all(q in QUESTIONS for q in qs)
    for q in QUESTIONS.values():
        assert q["en"] and q["hi"] and q["kn"]


@pytest.mark.parametrize("lang,expect_script", [("hi-IN", "पिन"), ("en-IN", "पिन"), ("kn-IN", "ಪಿನ್")])
def test_ask_for_uses_the_warning_language(lang, expect_script):
    items = ask_for(lang, "upi_receive")
    assert len(items) == 2
    assert expect_script in items[0]["text"]
    assert items[0]["en"].startswith("Why do I need to pay")


# ---- Tuned to the live Hindi UPI test on Nov 6 ----
# Exactly what Prisma wrote when the scripted UPI scam was read aloud. Prisma
# dropped "स्कैन करके अपना यूपीआई" and wrote "आ जाए" instead of "आ जाएँगे",
# so Kavach stopped at risk 45 and never warned.
LIVE_HI_UPI = [
    "का ओ एल एक्स पे डाला हुआ तोफा खरीद",
    "मैं आपको अडवांस पेमेंट के लिए क्यूआर कोड भेज रहा हूँ",
    "क्यूआर पिन डालिए पैसे तुरंत आपके अकाउन्ट में आ जाए",
    "ओके",
    "ठीक है",
]


def test_live_hindi_upi_transcript_now_warns():
    d = ScamDetector()
    risks = [d.update(line, i).risk for i, line in enumerate(LIVE_HI_UPI)]
    assert risks[2] >= 85            # warns, and gives the final warning, at the QR + PIN sentence
    assert d.scam_type() == "upi_receive"


@pytest.mark.parametrize("text", [
    "QR pin daaliye, paise aa jaye",
    "Advance payment ke liye QR code bhej raha hoon, PIN daal dijiye",
    "ಕ್ಯೂಆರ್ ಪಿನ್ ಹಾಕಿ, ಹಣ ಬರುತ್ತೆ",
])
def test_qr_and_pin_together_is_a_upi_scam(text):
    r = ScamDetector().update(text, 0)
    assert {"upi_receive", "credential"} <= {m.category for m in r.matches}
    assert r.level >= 2


@pytest.mark.parametrize("text", [
    "दुकान पर पेमेंट के लिए क्यूआर स्कैन कर लीजिए",   # a shop asking you to pay by QR
    "Payment ke liye QR scan kar lijiye",
    "ಪೇಮೆಂಟ್‌ಗೆ ಕ್ಯೂಆರ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ",
])
def test_paying_a_shop_by_qr_does_not_warn(text):
    r = ScamDetector().update(text, 0)
    assert r.risk < 40 and r.level == 0


def test_prisma_spelling_of_account():
    r = ScamDetector().update("सारे पैसे सेफ अकाउन्ट में डाल दीजिए", 0)
    assert "payment" in {m.category for m in r.matches}


def test_prisma_spelling_of_upi_with_spaces():
    # From the real audio demo: "क्यूआर स्कैन करके अपना यू पी आई पिन डालिये…"
    r = ScamDetector().update("क्यूआर स्कैन करके अपना यू पी आई पिन डालिये, पैसे तुरंत आपके खाते में आ जाएंगे।", 0)
    assert {"payment", "upi_receive", "credential"} <= {m.category for m in r.matches}


# ---- Tuned to the Kannada audio demo on Nov 6 (what Prisma actually wrote) ----
@pytest.mark.parametrize("text,category", [
    ("ವಿಡಿಯೋ ಕಾಲ್ ನಲ್ಲೇ ಇರಿ", "secrecy"),          # Prisma put a space in ಕಾಲ್ನಲ್ಲೇ
    ("ಯಾರಿಗೂ ಹೇಳ್ಬೇಡಿ", "secrecy"),               # spoken short form of ಹೇಳಬೇಡಿ
    ("ನಿಮ್ಮ ಹಣವನ್ನು ಆರ್ ಬೈ ಸೇಫ್ ಅಕೌಂಟ್ ಗೆ ವರ್ಗಾಯಿಸಿ", "authority"),  # RBI misheard
])
def test_prisma_kannada_spellings(text, category):
    assert category in {m.category for m in ScamDetector().update(text, 0).matches}


# ---- Tuned to the full benchmark on Nov 6 (what Prisma actually wrote) ----
@pytest.mark.parametrize("text,category", [
    ("qr scan karke apna upi pin daliye paise turant aapke account mein aa jaayenge", "credential"),  # "daliye"
    ("ಈ ಟ್ರೇಡಿಂಗ್ ಆಲ್ ಆ್ಯಪ್ ಡೌನ್ ಲೋಡ್ ಮಾಡಿ", "remote"),    # Prisma split ಡೌನ್ ಲೋಡ್
    ("ಎಪಿಕೆ ಇನ್ ಸ್ಟಾಲ್ ಮಾಡಿ", "remote"),
])
def test_prisma_benchmark_spellings(text, category):
    assert category in {m.category for m in ScamDetector().update(text, 0).matches}
