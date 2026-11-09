"""Held-out test calls, set 1: written Nov 9 before lexicon v2.

STATUS: no longer held out. These calls exposed the v1 rules' weak spots
(4 of 9 scams caught), and the v2 rules were written knowing those misses.
They now count as development data; the fair test is blind_calls.py.

Original note follows.

The 27 demo calls in mock_calls.py are the calls the detector's patterns were
tuned on, so scoring well on them is close to a best case. These 15 calls are
the honest test: new wording, scam variants the demo calls don't cover
(TRAI SIM block, customs parcel, reward points, task jobs, KBC lottery, stock
tips, a buyer posing as an army officer), and genuine calls built to look
alarming (a real bank fraud alert, police passport verification, a delivery
that really does ask for an OTP).

The expected scam type for each call was fixed before the first run, using
the name a person would give it. Rule: do not tune the lexicon on these calls.
If a change is ever made because of them, they stop being held out; write new
ones and say so.

All names, numbers and organisations are fictional or used generically.
"""

UNSEEN = {
    # ---------------- Hindi ----------------
    ("hi-IN", "trai_sim"): {
        "expected": "digital_arrest", "short": "TRAI SIM",
        "lines": [
            "नमस्कार, मैं टेलीकॉम रेगुलेटरी अथॉरिटी यानी ट्राई के दफ्तर से बोल रहा हूँ।",
            "आपके आधार कार्ड से एक और सिम निकाली गई है जिससे लोगों को धमकी भरे मैसेज भेजे गए हैं।",
            "दो घंटे बाद आपके सारे नंबर बंद कर दिए जाएंगे और आपके खिलाफ एफआईआर दर्ज होगी।",
            "मैं आपकी कॉल दिल्ली पुलिस के अधिकारी को ट्रांसफर कर रहा हूँ, उनसे बात कीजिए।",
            "जांच पूरी होने तक यह बात अपने परिवार में किसी से शेयर मत कीजिए।",
            "अपनी बेगुनाही साबित करने के लिए आपको सिक्योरिटी डिपॉज़िट जमा करना होगा, जो बाद में लौटा दिया जाएगा।",
        ],
    },
    ("hi-IN", "bijli"): {
        "expected": "utility", "short": "power bill",
        "lines": [
            "नमस्ते, मैं बिजली विभाग के ऑफिस से बोल रहा हूँ।",
            "आपका पिछले महीने का बिल हमारे सिस्टम में अपडेट नहीं हुआ है।",
            "आज रात साढ़े नौ बजे आपके घर का कनेक्शन काट दिया जाएगा।",
            "अगर कनेक्शन चालू रखना है तो अभी मैं जो ऐप भेज रहा हूँ उसे इंस्टॉल कीजिए और दस रुपये का पेमेंट कीजिए।",
        ],
    },
    ("hi-IN", "olx_army"): {
        "expected": "upi_receive", "short": "OLX buyer",
        "lines": [
            "हेलो, मैंने आपका ओएलएक्स पर डाला हुआ सोफ़ा देखा, मुझे लेना है।",
            "मैं आर्मी में हूँ, अभी कैंट में पोस्टिंग है, इसलिए खुद नहीं आ सकता।",
            "आप जो दाम बोल रहे हैं वो ठीक है, मैं पूरा एडवांस अभी भेज देता हूँ।",
            "मैं आपको व्हाट्सएप पर एक क्यूआर कोड भेज रहा हूँ, उसे स्कैन करके अपना पिन डालिए, पैसे आपके खाते में आ जाएंगे।",
        ],
    },
    ("hi-IN", "ok_fraud_alert"): {
        "expected": None, "short": "bank alert ✓",
        "lines": [
            "नमस्ते, मैं आईसीआईसीआई बैंक के फ्रॉड मॉनिटरिंग विभाग से बोल रही हूँ।",
            "आपके डेबिट कार्ड से अभी बारह हज़ार रुपये का एक ऑनलाइन लेनदेन हुआ है, क्या यह आपने किया है?",
            "ठीक है, अगर आपने नहीं किया तो हम कार्ड अभी ब्लॉक कर देते हैं, नया कार्ड घर के पते पर आ जाएगा।",
            "आपको कोई ओटीपी, पिन या पासवर्ड बताने की ज़रूरत नहीं है। धन्यवाद।",
        ],
    },
    ("hi-IN", "ok_police_verify"): {
        "expected": None, "short": "passport ✓",
        "lines": [
            "नमस्ते, मैं कोरमंगला थाने से हवलदार यादव बोल रहा हूँ।",
            "आपके पासपोर्ट आवेदन की पुलिस वेरिफिकेशन करनी है।",
            "कल सुबह ग्यारह बजे अपने आधार कार्ड और पते के प्रमाण की कॉपी लेकर थाने आ जाइए।",
            "कोई फीस नहीं है, बस दस्तख़त करने हैं।",
        ],
    },

    # ---------------- Hinglish ----------------
    ("en-IN", "customs"): {
        "expected": "parcel", "short": "customs",
        "lines": [
            "Hello, main DHL courier ki customer service se bol rahi hoon.",
            "Aapke naam ka ek international parcel Mumbai customs pe roka gaya hai.",
            "Usme kuch illegal items mile hain, isliye case cyber police ko forward ho raha hai.",
            "Agar aap FIR se bachna chahte hain toh abhi clearance charge online pay kar dijiye.",
        ],
    },
    ("en-IN", "reward_points"): {
        "expected": "credential", "short": "reward pts",
        "lines": [
            "Good afternoon sir, main SBI credit card department se bol raha hoon.",
            "Aapke card ke saat hazaar reward points aaj raat expire ho rahe hain.",
            "Main aapko SMS pe ek link bhej raha hoon, usme apna card number aur CVV bhar dijiye.",
            "Phir aapke phone pe ek code aayega, woh mujhe bata dijiye, points cash mein convert ho jayenge.",
        ],
    },
    ("en-IN", "task_job"): {
        "expected": "job", "short": "task job",
        "lines": [
            "Hi, main ek digital marketing company se HR bol rahi hoon.",
            "Ghar baithe YouTube videos like karne ka part time kaam hai, har like ke pachaas rupaye milte hain.",
            "Pehle hamara Telegram group join kijiye, wahan daily tasks milenge.",
            "Premium task ke liye pehle das hazaar deposit karna hota hai, phir aapko double wapas milta hai.",
        ],
    },
    ("en-IN", "ok_power_cut"): {
        "expected": None, "short": "power cut ✓",
        "lines": [
            "Namaste, main BESCOM ke local office se bol raha hoon.",
            "Kal subah das baje se do baje tak aapke area mein maintenance ki wajah se light nahi rahegi.",
            "Aapko kuch pay karne ki zaroorat nahi hai, bas information de rahe the. Thank you.",
        ],
    },
    ("en-IN", "ok_delivery_otp"): {
        "expected": None, "short": "delivery OTP ✓",
        "lines": [
            "Hello sir, main Flipkart se delivery boy bol raha hoon, aapka mobile phone ka parcel lekar aaya hoon.",
            "Main aapke gate ke bahar khada hoon.",
            "Yeh open box delivery hai, parcel check karne ke baad aapke phone pe jo delivery OTP aaya hai woh bata dijiye.",
        ],
    },

    # ---------------- Kannada ----------------
    ("kn-IN", "police_sim"): {
        "expected": "digital_arrest", "short": "cyber police",
        "lines": [
            "ನಮಸ್ಕಾರ, ನಾನು ಮುಂಬೈ ಸೈಬರ್ ಕ್ರೈಂ ಪೊಲೀಸ್ ಠಾಣೆಯಿಂದ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ.",
            "ನಿಮ್ಮ ಆಧಾರ್ ಸಂಖ್ಯೆ ಬಳಸಿ ಒಂದು ಬ್ಯಾಂಕ್ ಖಾತೆ ತೆರೆದು ಕೋಟಿ ರೂಪಾಯಿ ವಂಚನೆ ಮಾಡಲಾಗಿದೆ.",
            "ನಿಮ್ಮ ಮೇಲೆ ಎಫ್‌ಐಆರ್ ದಾಖಲಾಗಿದೆ, ಇವತ್ತೇ ನಿಮ್ಮನ್ನು ಬಂಧಿಸಲಾಗುತ್ತದೆ.",
            "ಈ ವಿಷಯ ಮನೆಯವರಿಗೆ ಗೊತ್ತಾಗಬಾರದು, ತನಿಖೆ ಗೌಪ್ಯವಾಗಿದೆ.",
            "ನಿಮ್ಮ ಹಣ ಸರಿಯಾದದ್ದು ಎಂದು ಪರಿಶೀಲಿಸಲು ನಾವು ಹೇಳುವ ಖಾತೆಗೆ ಎಲ್ಲ ಹಣವನ್ನು ಕಳುಹಿಸಿ.",
        ],
    },
    ("kn-IN", "kbc_lottery"): {
        "expected": "bait", "short": "KBC lottery",
        "lines": [
            "ಅಭಿನಂದನೆಗಳು ಸಾರ್, ನಿಮ್ಮ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಕೌನ್ ಬನೇಗಾ ಕರೋಡ್‌ಪತಿ ಲಕ್ಕಿ ಡ್ರಾದಲ್ಲಿ ಆಯ್ಕೆಯಾಗಿದೆ.",
            "ನೀವು ಇಪ್ಪತ್ತೈದು ಲಕ್ಷ ರೂಪಾಯಿ ಗೆದ್ದಿದ್ದೀರಿ.",
            "ಬಹುಮಾನದ ಹಣ ಪಡೆಯಲು ಮೊದಲು ಹದಿನೈದು ಸಾವಿರ ರೂಪಾಯಿ ತೆರಿಗೆ ಕಟ್ಟಬೇಕು.",
            "ಇವತ್ತು ಸಂಜೆಯೊಳಗೆ ಕಟ್ಟದಿದ್ದರೆ ಬಹುಮಾನ ರದ್ದಾಗುತ್ತದೆ.",
        ],
    },
    ("kn-IN", "stock_tips"): {
        "expected": "investment", "short": "stock tips",
        "lines": [
            "ನಮಸ್ಕಾರ, ನಾವು ಷೇರು ಮಾರುಕಟ್ಟೆ ಸಲಹೆ ಕೊಡುವ ಸಂಸ್ಥೆಯಿಂದ ಕರೆ ಮಾಡುತ್ತಿದ್ದೇವೆ.",
            "ನಮ್ಮ ವಾಟ್ಸಾಪ್ ಗುಂಪಿಗೆ ಸೇರಿದರೆ ಪ್ರತಿ ತಿಂಗಳು ಮೂವತ್ತು ಶೇಕಡಾ ಲಾಭ ಖಚಿತ.",
            "ಮೊದಲು ನಾವು ಕಳುಹಿಸುವ ಆ್ಯಪ್‌ನಲ್ಲಿ ಐವತ್ತು ಸಾವಿರ ಹೂಡಿಕೆ ಮಾಡಿ.",
            "ಈ ಆಫರ್ ಇವತ್ತು ಮಾತ್ರ, ಬೇಗ ನಿರ್ಧಾರ ಮಾಡಿ.",
        ],
    },
    ("kn-IN", "ok_hospital"): {
        "expected": None, "short": "hospital ✓",
        "lines": [
            "ನಮಸ್ಕಾರ, ನಾನು ಮಣಿಪಾಲ್ ಆಸ್ಪತ್ರೆಯ ರಿಸೆಪ್ಷನ್‌ನಿಂದ ಮಾತನಾಡುತ್ತಿದ್ದೇನೆ.",
            "ನಾಳೆ ಬೆಳಿಗ್ಗೆ ಹತ್ತು ಗಂಟೆಗೆ ನಿಮ್ಮ ತಂದೆಯವರ ಡಾಕ್ಟರ್ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಇದೆ.",
            "ಹಿಂದಿನ ರಿಪೋರ್ಟ್‌ಗಳನ್ನು ತೆಗೆದುಕೊಂಡು ಬನ್ನಿ, ಶುಲ್ಕವನ್ನು ಕೌಂಟರ್‌ನಲ್ಲೇ ಕಟ್ಟಬಹುದು.",
        ],
    },
    ("kn-IN", "ok_branch_kyc"): {
        "expected": None, "short": "branch KYC ✓",
        "lines": [
            "ನಮಸ್ಕಾರ, ನಾವು ಕೆನರಾ ಬ್ಯಾಂಕ್ ಜಯನಗರ ಶಾಖೆಯಿಂದ ಕರೆ ಮಾಡುತ್ತಿದ್ದೇವೆ.",
            "ನಿಮ್ಮ ಖಾತೆಯ ಕೆವೈಸಿ ನವೀಕರಣ ಬಾಕಿ ಇದೆ.",
            "ಸಮಯ ಸಿಕ್ಕಾಗ ಆಧಾರ್ ಮತ್ತು ಪ್ಯಾನ್ ಕಾರ್ಡ್ ಜೊತೆ ಶಾಖೆಗೆ ಬನ್ನಿ.",
            "ಫೋನಿನಲ್ಲಿ ನಾವು ಯಾವುದೇ ವಿವರ ಕೇಳುವುದಿಲ್ಲ. ಧನ್ಯವಾದ.",
        ],
    },
}
