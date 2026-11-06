"""Synthetic calls written the way Prisma would transcribe them.

Used by demo mode (no API key) and by the detector tests. All names, numbers
and agencies here are fictional. No real call data is used anywhere.
"""

CALLS = {
    ("hi-IN", "scam"): [
        "नमस्ते, मैं मुंबई क्राइम ब्रांच से इंस्पेक्टर राठौर बोल रहा हूँ।",
        "आपके नाम से फेडेक्स का एक पार्सल पकड़ा गया है जिसमें ड्रग्स और पाँच पासपोर्ट मिले हैं।",
        "आपके आधार नंबर से मनी लॉन्ड्रिंग का केस दर्ज हुआ है, आपके खिलाफ अरेस्ट वारंट है।",
        "अभी हम आपको डिजिटल अरेस्ट में रख रहे हैं, वीडियो कॉल पर रहिए और किसी को मत बताइए।",
        "फ़ोन मत काटिए, वरना लोकल पुलिस एक घंटे में आपके घर आ जाएगी।",
        "वेरिफिकेशन के लिए अपने खाते के सारे पैसे आरबीआई के सेफ अकाउंट में ट्रांसफर कीजिए।",
    ],
    ("hi-IN", "legit"): [
        "नमस्ते, मैं एचडीएफसी बैंक से बोल रही हूँ, आपके क्रेडिट कार्ड पर एक नया ऑफर है।",
        "क्या आप अभी दो मिनट बात कर सकते हैं?",
        "ध्यान रखिए, बैंक कभी भी ओटीपी नहीं मांगता, ओटीपी किसी को मत बताइए।",
        "अगर आप रुचि रखते हैं तो हमारी शाखा पर आकर फॉर्म भर सकते हैं।",
        "धन्यवाद, आपका दिन शुभ हो।",
    ],
    ("en-IN", "scam"): [
        "Hello, main Mumbai cyber crime branch se officer bol raha hoon.",
        "Aapke naam se ek FedEx parcel seize hua hai, usme drugs mile hain.",
        "Aapke against money laundering ka case file hua hai, arrest warrant nikla hai.",
        "Aap abhi digital arrest mein hain, video call pe rahiye, kisi ko mat bataiye.",
        "Verification ke liye apna OTP bataiye aur AnyDesk app download kijiye.",
        "Saare paise RBI ke safe account mein transfer kijiye, turant.",
    ],
    ("en-IN", "legit"): [
        "Hello sir, main Swiggy delivery partner bol raha hoon.",
        "Aapka order ready hai, building ka gate number kya hai?",
        "Cash on delivery hai, total do sau pachaas rupaye.",
        "Theek hai sir, paanch minute mein pahunch raha hoon. Thank you.",
    ],
    ("kn-IN", "scam"): [
        "ನಮಸ್ಕಾರ, ನಾನು ಸಿಬಿಐ ಅಧಿಕಾರಿ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ.",
        "ನಿಮ್ಮ ಹೆಸರಿನಲ್ಲಿ ಒಂದು ಕೊರಿಯರ್ ಪಾರ್ಸೆಲ್ ಸಿಕ್ಕಿದೆ, ಅದರಲ್ಲಿ ಡ್ರಗ್ಸ್ ಇವೆ.",
        "ನಿಮ್ಮ ಮೇಲೆ ಮನಿ ಲಾಂಡರಿಂಗ್ ಕೇಸ್ ಇದೆ, ನಿಮ್ಮನ್ನು ಡಿಜಿಟಲ್ ಅರೆಸ್ಟ್ ಮಾಡಲಾಗಿದೆ.",
        "ವಿಡಿಯೋ ಕಾಲ್‌ನಲ್ಲೇ ಇರಿ, ಯಾರಿಗೂ ಹೇಳಬೇಡಿ, ಕರೆ ಕಟ್ ಮಾಡಬೇಡಿ.",
        "ತಕ್ಷಣ ನಿಮ್ಮ ಹಣವನ್ನು ಆರ್‌ಬಿಐ ಸೇಫ್ ಅಕೌಂಟ್‌ಗೆ ವರ್ಗಾಯಿಸಿ.",
    ],
    ("kn-IN", "legit"): [
        "ನಮಸ್ಕಾರ, ನಾನು ಡೆಲಿವರಿ ಹುಡುಗ, ನಿಮ್ಮ ಆರ್ಡರ್ ತಂದಿದ್ದೇನೆ.",
        "ನಿಮ್ಮ ಮನೆ ವಿಳಾಸ ಸರಿಯಾಗಿದೆಯಾ? ಗೇಟ್ ಹತ್ತಿರ ನಿಂತಿದ್ದೇನೆ.",
        "ಕ್ಯಾಶ್ ಆನ್ ಡೆಲಿವರಿ ಇದೆ, ಐದು ನೂರು ರೂಪಾಯಿ ಆಗುತ್ತದೆ.",
        "ಸರಿ, ಐದು ನಿಮಿಷದಲ್ಲಿ ಬರುತ್ತೇನೆ. ಧನ್ಯವಾದ.",
    ],

    # ---- Added Nov 6: five more scam types, each with genuine look-alikes ----

    # Family emergency: a "son" on a new number needs money for an accident.
    ("en-IN", "family"): [
        "Hello papa, main Rahul bol raha hoon, yeh mera naya number hai.",
        "Papa mera accident ho gaya hai, main hospital mein hoon.",
        "Doctor operation ke liye turant pachaas hazaar maang rahe hain, jaldi paise bhej do.",
        "Mummy ko mat batana, woh pareshaan ho jayengi.",
    ],
    ("hi-IN", "family"): [
        "हेलो पापा, मैं राहुल बोल रहा हूँ, यह मेरा नया नंबर है।",
        "पापा मेरा एक्सीडेंट हो गया है, मैं अस्पताल में हूँ।",
        "डॉक्टर ऑपरेशन के लिए तुरंत पचास हज़ार माँग रहे हैं, जल्दी पैसे भेज दो।",
        "मम्मी को मत बताना, वो परेशान हो जाएँगी।",
    ],
    ("kn-IN", "family"): [
        "ಹಲೋ ಅಪ್ಪ, ನಾನು ರಾಹುಲ್, ಇದು ನನ್ನ ಹೊಸ ನಂಬರ್.",
        "ಅಪ್ಪ, ನನಗೆ ಆಕ್ಸಿಡೆಂಟ್ ಆಗಿದೆ, ನಾನು ಆಸ್ಪತ್ರೆಯಲ್ಲಿ ಇದ್ದೇನೆ.",
        "ಆಪರೇಷನ್‌ಗೆ ತಕ್ಷಣ ಐವತ್ತು ಸಾವಿರ ಬೇಕು, ಬೇಗ ಹಣ ಕಳುಹಿಸಿ.",
        "ಅಮ್ಮನಿಗೆ ಹೇಳಬೇಡಿ, ಅವರು ಗಾಬರಿ ಆಗುತ್ತಾರೆ.",
    ],

    # UPI QR: a fake "army officer" buyer asks you to scan and enter your PIN.
    ("en-IN", "upi"): [
        "Namaste, main army mein officer hoon, aapka OLX pe dala hua sofa kharidna hai.",
        "Main aapko advance payment ke liye ek QR code bhej raha hoon.",
        "QR scan karke apna UPI PIN daaliye, paise turant aapke account mein aa jayenge.",
    ],
    ("hi-IN", "upi"): [
        "नमस्ते, मैं आर्मी में ऑफ़िसर हूँ, आपका ओएलएक्स पर डाला हुआ सोफ़ा खरीदना है।",
        "मैं आपको एडवांस के लिए एक क्यूआर कोड भेज रहा हूँ।",
        "क्यूआर स्कैन करके अपना यूपीआई पिन डालिए, पैसे तुरंत आपके खाते में आ जाएँगे।",
    ],
    ("kn-IN", "upi"): [
        "ನಮಸ್ಕಾರ, ನಾನು ಆರ್ಮಿ ಆಫೀಸರ್, ನಿಮ್ಮ ಸೋಫಾ ಖರೀದಿಸಬೇಕು.",
        "ನಾನು ಒಂದು ಕ್ಯೂಆರ್ ಕೋಡ್ ಕಳುಹಿಸುತ್ತೇನೆ.",
        "ಕ್ಯೂಆರ್ ಸ್ಕ್ಯಾನ್ ಮಾಡಿ ನಿಮ್ಮ ಯುಪಿಐ ಪಿನ್ ಹಾಕಿ, ಹಣ ತಕ್ಷಣ ನಿಮ್ಮ ಖಾತೆಗೆ ಬರುತ್ತದೆ.",
    ],

    # Job / task: paid for liking videos, then a "registration fee".
    ("en-IN", "job"): [
        "Hello, aapke liye ek part time job offer hai, ghar baithe kaam.",
        "Bas YouTube videos like karne hain, har like ke pachaas rupaye milenge.",
        "Roz paanch hazaar tak kama sakte hain, Telegram group join kijiye.",
        "Task unlock karne ke liye pehle do hazaar rupaye registration fee jama kijiye.",
    ],
    ("hi-IN", "job"): [
        "नमस्ते, आपके लिए एक पार्ट टाइम जॉब है, घर बैठे काम।",
        "बस यूट्यूब वीडियो लाइक करने हैं, हर लाइक के पचास रुपये मिलेंगे।",
        "टास्क अनलॉक करने के लिए पहले दो हज़ार रुपये रजिस्ट्रेशन फीस जमा कीजिए।",
    ],
    ("kn-IN", "job"): [
        "ನಮಸ್ಕಾರ, ನಿಮಗೆ ಒಂದು ಪಾರ್ಟ್ ಟೈಮ್ ಜಾಬ್ ಇದೆ, ಮನೆಯಲ್ಲೇ ಕೆಲಸ.",
        "ಯೂಟ್ಯೂಬ್ ವಿಡಿಯೋ ಲೈಕ್ ಮಾಡಿದರೆ ಪ್ರತಿ ಲೈಕ್‌ಗೆ ಐವತ್ತು ರೂಪಾಯಿ ಸಿಗುತ್ತದೆ.",
        "ಟಾಸ್ಕ್ ಅನ್‌ಲಾಕ್ ಮಾಡಲು ಮೊದಲು ಎರಡು ಸಾವಿರ ರೂಪಾಯಿ ರಿಜಿಸ್ಟ್ರೇಷನ್ ಫೀ ಕಟ್ಟಿ.",
    ],

    # Investment: a "VIP trading group" with guaranteed returns and an app.
    ("en-IN", "investment"): [
        "Sir, main ek stock market advisory company se bol raha hoon.",
        "Hamare VIP trading group mein guaranteed thirty percent monthly return milta hai.",
        "Bas yeh trading app download kijiye aur pehle das hazaar rupaye invest kijiye.",
        "Paisa ek mahine mein double ho jayega, offer sirf aaj ke liye hai.",
    ],
    ("hi-IN", "investment"): [
        "सर, हमारे वीआईपी ट्रेडिंग ग्रुप में गारंटीड तीस प्रतिशत रिटर्न मिलता है।",
        "बस यह ट्रेडिंग ऐप डाउनलोड कीजिए और पहले दस हज़ार रुपये इन्वेस्ट कीजिए।",
        "एक महीने में पैसा डबल हो जाएगा।",
    ],
    ("kn-IN", "investment"): [
        "ಸರ್, ನಮ್ಮ ವಿಐಪಿ ಟ್ರೇಡಿಂಗ್ ಗ್ರೂಪ್‌ನಲ್ಲಿ ಗ್ಯಾರಂಟಿ ಮೂವತ್ತು ಪರ್ಸೆಂಟ್ ರಿಟರ್ನ್ ಸಿಗುತ್ತದೆ.",
        "ಈ ಟ್ರೇಡಿಂಗ್ ಆ್ಯಪ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ, ಮೊದಲು ಹತ್ತು ಸಾವಿರ ರೂಪಾಯಿ ಇನ್ವೆಸ್ಟ್ ಮಾಡಿ.",
        "ಒಂದು ತಿಂಗಳಲ್ಲಿ ಹಣ ಡಬಲ್ ಆಗುತ್ತದೆ.",
    ],

    # Fake customer care: a stuck refund, then AnyDesk, then the OTP.
    ("en-IN", "customer_care"): [
        "Hello, main Flipkart customer care se bol raha hoon, aapne complaint ki thi.",
        "Aapka refund atka hua hai, use process karna padega.",
        "Iske liye AnyDesk app download kijiye, main screen pe help karunga.",
        "Ab aapke phone pe ek OTP aayega, woh bata dijiye.",
    ],
    ("hi-IN", "customer_care"): [
        "हेलो, मैं फ्लिपकार्ट कस्टमर केयर से बोल रहा हूँ, आपकी शिकायत के बारे में।",
        "आपका रिफंड अटका हुआ है, इसके लिए एनीडेस्क ऐप डाउनलोड कीजिए।",
        "अब आपके फ़ोन पर एक ओटीपी आएगा, वो बता दीजिए।",
    ],
    ("kn-IN", "customer_care"): [
        "ಹಲೋ, ನಾನು ಫ್ಲಿಪ್‌ಕಾರ್ಟ್ ಕಸ್ಟಮರ್ ಕೇರ್‌ನಿಂದ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ.",
        "ನಿಮ್ಮ ರಿಫಂಡ್ ಬಾಕಿ ಇದೆ, ಅದಕ್ಕೆ ಎನಿಡೆಸ್ಕ್ ಆ್ಯಪ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ.",
        "ಈಗ ನಿಮ್ಮ ಫೋನ್‌ಗೆ ಒಂದು ಒಟಿಪಿ ಬರುತ್ತದೆ, ಅದನ್ನು ಹೇಳಿ.",
    ],

    # Genuine look-alikes that must stay quiet.
    # A real family call that mentions a hospital visit.
    ("en-IN", "legit_family"): [
        "Hello beta, khana kha liya?",
        "Kal papa ke saath hospital gaye the, regular checkup tha, sab theek hai.",
        "Weekend pe ghar aa jaana, mummy ne tumhara favourite khana banaya hai.",
    ],
    ("hi-IN", "legit_family"): [
        "हेलो बेटा, खाना खा लिया?",
        "कल पापा के साथ अस्पताल गए थे, रेगुलर चेकअप था, सब ठीक है।",
        "वीकेंड पर घर आ जाना, मम्मी ने तुम्हारा पसंदीदा खाना बनाया है।",
    ],
    ("kn-IN", "legit_family"): [
        "ಹಲೋ ಮಗ, ಊಟ ಆಯ್ತಾ?",
        "ನಿನ್ನೆ ಅಪ್ಪನ ಜೊತೆ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿದ್ದೆ, ಸಾಮಾನ್ಯ ಚೆಕಪ್, ಎಲ್ಲಾ ಚೆನ್ನಾಗಿದೆ.",
        "ಶನಿವಾರ ಮನೆಗೆ ಬಾ, ಅಮ್ಮ ನಿನಗಿಷ್ಟದ ಊಟ ಮಾಡಿದ್ದಾರೆ.",
    ],
    # A real customer-care call about a refund that asks for nothing.
    ("en-IN", "legit_refund"): [
        "Namaste, main Amazon customer care se bol rahi hoon.",
        "Aapke return ka refund process ho gaya hai, teen se paanch din mein aapke account mein aa jayega.",
        "Iske liye aapko kuch karne ki zaroorat nahi hai. Dhanyavaad.",
    ],
    ("hi-IN", "legit_refund"): [
        "नमस्ते, मैं अमेज़न कस्टमर केयर से बोल रही हूँ।",
        "आपके रिटर्न का रिफंड हो गया है, तीन से पाँच दिन में आपके खाते में आ जाएगा।",
        "आपको कुछ करने की ज़रूरत नहीं है। धन्यवाद।",
    ],
    ("kn-IN", "legit_refund"): [
        "ನಮಸ್ಕಾರ, ನಾನು ಅಮೆಜಾನ್ ಕಸ್ಟಮರ್ ಕೇರ್‌ನಿಂದ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ.",
        "ನಿಮ್ಮ ರಿಫಂಡ್ ಮೂರು ದಿನಗಳಲ್ಲಿ ನಿಮ್ಮ ಖಾತೆಗೆ ಬರುತ್ತದೆ.",
        "ನೀವು ಏನೂ ಮಾಡಬೇಕಿಲ್ಲ. ಧನ್ಯವಾದ.",
    ],
}

# Which scam type each scripted scam call should be detected as (used by tests).
EXPECTED_TYPE = {
    "scam": "digital_arrest",
    "family": "emergency",
    "upi": "upi_receive",
    "job": "job",
    "investment": "investment",
    "customer_care": "customer_care",
}
SCAM_SCRIPTS = list(EXPECTED_TYPE)
LEGIT_SCRIPTS = ["legit", "legit_family", "legit_refund"]


def get_call(lang: str, kind: str) -> list[str]:
    """Lines of one scripted call; falls back to Hindi, then the fake-police scam."""
    return CALLS.get((lang, kind)) or CALLS.get(("hi-IN", kind)) or CALLS[("hi-IN", "scam")]
