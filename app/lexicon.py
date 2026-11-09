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
        "ಸಿಬಿಐ|ಪೊಲೀಸ್|ಕ್ರೈಂ ಬ್ರಾಂಚ್|ಸೈಬರ್|ಕಸ್ಟಮ್ಸ್|ಆರ್‌ಬಿಐ|ಆರ್ಬಿಐ|ಆರ್ ಬಿ ಐ|ಆರ್ ಬೈ|ಟ್ರಾಯ್|ನ್ಯಾಯಾಲಯ|ಕೋರ್ಟ್|ಇನ್ಸ್‌ಪೆಕ್ಟರ್|ಇನ್ಸ್ಪೆಕ್ಟರ್|ಅಧಿಕಾರಿ",
        r"(?:income )?tax department|it department|government of india|ministry|enforcement|"
        r"customs (?:department|officer)|cyber police|army|military|defen[cs]e|officer|uidai|sebi|department of telecom\w*",
        "अधिकारी|ऑफिसर|विभाग|मंत्रालय|सरकार|आर्मी|सेना|टेलीकॉम",
        "ಇಲಾಖೆ|ಸರ್ಕಾರ|ಸೇನೆ|ಆರ್ಮಿ|ಆಫೀಸರ್",
    ]),
    Signal("threat", 20, "Threatens arrest, a case or jail", [
        r"arrest\w*|warrant|jail|fir|money laundering|drugs?|illegal|legal action|case (?:file|darj|register)",
        "गिरफ़्तार|गिरफ्तार|अरेस्ट|वारंट|जेल|एफआईआर|मनी लॉन्ड्रिंग|ड्रग्स|ड्रग|अवैध|गैरकानूनी|"
        "कानूनी कार्रवाई|केस (?:दर्ज|फाइल|रजिस्टर)",
        "ಬಂಧನ|ಬಂಧಿಸ|ಅರೆಸ್ಟ್|ವಾರಂಟ್|ಜೈಲ|ಎಫ್‌ಐಆರ್|ಎಫ್ಐಆರ್|ಮನಿ ಲಾಂಡರಿಂಗ್|ಡ್ರಗ್ಸ್|ಕಾನೂನು ಕ್ರಮ|ಕೇಸ್",
        r"legal (?:action|notice|case|proceedings)|complaint (?:registered|filed|against)|"
        r"(?:account|card|number|sim|connection|policy|services?) (?:will|would|is going to) (?:be )?(?:blocked|suspended|frozen|closed|deactivated|terminated|disconnected|cancelled|seized)|"
        r"freez\w* your|summons|non[- ]bailable|criminal (?:case|charges)|lose (?:all )?(?:your )?(?:data|money|savings|account)|blacklist\w*|"
        r"(?:viral|leak|expose)\w* .{0,20}(?:video|photos?|pictures)|recovery agents?",
        "(?:खाता|अकाउंट|सिम|नंबर|कनेक्शन|कार्ड).{0,20}(?:बंद कर दि|ब्लॉक हो जा|ब्लॉक कर दि|फ्रीज)|कानूनी नोटिस|शिकायत दर्ज|समन",
        "ಕಾನೂನು|ದೂರು ದಾಖಲ|ಸ್ಥಗಿತಗೊಳ್ಳ|ಬ್ಲಾಕ್ ಆಗುತ್ತ|ರದ್ದಾಗುತ್ತ",
        r"embarrass\w*|(?:share|send|show|post)\w* (?:this|these|it|them|the|your)(?: (?:private )?(?:photos?|videos?|pictures|chats?))? (?:with|to) your (?:family|friends|workplace|office|wife|husband|contacts)|"
        r"(?:bad|low|ruin\w*) (?:cibil|credit score)|report (?:this |you )?to cibil",
    ]),
    Signal("secrecy", 25, "Tells you to stay quiet or stay on the call", [
        r"(?:\w+ ko|kisiko) (?:mat|na|nahi) (?:batana|bataiye|batao|bataye|batna)|"
        r"(?:phone|call) (?:mat|na) (?:kaatna|katna|kaatiye|katiye|kaato|kato|kaatein|disconnect)|"
        rf"video call (?:{PE}) (?:rahiye|raho|rahein|bane)|don'?t tell anyone|do not disconnect|stay on (?:the )?(?:video )?call",
        "को (?:मत|ना|न|नहीं) बता|" + FON + " (?:मत|ना|न) (?:काट|कट|डिस्कनेक्ट)|"
        "वीडियो कॉल (?:पर|पे) (?:रहिए|रहो|रहें|रहे|बने)|कैमरा (?:ऑन|चालू)|अकेले (?:रहिए|रहो|कमरे)",
        "ಹೇಳ ?ಬೇಡ|ಹೇಳ್ಬೇಡ|(?:ಕರೆ|ಫೋನ್|ಕಾಲ್) ಕಟ್ ಮಾಡಬೇಡಿ|ವಿಡಿಯೋ ಕಾಲ್[‌ ]?ನಲ್ಲೇ? ಇರಿ|ಕ್ಯಾಮೆರಾ ಆನ್|ಒಬ್ಬರೇ ಇರಿ",
        r"don'?t (?:tell|inform|share (?:this )?with|discuss (?:this )?with) (?:anyone|anybody|your (?:family|wife|husband|son|daughter|bank|parents))|"
        r"keep (?:this|it) (?:confidential|secret|between us|to yourself)|(?:confidential|secret) (?:matter|investigation|operation)|"
        r"(?:do not|don'?t) (?:hang up|cut the call|disconnect)|kisi (?:ko|se) (?:mat|na|nahi) (?:batana|bataiye|batao|share|kehna|kahiye)",
        "किसी (?:को|से) (?:मत|ना|न) (?:बता|कह|शेयर)|गोपनीय|(?:परिवार|घरवालों|घर वालों) (?:को|से).{0,15}(?:मत|ना|न)|शेयर मत",
        "ಗೊತ್ತಾಗಬಾರದು|ಗೌಪ್ಯ|ಯಾರಿಗೂ (?:ತಿಳಿಸ|ಹೇಳ)",
        r"between (?:you and me|us)|just between",
    ]),
    Signal("urgency", 10, "Rushes you", [
        r"turant|fauran|immediately|right now|within (?:one|1|two|2) hours?|ek ghante|do ghante|aaj raat|last warning|warna",
        "तुरंत|फ़ौरन|फौरन|अभी के अभी|(?:एक|दो) घंटे|घंटे के अंदर|आज रात|आखिरी (?:मौका|चेतावनी)|वरना",
        "ತಕ್ಷಣ|ಈಗಲೇ|ಒಂದು ಗಂಟೆ|ಗಂಟೆಯೊಳಗೆ|(?:ಇವತ್ತು|ಇಂದು) ರಾತ್ರಿ|ಕೊನೆಯ ಎಚ್ಚರಿಕೆ|ಇಲ್ಲದಿದ್ದರೆ",
        r"act (?:fast|now|quickly|immediately)|limited[- ]time|last (?:chance|date|day)|only (?:today|for today)|expir\w* (?:today|tonight|soon)|"
        r"within (?:\d+|one|two|24|48) (?:hours?|minutes?)|urgent\w*|right away|as soon as possible|hurry|no time|every minute|jaldi|aaj hi",
        "जल्दी|आज ही|सिर्फ आज|समय नहीं",
        "ಬೇಗ|ಇವತ್ತೇ|ಇಂದೇ|ಇವತ್ತು ಮಾತ್ರ|ಸಂಜೆಯೊಳಗೆ",
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
        r"gift ?cards?|(?:processing|verification|registration|joining|activation|clearance|release|convenience|handling|courier|customs|"
        r"service|insurance|re-?verification|training|security|unlock\w*|withdrawal|upgrade|token) (?:fee|charges?|amount|deposit)|"
        r"(?:small|nominal|one[- ]time|refundable) (?:fee|charge|payment|amount|deposit)|advance (?:payment|fee|amount)|"
        r"make (?:a |the )?payment|pay (?:kar|kijiye|karo|karein|kar do|kar dijiye|now|it now|online|through|via|using|the fee|a fee)|"
        r"payment (?:kar|kijiye|karo|karein|link)|deposit (?:kar|karna|kijiye|karo|karein)|(?:transfer|send) (?:the |rs|rupees|money|amount)",
        "(?:पेमेंट|भुगतान).{0,15}(?:कीजिए|करें|करो|कर दीजिए|करना|कर दो)|(?:फीस|शुल्क|चार्ज|डिपॉजिट|डिपॉज़िट|टैक्स|एडवांस).{0,25}(?:भर|जमा|दे|भेज|पेमेंट)|गिफ्ट कार्ड",
        "(?:ಶುಲ್ಕ|ಫೀಸ್|ತೆರಿಗೆ|ಟ್ಯಾಕ್ಸ್|ಡೆಪಾಸಿಟ್|ಮುಂಗಡ|ಅಡ್ವಾನ್ಸ್|ದಂಡ).{0,25}(?:ಕಟ್ಟ|ಪಾವತಿಸ|ಕಳುಹಿಸ|ಜಮಾ)|ಪಾವತಿ(?:ಸಿ|ಸಬೇಕು|ಮಾಡಿ)|ಪೇಮೆಂಟ್ ಮಾಡಿ|ಗಿಫ್ಟ್ ಕಾರ್ಡ್",
    ]),
    Signal("credential", 60, "Asks for your OTP, PIN, card details or password", [
        # v2 (Nov 9): card details, codes, credentials and English request verbs.
        # Not counted: "pin code" (postal), a delivery OTP at the door, Aadhaar,
        # PAN or ration card numbers, Wi-Fi passwords, and "QR code".
        r"(?:(?<!delivery )otp|(?<!delivery )o t p|one[- ]time password|pin(?! ?code)|cvv|c v v|(?<!wifi )(?<!wi-fi )password|"
        r"(?<!aadhaar )(?<!aadhar )(?<!pan )(?<!ration )card (?:number|details)|expiry(?: date)?|"
        r"(?:verification|security|secret|otp|sms) code|code (?:jo|that|which|you) .{0,20}(?:aaya|aayega|aaega|receive\w*|got|get)|"
        r"login (?:id|details|credentials)|net ?banking (?:id|password|details|credentials)|credentials)"
        r".{0,40}(?:bata|bol|share|send|bhej|tell|read|daal|dal|confirm|provide|give|need|enter|type|de do|dijiye|chahiye)\w*|"
        r"(?:bata|bol|share|send|tell|read|confirm|provide|give|need|enter|type)\w*.{0,30}"
        r"(?:(?<!delivery )otp|cvv|pin(?! ?code)|(?<!wifi )(?<!wi-fi )password|(?<!aadhaar )(?<!aadhar )(?<!pan )card (?:number|details)|"
        r"(?:verification |security |otp )code|code (?:that |which )?(?:you )?(?:received|got)|expiry|credentials|net ?banking)",
        "(?:(?<!डिलीवरी )ओटीपी|ओ टी पी|पिन(?! ?कोड)|सीवीवी|(?<!वाईफाई )पासवर्ड|(?<!आधार )कार्ड (?:नंबर|डिटेल)|एक्सपायरी|नेट ?बैंकिंग|(?:ओटीपी|वेरिफिकेशन) कोड)"
        ".{0,30}(?:बता|बोल|भेज|शेयर|पढ़|डाल|दीजिए|दें|चाहिए|कन्फर्म)",
        "(?:ಒಟಿಪಿ|ಓಟಿಪಿ|ಪಿನ್(?! ?ಕೋಡ್)|ಸಿವಿವಿ|ಪಾಸ್‌ವರ್ಡ್|ಪಾಸ್ವರ್ಡ್|(?<!ಆಧಾರ್ )ಕಾರ್ಡ್ ನಂಬರ್|ಕಾರ್ಡ್ ವಿವರ|(?:ಒಟಿಪಿ|ಓಟಿಪಿ) ಕೋಡ್)"
        ".{0,30}(?:ಹೇಳಿ|ಹೇಳ್ತೀರಾ|ಕಳುಹಿಸಿ|ಓದಿ|ಶೇರ್|ಹಾಕಿ|ಕೊಡಿ|ತಿಳಿಸಿ)",
    ]),
    Signal("remote", 35, "Asks you to install an app or share your screen", [
        r"any ?desk|team ?viewer|quick ?support|rust ?desk|screen share|"
        r"(?:app|apk).{0,20}(?:download|install)\w*|" + rf"link (?:{PE}) click\w*",
        "एनीडेस्क|एनी डेस्क|टीमव्यूअर|टीम व्यूअर|स्क्रीन शेयर|(?:ऐप|एप|एपीके).{0,20}(?:डाउनलोड|इंस्टॉल)|लिंक (?:पर|पे) क्लिक",
        "ಎನಿಡೆಸ್ಕ್|ಎನಿ ಡೆಸ್ಕ್|ಟೀಮ್ ?ವ್ಯೂವರ್|ಸ್ಕ್ರೀನ್ ಶೇರ್|(?:ಆಪ್|ಆ್ಯಪ್|ಎಪಿಕೆ).{0,20}(?:ಡೌನ್[‌ ]?ಲೋಡ್|ಇನ್[‌ ]?ಸ್ಟಾಲ್)|ಲಿಂಕ್.{0,10}ಕ್ಲಿಕ್",
        r"remote (?:access|desktop|support|control)|access (?:to )?your (?:computer|laptop|phone|mobile|device|screen|system)|screen ?sharing|"
        r"(?:install|download)\w* .{0,30}(?:app|application|software|tool|apk)|(?:click|open)\w* (?:on )?(?:the |this |that )?link",
        "रिमोट|(?:इंस्टॉल|डाउनलोड).{0,30}(?:ऐप|एप|सॉफ्टवेयर)|लिंक.{0,20}(?:खोल|क्लिक)",
        "ರಿಮೋಟ್|(?:ಇನ್[‌ ]?ಸ್ಟಾಲ್|ಡೌನ್[‌ ]?ಲೋಡ್).{0,30}(?:ಆ್ಯಪ್|ಆಪ್|ಸಾಫ್ಟ್‌ವೇರ್)|ಲಿಂಕ್.{0,20}(?:ಒತ್ತಿ|ತೆರೆ)",
        r"log ?in (?:to|on|through|via) .{0,25}(?:portal|link|website|site)|send (?:you )?(?:a |the |this )?link|link .{0,15}(?:sms|whatsapp)",
        "लिंक (?:भेज|भेजा)",
        "ಲಿಂಕ್ ಕಳುಹಿಸ",
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
        r"re-?kyc|(?:update|verify|link)\w* (?:your )?(?:aadhaar|pan|kyc|details|account)|(?:aadhaar|pan) .{0,20}(?:update|verif|link|mismatch)\w*|"
        r"mismatch|re-?verification|verification (?:pending|required|incomplete)",
        "(?:आधार|पैन).{0,20}(?:अपडेट|वेरिफ|लिंक)|सत्यापन|री-?वेरिफिकेशन",
        "ಪರಿಶೀಲನೆ|ನವೀಕರಣ|(?:ಆಧಾರ್|ಪ್ಯಾನ್).{0,20}(?:ಅಪ್ಡೇಟ್|ಲಿಂಕ್)",
    ]),
    Signal("utility", 20, "Threatens to cut your electricity", [
        r"(?:bijli|electricity|light|power) .{0,25}(?:cut|kaat|kat|band|disconnect)\w*|bill.{0,15}(?:pending|baki|update)",
        "(?:बिजली|लाइट|इलेक्ट्रिसिटी).{0,25}(?:कट|काट|बंद)|बिल.{0,15}(?:बकाया|पेंडिंग|अपडेट)",
        "(?:ವಿದ್ಯುತ್|ಕರೆಂಟ್|ಲೈಟ್).{0,25}(?:ಕಟ್|ಕಡಿತ|ಸ್ಥಗಿತ)|ಬಿಲ್.{0,15}(?:ಬಾಕಿ|ಪೆಂಡಿಂಗ್|ಅಪ್ಡೇಟ್)",
        r"electricity (?:bill|connection|supply|department|board)|power (?:connection|supply)|"
        r"(?:connection|supply|meter) .{0,20}(?:cut|disconnect|band|kaat)\w*|bill (?:is )?(?:pending|overdue|unpaid|not updated)|"
        r"gas (?:connection|subsidy)|bijli (?:vibhag|ka bill|connection)",
        "बिजली (?:विभाग|बिल|कनेक्शन|कंपनी)|कनेक्शन.{0,25}(?:काट|कट|बंद)|गैस (?:कनेक्शन|सब्सिडी)",
        "ವಿದ್ಯುತ್|ಬೆಸ್ಕಾಂ|ಕರೆಂಟ್ ಬಿಲ್|ಸಂಪರ್ಕ.{0,20}(?:ಕಡಿತ|ಕಟ್)",
        r"subsidy (?:has been |is )?(?:blocked|stopped|suspended)|lpg|gas agency|broadband|router|network (?:outage|issue|upgrade)|"
        r"maintenance outage|service (?:interruption|disruption)",
    ]),
    Signal("bait", 20, "Lottery prize or 'money sent by mistake' story", [
        r"galti se.{0,20}(?:paise|transfer|bhej)\w*|wrong(?:ly)? (?:transfer|sent)|lottery|prize|jackpot|kbc|"
        r"inaam|(?:wapas|return).{0,10}(?:kar do|kijiye|bhej)\w*",
        "गलती से.{0,20}(?:पैसे|ट्रांसफर|भेज)|लॉटरी|इनाम|ईनाम|केबीसी|कौन बनेगा करोड़पति|(?:वापस|रिटर्न).{0,10}(?:कर दो|कर दीजिए|भेज)",
        "ತಪ್ಪಾಗಿ.{0,20}(?:ಹಣ|ಕಳುಹಿಸ|ಟ್ರಾನ್ಸ್)|ಲಾಟರಿ|ಬಹುಮಾನ|ಕೆಬಿಸಿ|ವಾಪಸ್.{0,10}(?:ಕಳುಹಿಸಿ|ಹಾಕಿ)",
        r"you(?:'ve| have)? won|winner|lucky (?:draw|winner|customer)|selected (?:for|as)|"
        r"free (?:gift|voucher|holiday|trip|iphone|phone|tour)|reward points?|vouchers?|cash ?prize|bumper|congratulations|mubarak ho|"
        r"sent (?:by mistake|wrongly)|wrong transfer",
        "बधाई|विजेता|लकी ड्रा|मुफ्त (?:गिफ्ट|वाउचर|यात्रा)|रिवॉर्ड",
        "ಅಭಿನಂದನೆ|ಗೆದ್ದಿದ್ದೀರಿ|ವಿಜೇತ|ಲಕ್ಕಿ ಡ್ರಾ|ಉಚಿತ (?:ಉಡುಗೊರೆ|ಪ್ರವಾಸ)|ರಿವಾರ್ಡ್",
        r"special (?:offer|discount)|exclusive (?:offer|deal)",
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
        r"(?:your|aapka|aapki|aapke) (?:son|daughter|husband|wife|beta|beti|bete|father|mother|brother|sister).{0,40}"
        r"(?:accident|hospital|arrest\w*|police|custody|caught|trouble|kidnap\w*)|kidnap\w*|ransom",
        "अपहरण|फिरौती",
        "ಅಪಹರಣ",
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
        r"enter (?:your )?(?:upi )?pin.{0,40}(?:receive|get|credit|refund)\w*|(?:receive|get|refund|credit)\w* .{0,40}(?:enter|daal|dal)\w* (?:your )?(?:upi )?pin",
    ]),
    Signal("job", 20, "Offers easy money for online tasks or a part-time job", [
        r"part[ -]?time (?:job|kaam|work)|ghar (?:baithe|se) (?:kamai\w*|kamaye|kaam|paise)|work from home|"
        r"(?:like|review|rating)\w* .{0,30}(?:paise|rupaye|rupees|kamai|kama)\w*|task\w*|telegram group|daily (?:earning|income)",
        "पार्ट टाइम (?:जॉब|नौकरी|काम)|घर बैठे (?:कमा|काम|पैसे)|(?:लाइक|रिव्यू|रेटिंग).{0,30}(?:पैसे|रुपये|कमा)|टास्क|टेलीग्राम ग्रुप",
        "ಪಾರ್ಟ್ ಟೈಮ್ (?:ಜಾಬ್|ಕೆಲಸ)|ಮನೆಯಲ್ಲೇ.{0,20}(?:ಕೆಲಸ|ಹಣ|ಸಂಪಾದ)|ಲೈಕ್.{0,30}(?:ಹಣ|ರೂಪಾಯಿ|ಸಂಪಾದ)|ಟಾಸ್ಕ್|ಟೆಲಿಗ್ರಾಮ್ ಗ್ರೂಪ್",
        r"data entry|easy money|earn (?:rs|rupees|up to|daily|per|\d+)|per (?:task|like|review|day|hour)|"
        r"vacancy|job offer|offer letter|selected for (?:the )?job|(?:joining|training) kit",
        "नौकरी|जॉब|ऑफर लेटर|डाटा एंट्री|वैकेंसी",
        "ಉದ್ಯೋಗ|ಜಾಬ್|ಆಫರ್ ಲೆಟರ್|ಡೇಟಾ ಎಂಟ್ರಿ",
    ]),
    Signal("investment", 20, "Promises guaranteed returns or doubled money", [
        r"guarante\w* .{0,30}(?:return|profit|income)\w*|(?:paisa|paise|money|amount) .{0,20}double|"
        r"double (?:ho jayega|kar denge|return)|trading (?:app|group|tips)|stock tips?|vip group|crypto\w*|ipo allotment",
        "गारंटीड.{0,30}(?:रिटर्न|प्रॉफिट|मुनाफा|मुनाफ़ा)|(?:पैसा|पैसे) डबल|डबल हो जाएगा|ट्रेडिंग (?:ऐप|ग्रुप)|स्टॉक टिप्स|वीआईपी ग्रुप|क्रिप्टो",
        "ಗ್ಯಾರಂಟಿ.{0,30}(?:ರಿಟರ್ನ್|ಲಾಭ)|ಹಣ ಡಬಲ್|ಡಬಲ್ ಆಗುತ್ತ|ಟ್ರೇಡಿಂಗ್ (?:ಆಪ್|ಆ್ಯಪ್|ಗ್ರೂಪ್)|ಸ್ಟಾಕ್ ಟಿಪ್ಸ್|ಕ್ರಿಪ್ಟೋ",
        r"(?:\d+|ten|twenty|thirty|forty|fifty) ?(?:%|percent|per cent) .{0,20}(?:returns?|profit|monthly|guaranteed)|guaranteed (?:returns?|profit|income)|"
        r"double your money|stock market|share market|trading (?:platform|account)|bitcoin|forex|high returns?|risk[- ]free",
        "शेयर (?:बाजार|बाज़ार|मार्केट)|निवेश|मुनाफा (?:पक्का|गारंटी)|प्रतिशत (?:रिटर्न|मुनाफा|लाभ)|डबल (?:हो|कर|मिल)",
        "ಷೇರು|ಹೂಡಿಕೆ|ಲಾಭ ಖಚಿತ|ಖಚಿತ ಲಾಭ|ಶೇಕಡಾ.{0,10}ಲಾಭ|ಟ್ರೇಡಿಂಗ್",
    ]),
    Signal("customer_care", 15, "Says they are customer care, refunds or cashback", [
        r"customer (?:care|support|service)|helpline|refund\w*|cashback|complaint number",
        "कस्टमर (?:केयर|सपोर्ट|सर्विस)|रिफंड|कैशबैक|हेल्पलाइन",
        "ಕಸ್ಟಮರ್ (?:ಕೇರ್|ಸಪೋರ್ಟ್)|ರಿಫಂಡ್|ಕ್ಯಾಶ್‌?ಬ್ಯಾಕ್|ಹೆಲ್ಪ್‌?ಲೈನ್",
    ]),
    # ---- added Nov 9 (v2): stories common in ICFD-31k's development split ----
    Signal("personal_account", 30, "Asks you to pay into a personal UPI, wallet or account ID", [
        r"(?:pay|transfer|send|bhej)\w* .{0,30}(?:to |into |in |pe |par )?my (?:personal )?.{0,20}(?:id|wallet|account)|"
        r"(?:my|meri|mera|personal) .{0,15}(?:wallet|upi|pay) ?id|wallet id|"
        r"(?:give|provide|share|send)\w* (?:you )?(?:my|the) .{0,15}(?:wallet|upi|pay) ?id",
        "(?:मेरे|मेरी|पर्सनल).{0,20}(?:वॉलेट|यूपीआई|खाते|अकाउंट)(?: आईडी)?.{0,20}(?:में|पर|पे)",
        "(?:ನನ್ನ|ವೈಯಕ್ತಿಕ).{0,20}(?:ವಾಲೆಟ್|ಯುಪಿಐ|ಖಾತೆ)",
    ]),
    Signal("tech_support", 15, "Says your device or account is hacked or infected", [
        r"virus|malware|hack(?:ed|er|ing)|compromised|suspicious (?:activity|transaction|login)|unauthori[sz]ed (?:transaction|access|login)|"
        r"(?:technical|tech) support|microsoft|windows (?:support|licen[cs]e)|ip address|"
        r"(?:computer|laptop|system|device|phone) (?:is |has been )?(?:locked|infected|hacked)",
        "वायरस|हैक|संदिग्ध (?:लेनदेन|गतिविधि|ट्रांजैक्शन)|अनधिकृत",
        "ವೈರಸ್|ಹ್ಯಾಕ್|ಅನುಮಾನಾಸ್ಪದ",
    ]),
    Signal("loan", 15, "Offers a loan or a higher credit limit", [
        r"loan (?:approved|sanctioned|offer|app)|pre-?approved|instant loan|loan .{0,20}(?:approve|sanction|disburse)\w*|"
        r"emi (?:overdue|pending|bounce)|credit (?:limit|score) (?:increase|upgrade|badh)\w*|limit (?:increase|upgrade|badha)\w*",
        "लोन|ऋण|लिमिट (?:बढ़|बढ)",
        "ಸಾಲ|ಲೋನ್|ಲಿಮಿಟ್",
        r"loan .{0,25}(?:overdue|in your name)|overdue|settle(?:ment)? (?:the |this |your )?(?:loan|amount|dues)|cibil|credit score",
        "सिबिल|बकाया (?:लोन|किस्त)",
        "ಸಿಬಿಲ್",
    ]),
    Signal("insurance", 15, "Talks about an insurance policy, bonus or claim", [
        r"insurance (?:policy|claim|bonus|card)|policy (?:lapse\w*|bonus|maturity|renewal)|health card|maturity (?:amount|bonus)|irda\w*",
        "बीमा|पॉलिसी",
        "ವಿಮೆ|ಪಾಲಿಸಿ|ಇನ್ಶೂರೆನ್ಸ್",
        r"health policy|medical test|hospital bill|billing department|post-treatment",
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
    # v2 (Nov 9)
    r"(?:never|do not|don'?t|no need to|not required to) (?:share|tell|give|disclose)\w* .{0,25}(?:otp|pin|password|cvv|card)|we (?:will )?never ask|bank never asks",
    "(?:बताने|शेयर करने|देने) की (?:ज़रूरत|जरूरत) नहीं",
    "ಹೇಳಬೇಕಾಗಿಲ್ಲ|ಹಂಚಿಕೊಳ್ಳಬೇಡಿ|ಕೇಳುವುದಿಲ್ಲ",
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

    # added Nov 9 (v2)
    ({"loan", "payment"}, 15),          # "pay a processing fee to release your loan"
    ({"customer_care", "payment"}, 15),  # "pay a small charge to get your refund"
    ({"tech_support", "remote"}, 10),   # "your computer has a virus, install this"
]

# v2 (Nov 9): the shape of almost every phone scam is a STORY (who they claim
# to be, what happened), PRESSURE (threats, urgency, secrecy) and a REQUEST
# (money, a secret code, an app, a QR). A request on its own can be innocent;
# a request that comes with a story or with pressure is what scams look like.
# These bonuses apply once each, whatever the particular words were.
STORY = {"authority", "parcel", "kyc", "utility", "bait", "emergency", "job", "investment",
         "customer_care", "tech_support", "loan", "insurance", "digital_arrest"}
PRESSURE = {"threat", "urgency", "secrecy"}
REQUEST = {"payment", "credential", "remote", "upi_receive", "personal_account"}
SHAPE_BONUS = {"request+story": 25, "request+pressure": 10, "two requests": 15}

for _s in SIGNALS + [PROTECTIVE]:
    _s.compiled = [_compile(p) for p in _s.patterns]

# Words for Prisma word boosting: single words, letters only (Gnani rule).
BOOST_WORDS = {
    "hi": ["सीबीआई", "ओटीपी", "केवाईसी", "पुलिस", "पार्सल", "अरेस्ट", "वारंट", "कस्टम्स", "एनीडेस्क", "फेडेक्स", "आरबीआई", "क्यूआर", "यूपीआई", "रिफंड", "टेलीग्राम"],
    "kn": ["ಸಿಬಿಐ", "ಆರ್ಬಿಐ", "ಒಟಿಪಿ", "ಕೆವೈಸಿ", "ಪೊಲೀಸ್", "ಪಾರ್ಸೆಲ್", "ಅರೆಸ್ಟ್", "ವಾರಂಟ್", "ಕಸ್ಟಮ್ಸ್", "ಎನಿಡೆಸ್ಕ್", "ಕ್ಯೂಆರ್", "ಯುಪಿಐ", "ರಿಫಂಡ್"],
    "en": ["CBI", "OTP", "KYC", "police", "parcel", "arrest", "warrant", "customs", "AnyDesk", "FedEx", "RBI", "QR", "UPI", "refund", "Telegram"],
}
