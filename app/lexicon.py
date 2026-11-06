"""Red-flag signals for Indian phone scams.

Prisma returns native script for hi-IN (Devanagari) and kn-IN (Kannada), and
Latin script for en-IN (Hinglish). English loanwords like "CBI" or "OTP"
therefore show up as सीबीआई / ಸಿಬಿಐ, so every signal lists all three scripts.

Each pattern is a regular expression. Pure-ASCII patterns get word
boundaries automatically; Indic patterns are matched as substrings because
vowel signs break regex word boundaries in Indic scripts.

IMPORTANT: check the Kannada and Hindi patterns against real Prisma
transcripts and with a native speaker. Spelling variants are common.
"""
import re
from dataclasses import dataclass, field


@dataclass
class Signal:
    category: str
    weight: int
    label: str  # shown in the UI
    patterns: list[str]
    compiled: list[re.Pattern] = field(default_factory=list, repr=False)


def _compile(p: str) -> re.Pattern:
    if p.isascii():
        p = rf"(?<![a-z0-9])(?:{p})(?![a-z0-9])"
    return re.compile(p, re.IGNORECASE)


FON = "(?:फ़ोन|फोन|कॉल)"  # Hindi "phone/call" with and without nukta
# Hinglish "pe/par" ("on"). Live Prisma (en-IN) writes "pe" as "pay", e.g.
# "aapke naam pay fedex parcel", so accept the English-looking spellings too.
PE = "pe|pay|par|per"

SIGNALS: list[Signal] = [
    Signal("digital_arrest", 35, "Says you are under 'digital arrest'", [
        r"digital (?:arrest|giraftari)",
        "डिजिटल (?:अरेस्ट|गिरफ़्तारी|गिरफ्तारी)",
        "ಡಿಜಿಟಲ್ ಅರೆಸ್ಟ್",
    ]),
    Signal("authority", 15, "Claims to be police or a government officer", [
        r"cbi|c b i|police|crime branch|cyber (?:cell|crime)|customs|narcotics|ncb|trai|rbi|"
        r"enforcement directorate|income tax|court|judge|ips officer|inspector",
        # "कस्टम(?!र)": customs, but not कस्टमर (customer), as in "customer care".
        "सीबीआई|सी बी आई|पुलिस|क्राइम ब्रांच|साइबर (?:सेल|क्राइम)|कस्टम(?!र)|नारकोटिक्स|ट्राई|आरबीआई|"
        "इनकम टैक्स|आयकर|अदालत|कोर्ट|इंस्पेक्टर|ईडी ",
        "ಸಿಬಿಐ|ಪೊಲೀಸ್|ಕ್ರೈಂ ಬ್ರಾಂಚ್|ಸೈಬರ್|ಕಸ್ಟಮ್ಸ್|ಆರ್‌ಬಿಐ|ಆರ್ಬಿಐ|ಟ್ರಾಯ್|ನ್ಯಾಯಾಲಯ|ಕೋರ್ಟ್|ಇನ್ಸ್‌ಪೆಕ್ಟರ್|ಇನ್ಸ್ಪೆಕ್ಟರ್|ಅಧಿಕಾರಿ",
    ]),
    Signal("threat", 20, "Threatens arrest, a case or jail", [
        r"arrest\w*|warrant|jail|fir|money laundering|drugs?|illegal|legal action|case (?:file|darj|register)",
        "गिरफ़्तार|गिरफ्तार|अरेस्ट|वारंट|जेल|एफआईआर|मनी लॉन्ड्रिंग|ड्रग्स|ड्रग|अवैध|गैरकानूनी|"
        "कानूनी कार्रवाई|केस (?:दर्ज|फाइल|रजिस्टर)",
        "ಬಂಧನ|ಬಂಧಿಸ|ಅರೆಸ್ಟ್|ವಾರಂಟ್|ಜೈಲ|ಎಫ್‌ಐಆರ್|ಎಫ್ಐಆರ್|ಮನಿ ಲಾಂಡರಿಂಗ್|ಡ್ರಗ್ಸ್|ಕಾನೂನು ಕ್ರಮ|ಕೇಸ್",
    ]),
    Signal("secrecy", 25, "Tells you to stay quiet or stay on the call", [
        r"(?:\w+ ko|kisiko) (?:mat|na|nahi) (?:batana|bataiye|batao|bataye|batna)|"
        r"(?:phone|call) (?:mat|na) (?:kaatna|katna|kaatiye|katiye|kaato|kato|kaatein|disconnect)|"
        rf"video call (?:{PE}) (?:rahiye|raho|rahein|bane)|don'?t tell anyone|do not disconnect|stay on (?:the )?(?:video )?call",
        "को (?:मत|ना|न|नहीं) बता|" + FON + " (?:मत|ना|न) (?:काट|कट|डिस्कनेक्ट)|"
        "वीडियो कॉल (?:पर|पे) (?:रहिए|रहो|रहें|रहे|बने)|कैमरा (?:ऑन|चालू)|अकेले (?:रहिए|रहो|कमरे)",
        "ಹೇಳ ?ಬೇಡ|(?:ಕರೆ|ಫೋನ್|ಕಾಲ್) ಕಟ್ ಮಾಡಬೇಡಿ|ವಿಡಿಯೋ ಕಾಲ್‌?ನಲ್ಲೇ? ಇರಿ|ಕ್ಯಾಮೆರಾ ಆನ್|ಒಬ್ಬರೇ ಇರಿ",
    ]),
    Signal("urgency", 10, "Rushes you", [
        r"turant|fauran|immediately|right now|within (?:one|1|two|2) hours?|ek ghante|do ghante|aaj raat|last warning|warna",
        "तुरंत|फ़ौरन|फौरन|अभी के अभी|(?:एक|दो) घंटे|घंटे के अंदर|आज रात|आखिरी (?:मौका|चेतावनी)|वरना",
        "ತಕ್ಷಣ|ಈಗಲೇ|ಒಂದು ಗಂಟೆ|ಗಂಟೆಯೊಳಗೆ|(?:ಇವತ್ತು|ಇಂದು) ರಾತ್ರಿ|ಕೊನೆಯ ಎಚ್ಚರಿಕೆ|ಇಲ್ಲದಿದ್ದರೆ",
    ]),
    Signal("payment", 25, "Asks you to move or pay money", [
        r"(?:paise|paisa|rupees|rupaye|rupay|rupye|amount|money|funds).{0,40}(?:transfer|bhej|daal|jama|deposit|invest)\w*|"
        r"invest (?:kijiye|karo|karein|kar do|karna)|(?:registration|joining|activation) fee|"
        r"safe account|secure account|transfer (?:kijiye|karo|karein|kar do)|security deposit|processing fee|"
        r"penalty|fine bhar|google pay|phonepe|paytm|upi|u p i",
        "(?:पैसे|पैसा|रुपये|रकम|अमाउंट|राशि).{0,40}(?:ट्रांसफर|भेज|डाल|जमा|इन्वेस्ट|निवेश)|रजिस्ट्रेशन फीस|जॉइनिंग फीस|सेफ (?:अकाउंट|अकाउन्ट)|सुरक्षित खाते|"
        "ट्रांसफर (?:कीजिए|करें|करो|कर दो|कर दीजिए)|जुर्माना|पेनल्टी|प्रोसेसिंग फीस|सिक्योरिटी डिपॉजिट|"
        "गूगल पे|फोन पे|फ़ोन पे|पेटीएम|यू ?पी ?आई",  # Prisma also writes यू पी आई
        "(?:ಹಣ|ರೂಪಾಯಿ).{0,40}(?:ವರ್ಗಾಯಿಸ|ಕಳುಹಿಸ|ಹಾಕಿ|ಟ್ರಾನ್ಸ್‌ಫರ್|ಟ್ರಾನ್ಸ್ಫರ್|ಜಮಾ|ಇನ್ವೆಸ್ಟ್|ಹೂಡಿ|ಕಟ್ಟಿ)|ರಿಜಿಸ್ಟ್ರೇಷನ್ ಫೀ|ಸೇಫ್ ಅಕೌಂಟ್|ಸುರಕ್ಷಿತ ಖಾತೆ|"
        "ದಂಡ|ಪ್ರೊಸೆಸಿಂಗ್ ಫೀ|ಗೂಗಲ್ ಪೇ|ಫೋನ್ ಪೇ|ಯುಪಿಐ",
    ]),
    Signal("credential", 35, "Asks for your OTP, PIN or password", [
        r"(?:otp|o t p|pin|cvv|password|card number).{0,30}(?:bata|bol|share|send|bhej|tell|read|daal)\w*|"
        r"(?:bata|bol|share|send|tell)\w*.{0,15}(?:otp|cvv|pin)",
        "(?:ओटीपी|ओ टी पी|पिन|सीवीवी|पासवर्ड|कार्ड नंबर).{0,30}(?:बता|बोल|भेज|शेयर|पढ़|डाल)",
        "(?:ಒಟಿಪಿ|ಓಟಿಪಿ|ಪಿನ್|ಸಿವಿವಿ|ಪಾಸ್‌ವರ್ಡ್|ಪಾಸ್ವರ್ಡ್).{0,30}(?:ಹೇಳಿ|ಹೇಳ್ತೀರಾ|ಕಳುಹಿಸಿ|ಓದಿ|ಶೇರ್|ಹಾಕಿ)",
    ]),
    Signal("remote", 35, "Asks you to install an app or share your screen", [
        r"any ?desk|team ?viewer|quick ?support|rust ?desk|screen share|"
        r"(?:app|apk).{0,20}(?:download|install)\w*|" + rf"link (?:{PE}) click\w*",
        "एनीडेस्क|एनी डेस्क|टीमव्यूअर|टीम व्यूअर|स्क्रीन शेयर|(?:ऐप|एप|एपीके).{0,20}(?:डाउनलोड|इंस्टॉल)|लिंक (?:पर|पे) क्लिक",
        "ಎನಿಡೆಸ್ಕ್|ಎನಿ ಡೆಸ್ಕ್|ಟೀಮ್ ?ವ್ಯೂವರ್|ಸ್ಕ್ರೀನ್ ಶೇರ್|(?:ಆಪ್|ಆ್ಯಪ್|ಎಪಿಕೆ).{0,20}(?:ಡೌನ್‌ಲೋಡ್|ಡೌನ್ಲೋಡ್|ಇನ್‌ಸ್ಟಾಲ್|ಇನ್ಸ್ಟಾಲ್)|ಲಿಂಕ್.{0,10}ಕ್ಲಿಕ್",
    ]),
    Signal("parcel", 15, "Tells a parcel or courier story", [
        r"parcel|courier|fedex|fed ex|dhl|blue dart|package seized|seize",
        "पार्सल|कूरियर|कुरियर|फेडएक्स|फेडेक्स|ज़ब्त|जब्त|सीज़|सीज",
        "ಪಾರ್ಸೆಲ್|ಕೊರಿಯರ್|ಫೆಡ್‌ಎಕ್ಸ್|ಫೆಡೆಕ್ಸ್|ವಶಪಡಿಸ",
    ]),
    Signal("kyc", 15, "Threatens to block your KYC, SIM or account", [
        r"kyc|k y c|(?:sim|account|card|khata).{0,20}(?:block|band|suspend|deactivate)\w*|aadhaar.{0,15}link",
        "केवाईसी|के वाई सी|(?:सिम|खाता|अकाउंट|अकाउन्ट|कार्ड).{0,20}(?:ब्लॉक|बंद)|आधार.{0,15}लिंक",
        "ಕೆವೈಸಿ|(?:ಸಿಮ್|ಖಾತೆ|ಅಕೌಂಟ್|ಕಾರ್ಡ್).{0,20}(?:ಬ್ಲಾಕ್|ಬಂದ್|ಸ್ಥಗಿತ)|ಆಧಾರ್.{0,15}ಲಿಂಕ್",
    ]),
    Signal("utility", 20, "Threatens to cut your electricity", [
        r"(?:bijli|electricity|light|power) .{0,25}(?:cut|kaat|kat|band|disconnect)\w*|bill.{0,15}(?:pending|baki|update)",
        "(?:बिजली|लाइट|इलेक्ट्रिसिटी).{0,25}(?:कट|काट|बंद)|बिल.{0,15}(?:बकाया|पेंडिंग|अपडेट)",
        "(?:ವಿದ್ಯುತ್|ಕರೆಂಟ್|ಲೈಟ್).{0,25}(?:ಕಟ್|ಕಡಿತ|ಸ್ಥಗಿತ)|ಬಿಲ್.{0,15}(?:ಬಾಕಿ|ಪೆಂಡಿಂಗ್|ಅಪ್ಡೇಟ್)",
    ]),
    Signal("bait", 20, "Lottery prize or 'money sent by mistake' story", [
        r"galti se.{0,20}(?:paise|transfer|bhej)\w*|wrong(?:ly)? (?:transfer|sent)|lottery|prize|jackpot|kbc|"
        r"inaam|(?:wapas|return).{0,10}(?:kar do|kijiye|bhej)\w*",
        "गलती से.{0,20}(?:पैसे|ट्रांसफर|भेज)|लॉटरी|इनाम|ईनाम|केबीसी|कौन बनेगा करोड़पति|(?:वापस|रिटर्न).{0,10}(?:कर दो|कर दीजिए|भेज)",
        "ತಪ್ಪಾಗಿ.{0,20}(?:ಹಣ|ಕಳುಹಿಸ|ಟ್ರಾನ್ಸ್)|ಲಾಟರಿ|ಬಹುಮಾನ|ಕೆಬಿಸಿ|ವಾಪಸ್.{0,10}(?:ಕಳುಹಿಸಿ|ಹಾಕಿ)",
    ]),
    # ---- added Nov 6: five more common scams --------------------------------
    Signal("emergency", 20, "Says a family member is in trouble", [
        r"(?:beta|beti|bete|bhai|behen|papa|mummy|mom|dad|didi|son|daughter).{0,30}"
        r"(?:accident|hospital|operation|arrest\w*|pakad\w*|police station|thane|jail)|"
        r"(?:yeh|ye|this is) (?:mera |my )?(?:naya|new) number",
        "(?:बेटा|बेटी|बेटे|भाई|बहन|पापा|मम्मी|माँ|मां|दीदी).{0,30}"
        "(?:एक्सीडेंट|अस्पताल|हॉस्पिटल|ऑपरेशन|गिरफ्तार|गिरफ़्तार|पकड़|पकड|थाने|जेल)|नया नंबर",
        "(?:ಮಗ|ಮಗಳು|ಅಣ್ಣ|ತಮ್ಮ|ಅಕ್ಕ|ತಂಗಿ|ಅಪ್ಪ|ಅಮ್ಮ).{0,30}"
        "(?:ಆಕ್ಸಿಡೆಂಟ್|ಅಪಘಾತ|ಆಸ್ಪತ್ರೆ|ಹಾಸ್ಪಿಟಲ್|ಆಪರೇಷನ್|ಅರೆಸ್ಟ್|ಪೊಲೀಸ್ ಸ್ಟೇಷನ್)|ಹೊಸ ನಂಬರ್",
    ]),
    Signal("upi_receive", 35, "Asks you to scan a QR or enter your PIN to receive money", [
        # Tuned Nov 6 to a live Prisma transcript: Prisma dropped "scan karke apna UPI"
        # and shortened the verb, writing "क्यूआर पिन डालिए पैसे तुरंत आपके अकाउन्ट में आ जाए".
        # So: QR and PIN in one sentence is enough, a QR sent "for payment" counts,
        # and short verb forms (aa jaye, आ जाए, ಬರುತ್ತ…) are accepted.
        r"(?:qr|scan|pin).{0,60}(?:receive\w*|milenge|mil jayenge|mil jaye\w*|aayenge|aa jayenge|aa jaenge|aa jaye\w*|credit ho\w*)|"
        r"qr.{0,40}pin|pin.{0,40}qr|(?:payment|advance|paise)\w*.{0,25}qr|collect request|request accept\w*",
        "(?:क्यूआर|स्कैन|पिन).{0,60}(?:रिसीव|मिलेंगे|मिल जाएंगे|मिल जाएँगे|मिल जाए|मिलेगा|आएंगे|आएँगे|आ जाएंगे|आ जाएँगे|आ जाएगा|आ जाए|क्रेडिट)|"
        "क्यूआर.{0,40}पिन|पिन.{0,40}क्यूआर|(?:पेमेंट|एडवांस|अडवांस|पैसे).{0,25}क्यूआर|कलेक्ट रिक्वेस्ट",
        "(?:ಕ್ಯೂಆರ್|ಸ್ಕ್ಯಾನ್|ಪಿನ್).{0,60}(?:ರಿಸೀವ್|ಬರುತ್ತ|ಸಿಗುತ್ತ|ಕ್ರೆಡಿಟ್)|"
        "ಕ್ಯೂಆರ್.{0,40}ಪಿನ್|ಪಿನ್.{0,40}ಕ್ಯೂಆರ್|(?:ಪೇಮೆಂಟ್|ಅಡ್ವಾನ್ಸ್|ಹಣ).{0,25}ಕ್ಯೂಆರ್|ಕಲೆಕ್ಟ್ ರಿಕ್ವೆಸ್ಟ್",
    ]),
    Signal("job", 20, "Offers easy money for online tasks or a part-time job", [
        r"part[ -]?time (?:job|kaam|work)|ghar (?:baithe|se) (?:kamai\w*|kamaye|kaam|paise)|work from home|"
        r"(?:like|review|rating)\w* .{0,30}(?:paise|rupaye|rupees|kamai|kama)\w*|task\w*|telegram group|daily (?:earning|income)",
        "पार्ट टाइम (?:जॉब|नौकरी|काम)|घर बैठे (?:कमा|काम|पैसे)|(?:लाइक|रिव्यू|रेटिंग).{0,30}(?:पैसे|रुपये|कमा)|टास्क|टेलीग्राम ग्रुप",
        "ಪಾರ್ಟ್ ಟೈಮ್ (?:ಜಾಬ್|ಕೆಲಸ)|ಮನೆಯಲ್ಲೇ.{0,20}(?:ಕೆಲಸ|ಹಣ|ಸಂಪಾದ)|ಲೈಕ್.{0,30}(?:ಹಣ|ರೂಪಾಯಿ|ಸಂಪಾದ)|ಟಾಸ್ಕ್|ಟೆಲಿಗ್ರಾಮ್ ಗ್ರೂಪ್",
    ]),
    Signal("investment", 20, "Promises guaranteed returns or doubled money", [
        r"guarante\w* .{0,30}(?:return|profit|income)\w*|(?:paisa|paise|money|amount) .{0,20}double|"
        r"double (?:ho jayega|kar denge|return)|trading (?:app|group|tips)|stock tips?|vip group|crypto\w*|ipo allotment",
        "गारंटीड.{0,30}(?:रिटर्न|प्रॉफिट|मुनाफा|मुनाफ़ा)|(?:पैसा|पैसे) डबल|डबल हो जाएगा|ट्रेडिंग (?:ऐप|ग्रुप)|स्टॉक टिप्स|वीआईपी ग्रुप|क्रिप्टो",
        "ಗ್ಯಾರಂಟಿ.{0,30}(?:ರಿಟರ್ನ್|ಲಾಭ)|ಹಣ ಡಬಲ್|ಡಬಲ್ ಆಗುತ್ತ|ಟ್ರೇಡಿಂಗ್ (?:ಆಪ್|ಆ್ಯಪ್|ಗ್ರೂಪ್)|ಸ್ಟಾಕ್ ಟಿಪ್ಸ್|ಕ್ರಿಪ್ಟೋ",
    ]),
    Signal("customer_care", 15, "Says they are customer care, refunds or cashback", [
        r"customer (?:care|support|service)|helpline|refund\w*|cashback|complaint number",
        "कस्टमर (?:केयर|सपोर्ट|सर्विस)|रिफंड|कैशबैक|हेल्पलाइन",
        "ಕಸ್ಟಮರ್ (?:ಕೇರ್|ಸಪೋರ್ಟ್)|ರಿಫಂಡ್|ಕ್ಯಾಶ್‌?ಬ್ಯಾಕ್|ಹೆಲ್ಪ್‌?ಲೈನ್",
    ]),
]

# Genuine safety advice ("we never ask for your OTP"). When this appears in a
# segment, the credential and secrecy signals in that segment are ignored and
# the risk goes down a little.
PROTECTIVE = Signal("protective", -20, "Gives genuine safety advice", [
    r"(?:never|kabhi(?: bhi)?) .{0,20}(?:ask|maang|nahi maang|nahin maang|puchh)\w*|"
    r"(?:otp|pin).{0,25}(?:kisi ko|kisi ke saath|anyone).{0,15}(?:mat|na|never|nahi)",
    "(?:कभी|कभी भी).{0,20}(?:नहीं माँग|नहीं मांग|नहीं पूछ)|(?:ओटीपी|पिन).{0,25}(?:किसी को|किसी के साथ).{0,15}(?:मत|ना|न )",
    "ಯಾವತ್ತೂ.{0,20}ಕೇಳುವುದಿಲ್ಲ|(?:ಒಟಿಪಿ|ಓಟಿಪಿ|ಪಿನ್).{0,25}ಯಾರಿಗೂ.{0,10}ಹೇಳಬೇಡಿ",
])
SUPPRESSED_BY_PROTECTIVE = {"credential", "secrecy"}

# Extra risk when signals appear together, the classic scam "shapes".
COMBOS: list[tuple[set[str], int]] = [
    ({"authority", "threat"}, 15),
    ({"authority", "payment"}, 20),
    ({"threat", "payment"}, 15),
    ({"secrecy", "threat"}, 15),
    ({"secrecy", "payment"}, 15),
    ({"parcel", "threat"}, 10),
    # added Nov 6 with the five new scam types
    ({"emergency", "payment"}, 25),     # "I had an accident, send money"
    ({"emergency", "secrecy"}, 15),     # "...don't tell mummy"
    ({"upi_receive", "bait"}, 15),      # "money sent by mistake, scan to get it back"
    ({"upi_receive", "credential"}, 15),  # "scan the QR and enter your PIN"
    ({"job", "payment"}, 25),           # "pay a fee to unlock your earnings"
    ({"investment", "payment"}, 25),    # "invest now, guaranteed returns"
    ({"investment", "remote"}, 15),     # "download our trading app"
    ({"customer_care", "remote"}, 20),  # fake helpline asks for AnyDesk
    ({"customer_care", "credential"}, 20),  # fake helpline asks for OTP
]

for _s in SIGNALS + [PROTECTIVE]:
    _s.compiled = [_compile(p) for p in _s.patterns]

# Words for Prisma word boosting: single words, letters only (Gnani rule).
BOOST_WORDS = {
    "hi": ["सीबीआई", "ओटीपी", "केवाईसी", "पुलिस", "पार्सल", "अरेस्ट", "वारंट", "कस्टम्स", "एनीडेस्क", "फेडेक्स", "आरबीआई", "क्यूआर", "यूपीआई", "रिफंड", "टेलीग्राम"],
    "kn": ["ಸಿಬಿಐ", "ಒಟಿಪಿ", "ಕೆವೈಸಿ", "ಪೊಲೀಸ್", "ಪಾರ್ಸೆಲ್", "ಅರೆಸ್ಟ್", "ವಾರಂಟ್", "ಕಸ್ಟಮ್ಸ್", "ಎನಿಡೆಸ್ಕ್", "ಕ್ಯೂಆರ್", "ಯುಪಿಐ", "ರಿಫಂಡ್"],
    "en": ["CBI", "OTP", "KYC", "police", "parcel", "arrest", "warrant", "customs", "AnyDesk", "FedEx", "RBI", "QR", "UPI", "refund", "Telegram"],
}
