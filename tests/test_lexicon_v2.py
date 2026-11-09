"""Checks for lexicon v2 (Nov 9): the story + pressure + request "scam shape",
the wider English vocabulary, and the innocent phrases it must not flag.

All sentences here were written for these tests. None is copied from
ICFD-31k or from the blind held-out calls."""
import pytest

from app.detector import ScamDetector
from app.lexicon import PRESSURE, REQUEST, SHAPE_BONUS, SIGNALS, STORY


def run(lines):
    d = ScamDetector()
    for i, line in enumerate(lines):
        d.update(line, t=i * 5.0)
    return d


def cats(text):
    d = ScamDetector()
    d.update(text, 0)
    return set(d.seen)


def test_groups_cover_every_signal_once():
    names = {s.category for s in SIGNALS}
    assert STORY | PRESSURE | REQUEST == names
    assert not (STORY & PRESSURE) and not (STORY & REQUEST) and not (PRESSURE & REQUEST)


def test_shape_bonus_needs_a_request():
    story_and_pressure = run(["Sir, this is the electricity department.", "Do it urgently."])
    request_with_story = run(["Sir, this is the electricity department.", "Please pay the processing fee."])
    assert story_and_pressure.risk < 70
    assert request_with_story.risk >= 70
    assert request_with_story.risk - story_and_pressure.risk >= SHAPE_BONUS["request+story"]


@pytest.mark.parametrize("text, category", [
    ("Please share your card number and CVV for verification.", "credential"),
    ("Just read out the code that you received on SMS.", "credential"),
    ("Enter your net banking credentials on the page.", "credential"),
    ("Install AnyDesk so our engineer can access your computer.", "remote"),
    ("I will send you a link, log in through the link.", "remote"),
    ("Pay the amount to my wallet ID, it is faster.", "personal_account"),
    ("Your laptop has been infected with a virus.", "tech_support"),
    ("Your loan of two lakh is pre-approved.", "loan"),
    ("Your insurance policy bonus is pending.", "insurance"),
    ("Otherwise I will share these photos with your family.", "threat"),
    ("Keep this confidential, it is between us.", "secrecy"),
    ("This offer is for a limited time, act fast.", "urgency"),
    ("Congratulations, you have won a free holiday voucher.", "bait"),
    ("You need to pay a small registration fee.", "payment"),
])
def test_v2_english_vocabulary(text, category):
    assert category in cats(text)


@pytest.mark.parametrize("text", [
    "Main QR code bhej raha hoon, scan karke payment kar dena.",   # QR code is not a secret code
    "Hospital registration ke liye Aadhaar card number bata dijiye.",
    "Beta, ghar ka wifi password bata do.",
    "Aapke area ka pin code bataiye.",
    "Sir, parcel check karke delivery OTP bata dijiye.",            # a delivery OTP at the door
])
def test_innocent_requests_are_not_credentials(text):
    assert "credential" not in cats(text)


def test_tech_support_scam_warns():
    d = run(["Hello, this is Microsoft technical support.",
             "Your computer has been hacked and is sending viruses.",
             "Please download this software so we can access your computer and fix it."])
    assert d.level >= 2 and d.scam_type() == "remote"


def test_fee_to_a_personal_wallet_warns():
    d = run(["Sir, your loan is approved.", "Pay the processing fee to my Paytm wallet ID today."])
    assert d.level >= 2


def test_genuine_fraud_alert_stays_quiet():
    d = run(["This is your bank's fraud team. We saw a suspicious transaction on your card.",
             "Did you make it? If not, we will block the card and send a new one.",
             "We will never ask for your OTP or PIN."])
    assert d.level < 2
