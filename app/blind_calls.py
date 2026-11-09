"""Blind held-out test calls (set 2), written Nov 9.

Written by a separate AI agent that was told the call format and the list of
scam-type names, and was not allowed to see Kavach's rules, its demo calls or
the first held-out set. 30 calls: 5 scams and 5 genuine calls in each of
Hindi, Hinglish and Kannada, most genuine calls built to look alarming.

The detector's rules were frozen (lexicon v2) BEFORE these calls were run or
read. Do not tune on them. If they are ever used for tuning, say so and
write a new blind set.

Why a second held-out set: after the first one (unseen_calls.py) exposed the
rules' weak spots, the v2 rules were written knowing those misses, so the
first set is no longer a fair test. This one is.
"""

BLIND = {
    # ---------------- hi-IN : scams ----------------
    ("hi-IN", "b_customs_cbi"): {"expected": "digital_arrest", "short": "Customs/CBI", "lines": [
        "नमस्कार, मैं मुंबई कस्टम्स विभाग से इंस्पेक्टर बोल रहा हूँ।",
        "आपके आधार कार्ड से जुड़ा एक पार्सल विदेश भेजा जा रहा था, उसमें पाँच पासपोर्ट और नशीले पदार्थ मिले हैं।",
        "यह मामला अब सीबीआई को सौंप दिया गया है और आपके नाम पर गिरफ़्तारी वारंट जारी हो चुका है।",
        "आप अभी स्काइप पर वीडियो कॉल से जुड़िए और जाँच पूरी होने तक कमरे से बाहर मत जाइए, किसी को कुछ मत बताइए।",
        "आपके पैसे की जाँच के लिए पूरी जमा राशि हमारे बताए गए सरकारी खाते में ट्रांसफ़र करनी होगी, जाँच के बाद वापस कर दी जाएगी।",
    ]},
    ("hi-IN", "b_bijli_cut"): {"expected": "utility", "short": "Bijli cut", "lines": [
        "प्रिय उपभोक्ता, मैं बिजली विभाग के बिलिंग ऑफ़िस से बात कर रहा हूँ।",
        "आपका पिछले महीने का बिल सिस्टम में अपडेट नहीं हुआ है, इसलिए आज रात साढ़े नौ बजे आपकी बिजली काट दी जाएगी।",
        "अगर कनेक्शन चालू रखना है तो अभी हमारे भेजे हुए लिंक से दस रुपये का भुगतान करके अपडेट कर दीजिए।",
        "लिंक न खुले तो मैं आपको एक सपोर्ट ऐप का नाम बताता हूँ, उसे डाउनलोड कर लीजिए, मैं ख़ुद अपडेट कर दूँगा।",
    ]},
    ("hi-IN", "b_kbc_lottery"): {"expected": "bait", "short": "KBC lottery", "lines": [
        "बधाई हो जी, आपका मोबाइल नंबर कौन बनेगा करोड़पति के लकी ड्रॉ में चुना गया है।",
        "आपके नाम पच्चीस लाख रुपये की इनामी राशि निकली है, मैं मुंबई ऑफ़िस से मैनेजर बोल रहा हूँ।",
        "यह रक़म आपके खाते में डालने से पहले बारह हज़ार पाँच सौ रुपये का जीएसटी और प्रोसेसिंग चार्ज जमा करना होगा।",
        "यह बात अभी घर में किसी को मत बताइए, वरना आपका इनाम रद्द हो सकता है।",
    ]},
    ("hi-IN", "b_beta_thane"): {"expected": "emergency", "short": "Son arrested", "lines": [
        "हैलो, मैं थाने से हेड कांस्टेबल बोल रहा हूँ, आपका बेटा इस वक़्त हमारे पास है।",
        "कॉलेज के तीन लड़कों के साथ मारपीट के एक केस में पकड़ा गया है, बहुत रो रहा है बेचारा।",
        "अगर एफ़आईआर दर्ज हो गई तो उसका पूरा करियर ख़राब हो जाएगा, साहब मामला यहीं निपटाने को तैयार हैं।",
        "अभी तुरंत पचास हज़ार रुपये इसी नंबर पर फ़ोन पे कर दीजिए, और घर में किसी और को फ़ोन मत कीजिए।",
    ]},
    ("hi-IN", "b_share_tips"): {"expected": "investment", "short": "Stock tips", "lines": [
        "नमस्ते सर, मैं एक सेबी रजिस्टर्ड एडवाइज़री फ़र्म से रिलेशनशिप मैनेजर बात कर रही हूँ।",
        "हमारे वीआईपी ग्रुप के सदस्य पिछले महीने हर ट्रेड में तीस से चालीस प्रतिशत मुनाफ़ा कमा रहे हैं।",
        "आपको बस हमारा ट्रेडिंग ऐप इंस्टॉल करना है और शुरुआत में सिर्फ़ दस हज़ार रुपये लगाने हैं, बाक़ी हमारे एक्सपर्ट संभाल लेंगे।",
        "यह ऑफ़र सिर्फ़ आज रात तक है, कल से न्यूनतम निवेश एक लाख रुपये हो जाएगा।",
    ]},
    # ---------------- hi-IN : genuine ----------------
    ("hi-IN", "b_ok_bank_alert"): {"expected": None, "short": "Bank alert ✓", "lines": [
        "नमस्ते, मैं आपके बैंक की फ़्रॉड मॉनिटरिंग टीम से बोल रही हूँ।",
        "आपके क्रेडिट कार्ड से कुछ देर पहले एक ऑनलाइन शॉपिंग साइट पर अठारह हज़ार रुपये का लेन-देन करने की कोशिश हुई है।",
        "क्या यह ख़रीदारी आपने ख़ुद की है? बस हाँ या ना में बता दीजिए।",
        "कृपया ध्यान दें, बैंक कभी भी आपसे ओटीपी, पिन या कार्ड का पूरा नंबर नहीं पूछता, इसलिए वह किसी को मत बताइए।",
        "अगर यह आपने नहीं किया है तो हम कार्ड को अस्थायी रूप से रोक देंगे, और आप कार्ड के पीछे लिखे नंबर पर भी हमें कॉल कर सकते हैं।",
    ]},
    ("hi-IN", "b_ok_delivery"): {"expected": None, "short": "Delivery ✓", "lines": [
        "हैलो मैडम, मैं आपके ऑर्डर की डिलीवरी लेकर आया हूँ, आपकी गली के बाहर खड़ा हूँ।",
        "यहाँ दो-तीन बिल्डिंग एक जैसी दिख रही हैं, आपका मकान मंदिर वाली साइड है या पार्क वाली?",
        "कैश ऑन डिलीवरी है, चार सौ अस्सी रुपये बनते हैं, छुट्टे रख लीजिएगा।",
        "मैं पाँच मिनट में पहुँच रहा हूँ, कोई नीचे आ जाए तो अच्छा रहेगा।",
    ]},
    ("hi-IN", "b_ok_doctor_report"): {"expected": None, "short": "Doctor ✓", "lines": [
        "नमस्ते, मैं सिटी हॉस्पिटल में डॉक्टर साहब की क्लिनिक से बोल रही हूँ।",
        "आपके पिताजी की ब्लड रिपोर्ट आ गई है, शुगर थोड़ी बढ़ी हुई है, लेकिन घबराने वाली कोई बात नहीं है।",
        "डॉक्टर साहब ने कहा है कि गुरुवार सुबह दस बजे उन्हें एक बार दिखा दीजिए, दवा बदलनी पड़ सकती है।",
        "आते समय पुरानी फ़ाइल और दवाइयों की पर्ची साथ ले आइएगा।",
    ]},
    ("hi-IN", "b_ok_kiraya"): {"expected": None, "short": "Son rent ✓", "lines": [
        "हैलो मम्मी, मैं बोल रहा हूँ, सब ठीक है, आपने खाना खा लिया?",
        "इस बार मकान मालिक ने किराया पाँच सौ रुपये बढ़ा दिया है, और मेरी सैलरी इस महीने दस तारीख़ को आएगी।",
        "अगर आप पापा से कहकर आठ हज़ार रुपये मेरे खाते में डलवा दें तो मैं अगले महीने लौटा दूँगा।",
        "कोई जल्दी नहीं है, कल शाम तक भी चलेगा, और मैं रविवार को वीडियो कॉल करता हूँ।",
    ]},
    ("hi-IN", "b_ok_bijli_kaam"): {"expected": None, "short": "Power work ✓", "lines": [
        "नमस्कार, मैं बिजली विभाग के स्थानीय सब-स्टेशन से लाइनमैन बोल रहा हूँ।",
        "कल सुबह दस बजे से दोपहर दो बजे तक आपके इलाक़े में ट्रांसफ़ॉर्मर की मरम्मत का काम होगा, इस दौरान बिजली बंद रहेगी।",
        "पानी की टंकी पहले से भर लीजिए और ज़रूरी चीज़ें चार्ज कर लीजिए।",
        "आपको कुछ भी भुगतान नहीं करना है, यह सिर्फ़ सूचना देने के लिए कॉल है।",
    ]},
    # ---------------- en-IN (Hinglish) : scams ----------------
    ("en-IN", "b_card_limit"): {"expected": "credential", "short": "Card limit", "lines": [
        "Good afternoon sir, main aapke credit card department se bol rahi hoon.",
        "Aapke card pe pre-approved limit enhancement aaya hai, do lakh se badhkar paanch lakh, bilkul free of charge.",
        "Bas verification ke liye aapke registered mobile pe ek code aayega, woh mujhe bata dijiye toh main abhi activate kar deti hoon.",
        "Aur card ke peeche jo teen digit ka number hai, woh bhi confirm kar dijiye sir, system mein match karna hai.",
        "Yeh offer sirf aaj valid hai, kal se poora process dobara karna padega.",
    ]},
    ("en-IN", "b_army_olx"): {"expected": "upi_receive", "short": "OLX army QR", "lines": [
        "Hello, main aapka OLX pe sofa ka ad dekh ke call kar raha hoon, main army mein hoon, abhi abhi transfer hua hai.",
        "Price ka koi issue nahi hai, jo aapne likha hai woh full de dunga, pickup ke liye apni gaadi bhejunga.",
        "Army ka payment system thoda alag hota hai, main aapko WhatsApp pe ek QR code bhej raha hoon.",
        "Usko scan karke apna UPI PIN daal dena, paisa seedha aapke account mein aa jayega.",
        "Pehle main ek rupaya bhejta hoon test ke liye, phir full amount.",
    ]},
    ("en-IN", "b_kyc_app"): {"expected": "kyc", "short": "KYC app", "lines": [
        "Sir namaste, main aapke bank ki KYC cell se bol raha hoon, aapka KYC expire ho gaya hai.",
        "Agar aaj shaam paanch baje tak update nahi hua toh aapki net banking aur debit card dono band ho jayenge.",
        "Aapko branch jaane ki zaroorat nahi hai, main ek SMS bhej raha hoon, usme link pe click karke ek app install kar lijiye.",
        "Usme apna customer ID, password aur Aadhaar daal dijiye, bas do minute ka kaam hai.",
    ]},
    ("en-IN", "b_task_job"): {"expected": "job", "short": "Task job", "lines": [
        "Hi, main ek digital marketing company ki HR team se bol rahi hoon, aapka resume humein job portal se mila.",
        "Hum part-time work from home de rahe hain, bas YouTube videos like karne hain aur screenshot bhejna hai, har task ke pachaas rupaye.",
        "Pehle din teen task free hain, uske baad aapko Telegram group mein add karenge jahan prepaid task milte hain.",
        "Prepaid task mein pehle ek hazaar rupaye dalne hote hain, aur turant teen hazaar wapas milte hain, sab log kar rahe hain.",
    ]},
    ("en-IN", "b_refund_care"): {"expected": "customer_care", "short": "Refund care", "lines": [
        "Hello ma'am, main aapke shopping app ke customer care se bol raha hoon, aapne jo return request daali thi uske baare mein.",
        "Aapka refund ek technical issue ki wajah se fail ho gaya hai, isliye hum manually process kar rahe hain.",
        "Main aapko ek payment request bhejta hoon, aap usme apna UPI PIN daal dena, toh refund turant credit ho jayega.",
        "Aur please call cut mat kijiye, warna refund ticket close ho jayega.",
    ]},
    # ---------------- en-IN (Hinglish) : genuine ----------------
    ("en-IN", "b_ok_policy_renew"): {"expected": None, "short": "Policy renew ✓", "lines": [
        "Hello sir, main aapki health insurance company se policy renewal reminder ke liye call kar rahi hoon.",
        "Aapki family floater policy agle mahine ki pandrah tarikh ko expire ho rahi hai.",
        "Aap renewal hamari official app se ya nearest branch pe jaake khud kar sakte hain, premium amount app mein dikh jayega.",
        "Main aapse koi payment ya card details nahi le rahi, yeh sirf ek reminder call hai.",
    ]},
    ("en-IN", "b_ok_school_fee"): {"expected": None, "short": "School fee ✓", "lines": [
        "Namaste, main school office se bol rahi hoon, aapke bete ki class teacher ne call karne ko bola tha.",
        "Second term ki fees ki last date is Friday hai, abhi tak hamare record mein payment show nahi ho raha.",
        "Aap school ke parent portal se ya office counter pe aakar pay kar sakte hain, receipt wahin mil jayegi.",
        "Agar aapne already bhar diya hai toh bas receipt ki photo class teacher ko bhej dijiye, hum update kar denge.",
    ]},
    ("en-IN", "b_ok_passport_police"): {"expected": None, "short": "Passport ✓", "lines": [
        "Namaste, main local police station se bol raha hoon, aapke passport application ki verification ke liye.",
        "Main kal subah gyarah baje ke aas paas aapke ghar aaunga, aap ghar pe hi rahiyega.",
        "Apna Aadhaar ka original, address proof, aur do padosiyon ke naam jo aapko jaante hon, ready rakhiyega.",
        "Iske liye koi fees nahi lagti, kisi ko bhi paise mat dijiyega.",
    ]},
    ("en-IN", "b_ok_broadband_callback"): {"expected": None, "short": "Complaint ✓", "lines": [
        "Hello sir, main aapke broadband provider ki customer support team se call kar raha hoon.",
        "Aapne kal internet slow hone ki complaint register ki thi, uske regarding follow-up hai.",
        "Humne line check kar li hai, area mein fiber cut tha, ab theek ho gaya hai.",
        "Kya ab aapki speed theek aa rahi hai? Agar abhi bhi problem hai toh main technician visit schedule kar deta hoon, koi charge nahi lagega.",
    ]},
    ("en-IN", "b_ok_mausi_health"): {"expected": None, "short": "Aunt call ✓", "lines": [
        "Hello beta, main bol rahi hoon, kaise ho? Bahut din se tumne phone nahi kiya.",
        "Tumhari tabiyat ab kaisi hai, woh fever utra ki nahi? Doctor ko dikhaya tha?",
        "Dawai time pe lena aur thoda garam paani peete rehna, kuch din bahar ka khana band karo.",
        "Aur Diwali pe ghar aa rahe ho na, sab tumhara intezaar kar rahe hain.",
    ]},
    # ---------------- kn-IN : scams ----------------
    ("kn-IN", "b_courier_drugs"): {"expected": "parcel", "short": "Courier drugs", "lines": [
        "ನಮಸ್ಕಾರ, ನಾನು ಫೆಡ್‌ಎಕ್ಸ್ ಕೊರಿಯರ್ ಕಸ್ಟಮರ್ ಸರ್ವೀಸ್‌ನಿಂದ ಮಾತಾಡ್ತಿದ್ದೀನಿ.",
        "ನಿಮ್ಮ ಹೆಸರಲ್ಲಿ ಮುಂಬೈನಿಂದ ಥೈಲ್ಯಾಂಡ್‌ಗೆ ಹೋಗ್ತಿದ್ದ ಒಂದು ಪಾರ್ಸಲ್‌ನ ಕಸ್ಟಮ್ಸ್‌ನವರು ಹಿಡಿದಿದ್ದಾರೆ, ಅದರಲ್ಲಿ ಡ್ರಗ್ಸ್ ಸಿಕ್ಕಿದೆ.",
        "ನೀವು ಕಳಿಸಿಲ್ಲ ಅಂದ್ರೆ ಈಗಲೇ ಮುಂಬೈ ಸೈಬರ್ ಪೊಲೀಸ್‌ಗೆ ಕಾಲ್ ಕನೆಕ್ಟ್ ಮಾಡ್ತೀನಿ, ಅವರಿಗೆ ಸ್ಟೇಟ್‌ಮೆಂಟ್ ಕೊಡಬೇಕು.",
        "ನಿಮ್ಮ ಆಧಾರ್ ಮಿಸ್‌ಯೂಸ್ ಆಗಿದೆಯಾ ಅಂತ ಚೆಕ್ ಮಾಡೋಕೆ ಒಂದು ಸಣ್ಣ ಕ್ಲಿಯರೆನ್ಸ್ ಫೀ ಕಟ್ಟಬೇಕಾಗುತ್ತೆ, ಇಲ್ಲಾಂದ್ರೆ ಕೇಸ್ ನಿಮ್ಮ ಮೇಲೆ ಆಗುತ್ತೆ.",
        "ಈ ವಿಷಯ ಮನೆಯವರಿಗೆ ಯಾರಿಗೂ ಹೇಳ್ಬೇಡಿ, ಇದು ಕಾನ್ಫಿಡೆನ್ಷಿಯಲ್ ಇನ್ವೆಸ್ಟಿಗೇಷನ್.",
    ]},
    ("kn-IN", "b_screen_share"): {"expected": "remote", "short": "AnyDesk", "lines": [
        "ಸಾರ್, ನಾನು ನಿಮ್ಮ ಬ್ಯಾಂಕ್‌ನ ಟೆಕ್ನಿಕಲ್ ಸಪೋರ್ಟ್ ಟೀಮ್‌ನಿಂದ ಕಾಲ್ ಮಾಡ್ತಿದ್ದೀನಿ.",
        "ನಿಮ್ಮ ಮೊಬೈಲ್ ಬ್ಯಾಂಕಿಂಗ್ ಆಪ್‌ನಲ್ಲಿ ಸೆಕ್ಯುರಿಟಿ ಅಪ್‌ಡೇಟ್ ಪೆಂಡಿಂಗ್ ಇದೆ, ಅದಕ್ಕೆ ನಿಮ್ಮ ಟ್ರಾನ್ಸಾಕ್ಷನ್ ಎಲ್ಲಾ ಹೋಲ್ಡ್‌ನಲ್ಲಿ ಇವೆ.",
        "ಪ್ಲೇ ಸ್ಟೋರ್‌ಗೆ ಹೋಗಿ ಎನಿಡೆಸ್ಕ್ ಅಂತ ಒಂದು ಆಪ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ, ಅದರಲ್ಲಿ ಬರೋ ಒಂಬತ್ತು ಅಂಕಿಯ ಕೋಡ್ ನನಗೆ ಹೇಳಿ.",
        "ನಾನೇ ನಿಮ್ಮ ಫೋನ್‌ನಲ್ಲಿ ಅಪ್‌ಡೇಟ್ ಮಾಡಿ ಕೊಡ್ತೀನಿ, ನೀವು ಏನೂ ಮಾಡಬೇಕಾಗಿಲ್ಲ, ಸ್ಕ್ರೀನ್ ಆನ್ ಇಟ್ಕೊಳ್ಳಿ ಸಾಕು.",
    ]},
    ("kn-IN", "b_tappu_transfer"): {"expected": "bait", "short": "Sent by error", "lines": [
        "ಹಲೋ ಅಕ್ಕ, ಕ್ಷಮಿಸಿ ತೊಂದರೆ ಕೊಡ್ತಿದ್ದೀನಿ, ನನ್ನ ಅಣ್ಣನಿಗೆ ಹಣ ಕಳಿಸೋಕೆ ಹೋಗಿ ತಪ್ಪಾಗಿ ನಿಮ್ಮ ನಂಬರ್‌ಗೆ ಐದು ಸಾವಿರ ರೂಪಾಯಿ ಕಳಿಸಿಬಿಟ್ಟೆ.",
        "ನಿಮಗೆ ಮೆಸೇಜ್ ಬಂದಿರಬೇಕು, ಒಮ್ಮೆ ಚೆಕ್ ಮಾಡಿ ನೋಡಿ.",
        "ಅದು ನನ್ನ ಅಮ್ಮನ ಆಸ್ಪತ್ರೆ ಖರ್ಚಿಗೆ ಇಟ್ಟಿದ್ದ ದುಡ್ಡು, ದಯವಿಟ್ಟು ಈಗಲೇ ವಾಪಸ್ ಕಳಿಸಿ.",
        "ನಾನು ಒಂದು ಪೇಮೆಂಟ್ ರಿಕ್ವೆಸ್ಟ್ ಕಳಿಸ್ತೀನಿ, ಅದನ್ನ ಅಪ್ರೂವ್ ಮಾಡಿ ಪಿನ್ ಹಾಕಿದ್ರೆ ಸಾಕು.",
    ]},
    ("kn-IN", "b_loan_fee"): {"expected": "payment", "short": "Loan fee", "lines": [
        "ನಮಸ್ಕಾರ ಮೇಡಂ, ನಮ್ಮ ಫೈನಾನ್ಸ್ ಕಂಪನಿಯಿಂದ ನಿಮಗೆ ಎರಡು ಲಕ್ಷ ರೂಪಾಯಿ ಪರ್ಸನಲ್ ಲೋನ್ ಪ್ರೀ-ಅಪ್ರೂವ್ ಆಗಿದೆ.",
        "ಸಿಬಿಲ್ ಸ್ಕೋರ್ ಬೇಕಾಗಿಲ್ಲ, ಯಾವುದೇ ಡಾಕ್ಯುಮೆಂಟ್ ಬೇಕಾಗಿಲ್ಲ, ಇವತ್ತೇ ಅಕೌಂಟ್‌ಗೆ ಹಣ ಬರುತ್ತೆ.",
        "ಲೋನ್ ರಿಲೀಸ್ ಮಾಡೋಕೆ ಮುಂಚೆ ಎರಡು ಸಾವಿರದ ಐನೂರು ರೂಪಾಯಿ ಪ್ರೋಸೆಸಿಂಗ್ ಫೀ ಮತ್ತು ಇನ್ಶೂರೆನ್ಸ್ ಚಾರ್ಜ್ ಕಟ್ಟಬೇಕು.",
        "ನಾನು ವಾಟ್ಸಾಪ್‌ನಲ್ಲಿ ಕಳಿಸೋ ಯುಪಿಐ ಐಡಿಗೆ ಈಗಲೇ ಕಟ್ಟಿದ್ರೆ ಅರ್ಧ ಗಂಟೆಯಲ್ಲಿ ಲೋನ್ ಕ್ರೆಡಿಟ್ ಆಗುತ್ತೆ.",
    ]},
    ("kn-IN", "b_sim_block"): {"expected": "kyc", "short": "SIM block", "lines": [
        "ಇದು ಟೆಲಿಕಾಂ ರೆಗ್ಯುಲೇಟರಿ ಅಥಾರಿಟಿಯಿಂದ ಬಂದಿರೋ ಒಂದು ಮುಖ್ಯವಾದ ಕರೆ.",
        "ನಿಮ್ಮ ಆಧಾರ್ ಬಳಸಿ ಯಾರೋ ಇನ್ನೊಂದು ಸಿಮ್ ತೆಗೆದುಕೊಂಡಿದ್ದಾರೆ, ಅದರಿಂದ ಕಾನೂನುಬಾಹಿರ ಮೆಸೇಜ್‌ಗಳು ಹೋಗ್ತಿವೆ.",
        "ಎರಡು ಗಂಟೆಯೊಳಗೆ ನಿಮ್ಮ ಹೆಸರಲ್ಲಿರೋ ಎಲ್ಲಾ ಮೊಬೈಲ್ ನಂಬರ್‌ಗಳು ಬ್ಲಾಕ್ ಆಗುತ್ತವೆ.",
        "ಬ್ಲಾಕ್ ಆಗಬಾರದು ಅಂದ್ರೆ ಈಗಲೇ ನಮ್ಮ ಅಧಿಕಾರಿಗೆ ನಿಮ್ಮ ಆಧಾರ್ ವಿವರ ಮತ್ತು ಫೋನ್‌ಗೆ ಬರೋ ವೆರಿಫಿಕೇಷನ್ ಕೋಡ್ ಹೇಳಿ ರೀ-ವೆರಿಫೈ ಮಾಡಿಸಿಕೊಳ್ಳಿ.",
    ]},
    # ---------------- kn-IN : genuine ----------------
    ("kn-IN", "b_ok_courier_daari"): {"expected": None, "short": "Courier ✓", "lines": [
        "ಹಲೋ ಸಾರ್, ನಾನು ಕೊರಿಯರ್‌ನಿಂದ ಮಾತಾಡ್ತಿದ್ದೀನಿ, ನಿಮ್ಮ ಪಾರ್ಸಲ್ ಡೆಲಿವರಿ ಮಾಡೋಕೆ ಬಂದಿದ್ದೀನಿ.",
        "ನಿಮ್ಮ ಅಡ್ರೆಸ್‌ನಲ್ಲಿ ಕ್ರಾಸ್ ಸರಿಯಾಗಿ ಹಾಕಿಲ್ಲ, ನಾನು ಈಗ ಗಣೇಶ ದೇವಸ್ಥಾನದ ಹತ್ರ ನಿಂತಿದ್ದೀನಿ.",
        "ಇಲ್ಲಿಂದ ಎಡಕ್ಕೆ ಹೋಗಬೇಕಾ ಬಲಕ್ಕೆ ಹೋಗಬೇಕಾ ಸ್ವಲ್ಪ ಹೇಳ್ತೀರಾ?",
        "ಇದು ಪ್ರೀಪೇಯ್ಡ್ ಆರ್ಡರ್ ಸಾರ್, ಏನೂ ಕಟ್ಟಬೇಕಾಗಿಲ್ಲ, ಮನೇಲಿ ಯಾರಾದ್ರೂ ಇದ್ರೆ ಸಾಕು.",
    ]},
    ("kn-IN", "b_ok_emi_reminder"): {"expected": None, "short": "EMI remind ✓", "lines": [
        "ನಮಸ್ಕಾರ ಸಾರ್, ನಾನು ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ಶಾಖೆಯ ಹೋಮ್ ಲೋನ್ ವಿಭಾಗದಿಂದ ಕಾಲ್ ಮಾಡ್ತಿದ್ದೀನಿ.",
        "ಈ ತಿಂಗಳ ಇಎಂಐ ಐದನೇ ತಾರೀಖಿಗೆ ಡ್ಯೂ ಇದೆ, ನಿಮ್ಮ ಸೇವಿಂಗ್ಸ್ ಅಕೌಂಟ್‌ನಲ್ಲಿ ಬ್ಯಾಲೆನ್ಸ್ ಸ್ವಲ್ಪ ಕಡಿಮೆ ಇದೆ ಅಂತ ತೋರಿಸ್ತಿದೆ.",
        "ದಯವಿಟ್ಟು ನಿಮ್ಮ ನೆಟ್ ಬ್ಯಾಂಕಿಂಗ್‌ನಿಂದ ಅಥವಾ ಬ್ರಾಂಚ್‌ಗೆ ಬಂದು ಅಕೌಂಟ್‌ಗೆ ಹಣ ಹಾಕಿ, ಇಲ್ಲಾಂದ್ರೆ ಬೌನ್ಸ್ ಚಾರ್ಜ್ ಬೀಳಬಹುದು.",
        "ನಾವು ಫೋನ್‌ನಲ್ಲಿ ಯಾವುದೇ ಪಿನ್ ಅಥವಾ ಓಟಿಪಿ ಕೇಳೋದಿಲ್ಲ, ಏನಾದ್ರೂ ಸಂದೇಹ ಇದ್ರೆ ನೇರವಾಗಿ ಬ್ರಾಂಚ್‌ಗೆ ಬನ್ನಿ.",
    ]},
    ("kn-IN", "b_ok_hospital_appt"): {"expected": None, "short": "Hospital ✓", "lines": [
        "ನಮಸ್ಕಾರ, ನಾನು ಆಸ್ಪತ್ರೆಯ ಅಪಾಯಿಂಟ್‌ಮೆಂಟ್ ಡೆಸ್ಕ್‌ನಿಂದ ಮಾತಾಡ್ತಿದ್ದೀನಿ.",
        "ನಾಳೆ ಬೆಳಿಗ್ಗೆ ಹನ್ನೊಂದು ಗಂಟೆಗೆ ಕಾರ್ಡಿಯಾಲಜಿ ಡಾಕ್ಟರ್ ಹತ್ರ ನಿಮ್ಮ ತಾಯಿಯವರ ಚೆಕಪ್ ಬುಕ್ ಆಗಿದೆ, ಅದನ್ನ ಕನ್ಫರ್ಮ್ ಮಾಡೋಕೆ ಕಾಲ್ ಮಾಡಿದ್ದೀನಿ.",
        "ಇಸಿಜಿ ಮತ್ತು ಬ್ಲಡ್ ಟೆಸ್ಟ್ ಇರೋದ್ರಿಂದ ಬೆಳಿಗ್ಗೆ ತಿಂಡಿ ತಿನ್ನದೆ ಬರೋಕೆ ಹೇಳಿ.",
        "ಹಿಂದಿನ ರಿಪೋರ್ಟ್‌ಗಳು ಮತ್ತು ಇನ್ಶೂರೆನ್ಸ್ ಕಾರ್ಡ್ ತಗೊಂಡು ಬನ್ನಿ, ಪೇಮೆಂಟ್ ಬಿಲ್ಲಿಂಗ್ ಕೌಂಟರ್‌ನಲ್ಲೇ ಮಾಡಬಹುದು.",
    ]},
    ("kn-IN", "b_ok_gas_delivery"): {"expected": None, "short": "Gas cylinder ✓", "lines": [
        "ನಮಸ್ಕಾರ, ನಾನು ನಿಮ್ಮ ಗ್ಯಾಸ್ ಏಜೆನ್ಸಿಯಿಂದ ಡೆಲಿವರಿ ಹುಡುಗ ಮಾತಾಡ್ತಿದ್ದೀನಿ.",
        "ನೀವು ನಿನ್ನೆ ಬುಕ್ ಮಾಡಿದ್ದ ಸಿಲಿಂಡರ್ ಇವತ್ತು ಮಧ್ಯಾಹ್ನ ಮೂರು ಗಂಟೆ ಒಳಗೆ ತರ್ತೀನಿ.",
        "ಮನೆಯಲ್ಲಿ ಯಾರಾದ್ರೂ ಇರ್ತಾರಾ? ಖಾಲಿ ಸಿಲಿಂಡರ್ ರೆಡಿ ಇಟ್ಟಿರಿ.",
        "ಬಿಲ್‌ನಲ್ಲಿ ಇರೋ ಅಷ್ಟು ಹಣ ಸಿಲಿಂಡರ್ ಕೈಗೆ ಸಿಕ್ಕಿದ ಮೇಲೆ ಕೊಟ್ರೆ ಸಾಕು.",
    ]},
    ("kn-IN", "b_ok_magalu_fees"): {"expected": None, "short": "Exam fee ✓", "lines": [
        "ಹಲೋ ಅಪ್ಪಾ, ನಾನು ಮಾತಾಡ್ತಿದ್ದೀನಿ, ಹಾಸ್ಟೆಲ್‌ನಲ್ಲಿ ಎಲ್ಲಾ ಚೆನ್ನಾಗಿದೆ.",
        "ಮುಂದಿನ ಸೆಮಿಸ್ಟರ್ ಎಕ್ಸಾಮ್ ಫೀ ಕಟ್ಟೋಕೆ ಈ ಶುಕ್ರವಾರ ಲಾಸ್ಟ್ ಡೇಟ್ ಅಂತ ಕಾಲೇಜಲ್ಲಿ ನೋಟೀಸ್ ಹಾಕಿದ್ದಾರೆ.",
        "ಮೂರು ಸಾವಿರದ ಇನ್ನೂರು ರೂಪಾಯಿ ಆಗುತ್ತೆ, ನನ್ನ ಅಕೌಂಟ್‌ಗೆ ಹಾಕಿದ್ರೆ ನಾನೇ ಕಾಲೇಜ್ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಕಟ್ತೀನಿ.",
        "ರಸೀದಿ ಬಂದ ಮೇಲೆ ನಿಮಗೆ ವಾಟ್ಸಾಪ್ ಮಾಡ್ತೀನಿ, ಅಮ್ಮನಿಗೂ ಹೇಳಿ, ಭಾನುವಾರ ಕಾಲ್ ಮಾಡ್ತೀನಿ.",
    ]},
}
