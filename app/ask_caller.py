""""Ask the caller": questions the listener can say to test a suspicious call.

When Kavach warns, the screen also shows two or three questions for that kind
of scam. A genuine caller agrees to all of them (call back on the official
number, send it in writing, meet in person). A scammer refuses, gets angry or
adds pressure, which makes the scam obvious to the listener.

Questions are shown in the warning's language (Hindi or Kannada) with the
English underneath. Have a native speaker check the Kannada lines.
"""
from .warnings_text import warning_lang

QUESTIONS = {
    "name_id": {
        "en": "What is your full name, ID number and office address?",
        "hi": "आपका पूरा नाम, आईडी नंबर और दफ़्तर का पता क्या है?",
        "kn": "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು, ಐಡಿ ನಂಬರ್ ಮತ್ತು ಕಚೇರಿ ವಿಳಾಸ ಏನು?",
    },
    "callback": {
        "en": "I will call your office back on its official number.",
        "hi": "मैं आपके दफ़्तर के ऑफ़िशियल नंबर पर खुद फ़ोन करूँगा।",
        "kn": "ನಿಮ್ಮ ಕಚೇರಿಯ ಅಧಿಕೃತ ನಂಬರ್‌ಗೆ ನಾನೇ ಕರೆ ಮಾಡುತ್ತೇನೆ.",
    },
    "in_person": {
        "en": "I will come to the police station or branch in person.",
        "hi": "मैं खुद थाने या ब्रांच आकर मिलूँगा।",
        "kn": "ನಾನೇ ಠಾಣೆಗೆ ಅಥವಾ ಬ್ರಾಂಚ್‌ಗೆ ಬಂದು ಭೇಟಿಯಾಗುತ್ತೇನೆ.",
    },
    "in_writing": {
        "en": "Send me this in writing, by post or official email.",
        "hi": "यह लिखित में, डाक या ऑफ़िशियल ईमेल से भेजिए।",
        "kn": "ಇದನ್ನು ಅಂಚೆ ಅಥವಾ ಅಧಿಕೃತ ಇಮೇಲ್ ಮೂಲಕ ಬರವಣಿಗೆಯಲ್ಲಿ ಕಳುಹಿಸಿ.",
    },
    "family_first": {
        "en": "Let me talk to my family first. I will call you back.",
        "hi": "पहले मैं घरवालों से बात करूँगा, फिर आपको फ़ोन करूँगा।",
        "kn": "ಮೊದಲು ಮನೆಯವರ ಜೊತೆ ಮಾತನಾಡಿ, ನಿಮಗೆ ಮತ್ತೆ ಕರೆ ಮಾಡುತ್ತೇನೆ.",
    },
    "secret_question": {
        "en": "Tell me something only you would know.",
        "hi": "कोई ऐसी बात बताओ जो सिर्फ़ तुम्हें पता हो।",
        "kn": "ನಿನಗೆ ಮಾತ್ರ ಗೊತ್ತಿರುವ ಒಂದು ವಿಷಯ ಹೇಳು.",
    },
    "call_usual_number": {
        "en": "I will call you back on your usual number.",
        "hi": "मैं तुम्हारे पुराने नंबर पर वापस फ़ोन करता हूँ।",
        "kn": "ನಿನ್ನ ಹಳೆಯ ನಂಬರ್‌ಗೆ ನಾನೇ ಮತ್ತೆ ಕರೆ ಮಾಡುತ್ತೇನೆ.",
    },
    "why_pay_to_receive": {
        "en": "Why do I need to pay or enter a PIN to receive money?",
        "hi": "पैसे लेने के लिए मुझे पैसे या पिन क्यों देना पड़ेगा?",
        "kn": "ಹಣ ಪಡೆಯಲು ನಾನು ಯಾಕೆ ಹಣ ಅಥವಾ ಪಿನ್ ಕೊಡಬೇಕು?",
    },
    "company_details": {
        "en": "What is the company's registered name and website? I will check it myself.",
        "hi": "कंपनी का रजिस्टर्ड नाम और वेबसाइट बताइए, मैं खुद जाँच करूँगा।",
        "kn": "ಕಂಪನಿಯ ನೋಂದಾಯಿತ ಹೆಸರು ಮತ್ತು ವೆಬ್‌ಸೈಟ್ ಹೇಳಿ, ನಾನೇ ಪರಿಶೀಲಿಸುತ್ತೇನೆ.",
    },
    "sebi_number": {
        "en": "What is your SEBI registration number?",
        "hi": "आपका सेबी रजिस्ट्रेशन नंबर क्या है?",
        "kn": "ನಿಮ್ಮ ಸೆಬಿ ನೋಂದಣಿ ಸಂಖ್ಯೆ ಏನು?",
    },
    "official_app": {
        "en": "I will contact the company through its official app.",
        "hi": "मैं कंपनी के ऑफ़िशियल ऐप से खुद संपर्क करूँगा।",
        "kn": "ಕಂಪನಿಯ ಅಧಿಕೃತ ಆ್ಯಪ್ ಮೂಲಕ ನಾನೇ ಸಂಪರ್ಕಿಸುತ್ತೇನೆ.",
    },
}

# Which questions to show for each kind of scam (two or three each).
ASK = {
    "digital_arrest": ["name_id", "in_person", "in_writing"],
    "credential": ["callback", "family_first"],
    "remote": ["company_details", "callback"],
    "payment": ["family_first", "in_writing", "callback"],
    "parcel": ["in_writing", "callback", "in_person"],
    "kyc": ["in_person", "callback"],
    "utility": ["callback", "in_writing"],
    "bait": ["why_pay_to_receive", "in_writing"],
    "emergency": ["secret_question", "call_usual_number"],
    "upi_receive": ["why_pay_to_receive", "family_first"],
    "job": ["company_details", "why_pay_to_receive"],
    "investment": ["sebi_number", "company_details", "family_first"],
    "customer_care": ["official_app", "callback"],
    "generic": ["name_id", "callback", "family_first"],
}


def ask_for(stt_lang: str, scam_type: str) -> list[dict]:
    """Questions for this kind of scam: [{"text": <Hindi or Kannada>, "en": <English>}, ...]."""
    lang = warning_lang(stt_lang)
    return [{"text": QUESTIONS[q][lang], "en": QUESTIONS[q]["en"]}
            for q in ASK.get(scam_type, ASK["generic"])]
