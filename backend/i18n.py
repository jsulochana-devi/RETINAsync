"""
backend/i18n.py
Internationalization module supporting English, Telugu, and Hindi for RETINAsync.
"""

TRANSLATIONS = {
    "English": {
        "app_title": "RETINAsync",
        "app_subtitle": "Explainable AI for Diabetic Retinopathy Screening in Rural India",
        "nav_home": "Home",
        "nav_registration": "Patient Registration",
        "nav_screening": "New Screening",
        "nav_ai_analysis": "AI Analysis",
        "nav_history": "Patient History",
        "nav_dashboard": "Dashboard",
        "nav_about": "About",
        "start_screening": "Start New Screening",
        "key_features": "Key Features",
        "screening_workflow": "Screening Workflow",
        "how_it_works": "How RETINAsync Operates in PHCs",
        "voice_assistant": "Voice Assistant",
        "listen_explanation": "Listen to Workflow Explanation",
        "state_wise_report": "State-Wise Screening Report",
        "patients_screened": "Patients Screened",
        "total_screenings": "Total Screenings",
        "quality_pass_rate": "Quality Pass Rate",
        "referrals_required": "Referrals Required",
        "select_state": "Filter by State",
        "logout": "Logout",
        "offline_ready": "Offline-Ready · All processing local",
        "demo_mode": "Demo Mode",
        "language": "Language",
    },
    "తెలుగు (Telugu)": {
        "app_title": "రెటీనాసింక్ (RETINAsync)",
        "app_subtitle": "గ్రామీణ భారతదేశంలో డయాబెటిక్ రెటినోపతి స్క్రీనింగ్ కోసం వివరణాత్మక AI",
        "nav_home": "హోమ్ (Home)",
        "nav_registration": "పేషెంట్ రిజిస్ట్రేషన్",
        "nav_screening": "కొత్త స్క్రీనింగ్",
        "nav_ai_analysis": "AI విశ్లేషణ",
        "nav_history": "పేషెంట్ చరిత్ర",
        "nav_dashboard": "డ్యాష్‌బోర్డ్",
        "nav_about": "గురించి (About)",
        "start_screening": "కొత్త స్క్రీనింగ్ ప్రారంభించండి",
        "key_features": "ముఖ్య లక్షణాలు",
        "screening_workflow": "స్క్రీనింగ్ నిర్వహణ క్రమము",
        "how_it_works": "PHCలలో రెటీనాసింక్ ఎలా పనిచేస్తుంది",
        "voice_assistant": "వాయిస్ అసిస్టెంట్ (Voice Assistant)",
        "listen_explanation": "పనివిధానం వివరణ వినండి",
        "state_wise_report": "రాష్ట్రాల వారీగా నివేదిక (State-wise Report)",
        "patients_screened": "పరీక్షించిన రోగులు",
        "total_screenings": "మొత్తం స్క్రీనింగ్‌లు",
        "quality_pass_rate": "నాణ్యత ఉత్తీర్ణత శాతం",
        "referrals_required": "అవసరమైన రెఫరల్స్",
        "select_state": "రాష్ట్రాన్ని ఎంచుకోండి",
        "logout": "లాగౌట్",
        "offline_ready": "ఆఫ్‌లైన్-సిద్ధంగా ఉంది · స్థానిక ప్రాసెసింగ్",
        "demo_mode": "డెమో మోడ్",
        "language": "భాష",
    },
    "హిన్దీ (Hindi)": {
        "app_title": "रेटीनासिंक (RETINAsync)",
        "app_subtitle": "ग्रामीण भारत में डायबिटिक रेटिनोपैथी जांच के लिए व्याख्या योग्य AI",
        "nav_home": "होम (Home)",
        "nav_registration": "रोगी पंजीकरण",
        "nav_screening": "नई स्क्रीनिंग",
        "nav_ai_analysis": "AI विश्लेषण",
        "nav_history": "रोगी इतिहास",
        "nav_dashboard": "डैशबोर्ड",
        "nav_about": "के बारे में (About)",
        "start_screening": "नई स्क्रीनिंग शुरू करें",
        "key_features": "प्रमुख विशेषताएं",
        "screening_workflow": "स्क्रीनिंग कार्यप्रवाह",
        "how_it_works": "PHC में RETINAsync कैसे काम करता है",
        "voice_assistant": "वॉयस असिस्टेंट (Voice Assistant)",
        "listen_explanation": "कार्यप्रवाह विवरण सुनें",
        "state_wise_report": "राज्यवार रिपोर्ट (State-wise Report)",
        "patients_screened": "जांचे गए मरीज",
        "total_screenings": "कुल स्क्रीनिंग",
        "quality_pass_rate": "गुणवत्ता पास दर",
        "referrals_required": "आवश्यक रेफरल",
        "select_state": "राज्य चुनें",
        "logout": "लॉग आउट",
        "offline_ready": "ऑफलाइन तैयार · सभी प्रोसेसिंग स्थानीय",
        "demo_mode": "डेमो मोड",
        "language": "भाषा",
    }
}

WORKFLOW_EXPLANATIONS = {
    "English": "RETINAsync works in 6 steps: Step 1, Fundus Image Capture at the local PHC. Step 2, Automatic Quality Gate checks for blur and lighting. Step 3, CLAHE image preprocessing. Step 4, AI deep neural network DR grade classification. Step 5, Grad-CAM visual heatmap generation for explainable AI. Step 6, Risk assessment and PDF report generation for tele-referral.",
    "తెలుగు (Telugu)": "రెటీనాసింక్ 6 దశల్లో పనిచేస్తుంది: 1వ దశ, PHC వద్ద కంటి ఫండ్స్ ఫోటో క్యాప్చర్. 2వ దశ, ఇమేజ్ క్వాలిటీ మరియు స్పష్టత తనిఖీ. 3వ దశ, ఇమేజ్ ప్రోసెసింగ్. 4వ దశ, AI మోడల్ ద్వారా వ్యాధి విశ్లేషణ. 5వ దశ, గ్రాడ్-కామ్ హీట్‌మ్యాప్ వివరణ. 6వ దశ, రిస్క్ అంచనా మరియు హాస్పిటల్ రెఫరల్ పిడిఎఫ్ రిపోర్ట్ తయారీ.",
    "హిన్దీ (Hindi)": "RETINAsync 6 चरणों में काम करता है: चरण 1, प्राथमिक स्वास्थ्य केंद्र पर फंडस फोटो कैप्चर। चरण 2, स्वचालित गुणवत्ता जांच। चरण 3, छवि प्रसंस्करण। चरण 4, AI मॉडल द्वारा बीमारी का वर्गीकरण। चरण 5, Grad-CAM विजुअल हीटमैप द्वारा व्याख्या। चरण 6, जोखिम मूल्यांकन और विशेषज्ञ डॉक्टर के लिए PDF रिपोर्ट तैयार करना।"
}


def t(key: str, lang: str = "English") -> str:
    """Get translated text for given key and language."""
    # Normalize language string
    if "Telugu" in lang or "తెలుగు" in lang:
        lang_key = "తెలుగు (Telugu)"
    elif "Hindi" in lang or "హిన్దీ" in lang or "हिंदी" in lang:
        lang_key = "హిన్దీ (Hindi)"
    else:
        lang_key = "English"

    dict_for_lang = TRANSLATIONS.get(lang_key, TRANSLATIONS["English"])
    return dict_for_lang.get(key, TRANSLATIONS["English"].get(key, key))


def get_workflow_speech_text(lang: str = "English") -> str:
    if "Telugu" in lang or "తెలుగు" in lang:
        return WORKFLOW_EXPLANATIONS["తెలుగు (Telugu)"]
    elif "Hindi" in lang or "हिन्दी" in lang or "हिंदी" in lang:
        return WORKFLOW_EXPLANATIONS["హిన్దీ (Hindi)"]
    return WORKFLOW_EXPLANATIONS["English"]


def get_result_speech_text(grade: int, class_name: str, risk_level: str, lang: str = "English") -> str:
    """Generate audio narrative for post-screening diagnosis explanation and test recommendation."""
    if "Telugu" in lang or "తెలుగు" in lang:
        if grade == 0:
            return f"పరిశీలన పూర్తి అయ్యింది. పేషెంట్ కి కంటి పరీక్షలో ఎటువంటి డయాబెటిక్ రెటినోపతి సంకేతాలు లేవు. కళ్ళు ఆరోగ్యంగా ఉన్నాయి. సంవత్సరానికి ఒకసారి సాధారణ పరీక్ష చేయించుకోండి."
        elif grade in [1, 2]:
            return f"స్క్రీనింగ్ ఫలితం: {class_name}. కంటిలో స్వల్ప మార్పులు గమనించబడ్డాయి. పేషెంట్ కంటి వైద్యుడి వద్ద తదుపరి పరీక్ష మరియు సలహా తీసుకోవడం అవసరం."
        else:
            return f"హెచ్చరిక! స్క్రీనింగ్ ఫలితం: {class_name}, ప్రమాద స్థాయి {risk_level}. దృష్టి నష్టాన్ని నివారించడానికి పేషెంట్ వెంటనే కంటి వైద్య నిపుణుడిని సంప్రదించి పరీక్ష చేయించుకోవాలి."
    elif "Hindi" in lang or "హిन्दी" in lang or "हिंदी" in lang:
        if grade == 0:
            return f"जांच पूरी हो गई है। मरीज की आंखों में डायबिटिक रेटिनोपैथी के कोई लक्षण नहीं हैं। आंखें स्वस्थ हैं। वर्ष में एक बार नियमित जांच करवाएं।"
        elif grade in [1, 2]:
            return f"स्क्रीनिंग परिणाम: {class_name}। आंखों में हल्के लक्षण पाए गए हैं। मरीज को आगे की जांच के लिए नेत्र विशेषज्ञ से परामर्श लेना चाहिए।"
        else:
            return f"सावधान! स्क्रीनिंग परिणाम: {class_name}, जोखिम स्तर {risk_level}। दृष्टि हानि से बचाव के लिए मरीज को तुरंत विशेषज्ञ डॉक्टर से जांच करवानी चाहिए।"
    else:
        if grade == 0:
            return f"Screening complete. Patient shows no signs of Diabetic Retinopathy. Eyes are healthy! Annual routine eye checkup is recommended."
        elif grade in [1, 2]:
            return f"Screening result: {class_name}. Mild to moderate signs detected. The patient must consult an ophthalmologist for detailed follow-up testing."
        else:
            return f"Urgent Notice! Screening result: {class_name}, Risk Level {risk_level}. The patient must immediately visit an eye specialist for comprehensive testing and treatment."

