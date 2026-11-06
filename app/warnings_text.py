"""What Kavach says out loud. Calm, short, and always ends with a clear action.

Have a native speaker check the Kannada lines before recording the demo.
"""

WARNINGS = {
    "hi": {
        "digital_arrest": "सावधान! पुलिस, सीबीआई या कोई भी सरकारी अधिकारी फ़ोन या वीडियो कॉल पर गिरफ़्तार नहीं करते और पैसे नहीं माँगते। यह धोखा है। अभी फ़ोन काट दीजिए।",
        "credential": "सावधान! कोई भी बैंक या अधिकारी कभी ओटीपी या पिन नहीं माँगता। ओटीपी मत बताइए। अभी फ़ोन काट दीजिए।",
        "remote": "सावधान! किसी अनजान के कहने पर कोई ऐप डाउनलोड मत कीजिए और स्क्रीन शेयर मत कीजिए। यह धोखा है। फ़ोन काट दीजिए।",
        "payment": "सावधान! फ़ोन पर किसी के कहने पर पैसे ट्रांसफर मत कीजिए। पहले घरवालों से बात कीजिए। फ़ोन काट दीजिए।",
        "parcel": "सावधान! पार्सल में ड्रग्स मिलने वाली कॉल एक जाना-माना धोखा है। कोई पैसे मत भेजिए। फ़ोन काट दीजिए।",
        "kyc": "सावधान! केवाईसी या सिम बंद होने की धमकी वाली कॉल धोखा होती है। अपने बैंक को खुद फ़ोन कीजिए। यह कॉल काट दीजिए।",
        "utility": "सावधान! बिजली कटने की धमकी देकर पैसे माँगना धोखा है। बिजली दफ़्तर से खुद बात कीजिए। फ़ोन काट दीजिए।",
        "bait": "सावधान! लॉटरी या गलती से पैसे भेजने की कहानी धोखा है। कोई पैसे मत भेजिए। फ़ोन काट दीजिए।",
        "emergency": "सावधान! घरवाले की मुसीबत के नाम पर पैसे माँगने वाली कॉल अक्सर धोखा होती है। पैसे भेजने से पहले फ़ोन काटिए और उन्हें उनके पुराने नंबर पर खुद फ़ोन कीजिए।",
        "upi_receive": "सावधान! पैसे लेने के लिए कभी क्यूआर स्कैन या यूपीआई पिन नहीं डालना पड़ता। पिन सिर्फ़ पैसे भेजने के लिए होता है। फ़ोन काट दीजिए।",
        "job": "सावधान! घर बैठे कमाई का वादा करके पहले पैसे माँगना धोखा है। असली नौकरी में पैसे नहीं देने पड़ते। फ़ोन काट दीजिए।",
        "investment": "सावधान! पक्के मुनाफ़े या पैसे डबल करने का वादा धोखा है। किसी अनजान के कहने पर पैसे निवेश मत कीजिए। फ़ोन काट दीजिए।",
        "customer_care": "सावधान! असली कस्टमर केयर कभी ऐप डाउनलोड करने या ओटीपी बताने को नहीं कहता। कंपनी के ऑफ़िशियल ऐप से ही संपर्क कीजिए। फ़ोन काट दीजिए।",
        "generic": "सावधान! यह कॉल धोखा लग रही है। कोई पैसे, ओटीपी या जानकारी मत दीजिए। फ़ोन काट दीजिए।",
        "final": "यह पक्का धोखा है। अभी फ़ोन काट दीजिए और घर में किसी से बात कीजिए। ज़रूरत हो तो एक नौ तीन शून्य पर कॉल कीजिए।",
    },
    "kn": {
        "digital_arrest": "ಎಚ್ಚರಿಕೆ! ಪೊಲೀಸ್, ಸಿಬಿಐ ಅಥವಾ ಯಾವುದೇ ಸರ್ಕಾರಿ ಅಧಿಕಾರಿ ಫೋನ್ ಅಥವಾ ವಿಡಿಯೋ ಕಾಲ್‌ನಲ್ಲಿ ಬಂಧಿಸುವುದಿಲ್ಲ, ಹಣ ಕೇಳುವುದಿಲ್ಲ. ಇದು ಮೋಸ. ಈಗಲೇ ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "credential": "ಎಚ್ಚರಿಕೆ! ಯಾವುದೇ ಬ್ಯಾಂಕ್ ಅಥವಾ ಅಧಿಕಾರಿ ಒಟಿಪಿ ಅಥವಾ ಪಿನ್ ಕೇಳುವುದಿಲ್ಲ. ಒಟಿಪಿ ಹೇಳಬೇಡಿ. ಈಗಲೇ ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "remote": "ಎಚ್ಚರಿಕೆ! ಅಪರಿಚಿತರು ಹೇಳಿದರೆಂದು ಯಾವುದೇ ಆ್ಯಪ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಬೇಡಿ, ಸ್ಕ್ರೀನ್ ಶೇರ್ ಮಾಡಬೇಡಿ. ಇದು ಮೋಸ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "payment": "ಎಚ್ಚರಿಕೆ! ಫೋನ್‌ನಲ್ಲಿ ಯಾರೋ ಹೇಳಿದರೆಂದು ಹಣ ವರ್ಗಾಯಿಸಬೇಡಿ. ಮೊದಲು ಮನೆಯವರ ಜೊತೆ ಮಾತನಾಡಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "parcel": "ಎಚ್ಚರಿಕೆ! ಪಾರ್ಸೆಲ್‌ನಲ್ಲಿ ಡ್ರಗ್ಸ್ ಸಿಕ್ಕಿದೆ ಎಂಬ ಕರೆ ಒಂದು ಸಾಮಾನ್ಯ ಮೋಸ. ಹಣ ಕಳುಹಿಸಬೇಡಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "kyc": "ಎಚ್ಚರಿಕೆ! ಕೆವೈಸಿ ಅಥವಾ ಸಿಮ್ ಬ್ಲಾಕ್ ಆಗುತ್ತದೆ ಎಂಬ ಬೆದರಿಕೆ ಕರೆ ಮೋಸ. ನಿಮ್ಮ ಬ್ಯಾಂಕಿಗೆ ನೀವೇ ಕರೆ ಮಾಡಿ. ಈ ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "utility": "ಎಚ್ಚರಿಕೆ! ಕರೆಂಟ್ ಕಟ್ ಮಾಡುತ್ತೇವೆ ಎಂದು ಹಣ ಕೇಳುವುದು ಮೋಸ. ವಿದ್ಯುತ್ ಕಚೇರಿಗೆ ನೀವೇ ಕರೆ ಮಾಡಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "bait": "ಎಚ್ಚರಿಕೆ! ಲಾಟರಿ ಅಥವಾ ತಪ್ಪಾಗಿ ಹಣ ಕಳುಹಿಸಿದೆ ಎಂಬ ಕಥೆ ಮೋಸ. ಹಣ ಕಳುಹಿಸಬೇಡಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "emergency": "ಎಚ್ಚರಿಕೆ! ಮನೆಯವರು ತೊಂದರೆಯಲ್ಲಿದ್ದಾರೆ ಎಂದು ಹಣ ಕೇಳುವ ಕರೆ ಹೆಚ್ಚಾಗಿ ಮೋಸ. ಹಣ ಕಳುಹಿಸುವ ಮೊದಲು ಕರೆ ಕಟ್ ಮಾಡಿ, ಅವರ ಹಳೆಯ ನಂಬರ್‌ಗೆ ನೀವೇ ಕರೆ ಮಾಡಿ.",
        "upi_receive": "ಎಚ್ಚರಿಕೆ! ಹಣ ಪಡೆಯಲು ಕ್ಯೂಆರ್ ಸ್ಕ್ಯಾನ್ ಮಾಡುವ ಅಥವಾ ಯುಪಿಐ ಪಿನ್ ಹಾಕುವ ಅಗತ್ಯವಿಲ್ಲ. ಪಿನ್ ಹಣ ಕಳುಹಿಸಲು ಮಾತ್ರ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "job": "ಎಚ್ಚರಿಕೆ! ಮನೆಯಲ್ಲೇ ಸಂಪಾದನೆಯ ಆಸೆ ತೋರಿಸಿ ಮೊದಲು ಹಣ ಕೇಳುವುದು ಮೋಸ. ನಿಜವಾದ ಕೆಲಸಕ್ಕೆ ಹಣ ಕೊಡಬೇಕಿಲ್ಲ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "investment": "ಎಚ್ಚರಿಕೆ! ಖಚಿತ ಲಾಭ ಅಥವಾ ಹಣ ಡಬಲ್ ಮಾಡುವ ಭರವಸೆ ಮೋಸ. ಅಪರಿಚಿತರು ಹೇಳಿದರೆಂದು ಹಣ ಹೂಡಬೇಡಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "customer_care": "ಎಚ್ಚರಿಕೆ! ನಿಜವಾದ ಕಸ್ಟಮರ್ ಕೇರ್ ಆ್ಯಪ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಲು ಅಥವಾ ಒಟಿಪಿ ಹೇಳಲು ಕೇಳುವುದಿಲ್ಲ. ಕಂಪನಿಯ ಅಧಿಕೃತ ಆ್ಯಪ್ ಮೂಲಕವೇ ಸಂಪರ್ಕಿಸಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "generic": "ಎಚ್ಚರಿಕೆ! ಈ ಕರೆ ಮೋಸದಂತೆ ಕಾಣುತ್ತಿದೆ. ಹಣ, ಒಟಿಪಿ ಅಥವಾ ಮಾಹಿತಿ ಕೊಡಬೇಡಿ. ಕರೆ ಕಟ್ ಮಾಡಿ.",
        "final": "ಇದು ಖಂಡಿತ ಮೋಸ. ಈಗಲೇ ಕರೆ ಕಟ್ ಮಾಡಿ, ಮನೆಯವರ ಜೊತೆ ಮಾತನಾಡಿ. ಅಗತ್ಯವಿದ್ದರೆ ಒಂದು ಒಂಬತ್ತು ಮೂರು ಸೊನ್ನೆಗೆ ಕರೆ ಮಾಡಿ.",
    },
}

# Short English names for each kind of scam, shown on screen and in the summary.
SCAM_NAMES = {
    "digital_arrest": "Fake police / digital arrest scam",
    "credential": "OTP or PIN theft",
    "remote": "Remote-access app scam",
    "payment": "Money-transfer scam",
    "parcel": "Courier / parcel scam",
    "kyc": "KYC or SIM-block scam",
    "utility": "Electricity bill scam",
    "bait": "Lottery or 'sent by mistake' scam",
    "emergency": "Family emergency scam",
    "upi_receive": "UPI QR / PIN scam",
    "job": "Job or task scam",
    "investment": "Investment or trading scam",
    "customer_care": "Fake customer care scam",
    "generic": "Possible scam",
}

# The UI shows the helpline as digits; the spoken text spells it out so TTS reads it clearly.
DISPLAY_FIXES = {"एक नौ तीन शून्य": "1930", "ಒಂದು ಒಂಬತ್ತು ಮೂರು ಸೊನ್ನೆ": "1930"}


def warning_lang(stt_lang: str) -> str:
    """Hinglish (en-IN) speakers get the warning in Hindi."""
    return "kn" if stt_lang.startswith("kn") else "hi"


def warning_for(stt_lang: str, scam_type: str, final: bool = False) -> tuple[str, str, str]:
    """Returns (lang, spoken_text, display_text)."""
    lang = warning_lang(stt_lang)
    table = WARNINGS[lang]
    spoken = table["final"] if final else table.get(scam_type, table["generic"])
    display = spoken
    for k, v in DISPLAY_FIXES.items():
        display = display.replace(k, v)
    return lang, spoken, display


def warnings_to_speak(prev_level: int, new_level: int) -> list[bool]:
    """Which warnings to speak when the level rises from prev_level to new_level.

    Returns a list of `final` flags in the order they should play:
    crossing level 2 (warn) adds the tailored warning (False), crossing
    level 3 (alert) adds the firm "hang up, call 1930" warning (True).
    A single sentence that jumps from safe straight to alert gets both,
    tailored first, so the listener hears why and then what to do.
    """
    out = []
    if prev_level < 2 <= new_level:
        out.append(False)
    if prev_level < 3 <= new_level:
        out.append(True)
    return out


def all_warnings():
    for lang, table in WARNINGS.items():
        for key, text in table.items():
            yield lang, key, text
