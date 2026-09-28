import re
from typing import Dict, Any, List

# Devanagari to Standard ASCII Digit Map
DEVANAGARI_DIGITS = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}

def convert_devanagari_digits(text: str) -> str:
    """Converts Devanagari numerical digits (०-९) to ASCII digits (0-9)."""
    for dev, ascii_digit in DEVANAGARI_DIGITS.items():
        text = text.replace(dev, ascii_digit)
    return text

# Multilingual Vocabulary & Domain Concept Dictionary (Hindi & Marathi -> English Technical Signals)
INDIC_CONCEPT_MAP = {
    # LED & Lighting Signals
    r'एलईडी|एल\.ई\.डी\.|एल इ डी|स्ट्रीट लाइट|स्ट्रीट लाइट्स|स्ट्रीट लाईट|स्ट्रीट लाईट्स': 'led street lights',
    r'लाइट|लाइट्स|लाइटिंग|रोशनी|दीपक|लैंप|बल्ब': 'lighting luminaire lamp bulb',
    r'सड़क|सड़कों|रस्ते|रस्त्यांसाठी|मार्ग|बाहरी|बाहेरील|आउटडोर': 'outdoor road roadway',
    r'वाट|वाॉट': 'w',
    
    # Civil & Piping Signals
    r'एचडीपीई|एच\.डी\.पी\.ई\.|एच डी पी ई|एचडूपीई': 'hdpe',
    r'पाइप|पाइप्स|पाईप|पाईप्स|नल|नली': 'pipe piping',
    r'पानी|जल|पाणी|पाणीपुरवठा|जल आपूर्ति|नगरपालिका': 'water supply municipal',
    
    # Concrete & Civil Structural Signals
    r'कंक्रीट|काँक्रीट|आरएमसी|आर\.एम\.सी\.|रेडी मिक्स': 'rmc concrete',
    r'एम३०|एम30|एम२०|एम20|ग्रेड|प्रत': 'm30 grade',
    r'पुल|फ़्लाईओवर|फ्लाइओवर|पूल|संरचना': 'bridge flyover structural',
    r'सरिया|छड़|टीएमटी|टी\.एम\.टी\.|स्टील': 'tmt steel rebar bar',
    r'पेवर ब्लॉक|पेव्हिंग ब्लॉक्स|लादी': 'paver block paving',
    
    # IT & Electronics / Power Signals
    r'यूपीएस|यू\.पी\.एस\.|इनवर्टर|इन्व्हर्टर|बैटरी बैकअप|बॅटरी': 'ups uninterruptible power supply battery',
    r'डाटा सेंटर|डेटा सेंटर|सर्वर|संगणक|लॉपटॉप|कॉम्प्युटर': 'data center server computer',
    r'केवीए|के\.वी\.ए\.|केव्हीए': 'kva',
    
    # Mechanical & Pumps Signals
    r'सबमर्सिबल|सबमर्सिबल पम्प|सबमर्सिबल पंप|पंपसेट|पम्पसेट': 'submersible pumpset pump',
    r'ट्यूबवेल|ट्यूबवेल|बोअरवेल|बोरवेल|कुआँ|विहीर': 'tubewell borewell',
    r'एचपी|एच\.पी\.|अश्वशक्ति': 'hp',
    r'सिलेंडर|सिलिंडर|एलपीजी|गैस': 'cylinder lpg gas',
    
    # Safety & PPE Signals
    r'गंमबूट|गमबूट|सुरक्षा जूते|सेफ्टी शूज़|सुरक्षा बूट': 'gumboots safety boots footwear',
    r'सुरक्षा ऑडिट|सुरक्षा तपासणी|हादसा': 'safety audit',
    
    # Solar Signals
    r'सोलर|सौर|सोलर पंप|सोलर पॅनेल|फोटोव्होल्टाइक': 'solar pv photovoltaic panel',
    
    # Healthcare Signals (for proper classification)
    r'ऑक्सीमीटर|पल्स ऑक्सीमीटर|अस्पताल|रुग्णालय|वैद्यकीय': 'oximeter medical SpO2'
}

def normalize_multilingual_query(query: str) -> str:
    """
    Normalizes Hindi, Marathi, or mixed-language procurement specifications 
    into a standardized English technical search query representation.
    """
    if not query:
        return ""
        
    # Convert Devanagari numbers to standard ASCII digits
    text = convert_devanagari_digits(query.strip())
    text_lower = text.lower()
    
    extracted_terms = [text] # Keep original text
    
    # Apply regex domain mappings
    for pattern, eng_translation in INDIC_CONCEPT_MAP.items():
        if re.search(pattern, text_lower):
            extracted_terms.append(eng_translation)
            
    # Combine original query with extracted domain technical keywords
    normalized_query = " ".join(extracted_terms)
    return normalized_query


# UI Language Translations (i18n Dictionary)
UI_TRANSLATIONS = {
    "English": {
        "subtitle": "AI-Powered Indian Standards Intelligence for Procurement",
        "sih_badge": "SIH 2026 • Procurement Intelligence",
        "step_1": "1. Describe Requirement",
        "step_2": "2. AI Domain Analysis",
        "step_3": "3. Applicable Standards",
        "step_4": "4. Compliance & Evidence",
        "input_card_title": "Describe what you need to procure",
        "input_card_sub": "Enter product descriptions, technical parameters, wattage, materials, or compliance specs in English, Hindi, or Marathi.",
        "input_placeholder": "Example: Procure 100 LED street lights, 90W, for outdoor road use...",
        "click_sample": "Click an example to test in current language:",
        "sample_led": "💡 90W LED Street Lights",
        "sample_pipe": "💧 HDPE Water Pipes",
        "sample_concrete": "🏗️ M30 Concrete (RMC)",
        "sample_ups": "⚡ 10 KVA Data Center UPS",
        "btn_analyze": "✦ Analyze & Identify Applicable Indian Standards",
        "tab_text": "📝 Specification Input",
        "tab_pdf": "📄 Tender PDF Analyzer",
        "pdf_title": "Analyze a Tender Document",
        "pdf_sub": "Upload a procurement specification or tender PDF and let StandardsAI identify applicable standards.",
        "metrics_standards": "Applicable Standards",
        "metrics_match": "Top Retrieval Match",
        "metrics_cats": "Technical Categories",
        "metrics_time": "Analysis Time",
        "results_heading": "Applicable Indian Standards",
        "results_sub": "Standards ranked by technical relevance and domain compatibility to your procurement requirement.",
        "why_matches": "🤖 Why this standard matches",
        "related_standards": "🔗 Related Standards",
        "source_evidence": "🏛️ Statutory Evidence & Source",
        "matched_signals": "Matched Technical Signals:",
        "export_heading": "📄 Generate Procurement Standards Report",
        "export_sub": "Export a structured procurement compliance report including recommended Indian Standards, relevance justification, statutory evidence, and auditing notes.",
        "btn_download": "↓ Download Compliance Report (.MD)",
        "empty_title": "Find the standards behind your procurement specification",
        "empty_sub": "Describe a product in English, Hindi, or Marathi, upload a tender document, or select an example above to discover applicable Indian Standards (BIS)."
    },
    "हिंदी": {
        "subtitle": "खरीद के लिए एआई-संचालित भारतीय मानक इंटेलिजेंस",
        "sih_badge": "एसआईएच 2026 • खरीद इंटेलिजेंस",
        "step_1": "1. आवश्यकता का विवरण दें",
        "step_2": "2. एआई डोमेन विश्लेषण",
        "step_3": "3. लागू भारतीय मानक",
        "step_4": "4. अनुपालन और प्रमाण",
        "input_card_title": "आप क्या खरीदना चाहते हैं, उसका विवरण दें",
        "input_card_sub": "अंग्रेजी, हिंदी या मराठी में उत्पाद विवरण, तकनीकी मापदंड, वाट क्षमता या सामग्री दर्ज करें।",
        "input_placeholder": "उदाहरण: बाहरी सड़कों के लिए 90W की 100 एलईडी स्ट्रीट लाइट खरीदनी हैं...",
        "click_sample": "वर्तमान भाषा में परीक्षण करने के लिए उदाहरण पर क्लिक करें:",
        "sample_led": "💡 90W एलईडी स्ट्रीट लाइट",
        "sample_pipe": "💧 एचडीपीई पानी की पाइप",
        "sample_concrete": "🏗️ एम30 कंक्रीट (आरएमसी)",
        "sample_ups": "⚡ 10 केवीए यूपीएस सिस्टम",
        "btn_analyze": "✦ लागू भारतीय मानकों का विश्लेषण और पहचान करें",
        "tab_text": "📝 आवश्यकता इनपुट",
        "tab_pdf": "📄 टेंडर पीडीएफ विश्लेषण",
        "pdf_title": "टेंडर दस्तावेज का विश्लेषण करें",
        "pdf_sub": "खरीद विनिर्देश या टेंडर पीडीएफ अपलोड करें और मानकों की पहचान करें।",
        "metrics_standards": "लागू भारतीय मानक",
        "metrics_match": "शीर्ष मिलान स्कोर",
        "metrics_cats": "तकनीकी श्रेणियां",
        "metrics_time": "विश्लेषण समय",
        "results_heading": "लागू भारतीय मानक (BIS)",
        "results_sub": "आपकी खरीद आवश्यकता से तकनीकी प्रासंगिकता के आधार पर रैंक किए गए मानक।",
        "why_matches": "🤖 यह मानक क्यों मेल खाता है",
        "related_standards": "🔗 संबंधित मानक",
        "source_evidence": "🏛️ वैधानिक प्रमाण और स्रोत",
        "matched_signals": "मिलाए गए तकनीकी संकेत:",
        "export_heading": "📄 खरीद मानक अनुपालन रिपोर्ट तैयार करें",
        "export_sub": "अनुशंसित भारतीय मानकों, प्रासंगिकता तर्क, वैधानिक प्रमाण और ऑडिट नोट्स सहित रिपोर्ट डाउनलोड करें।",
        "btn_download": "↓ अनुपालन रिपोर्ट डाउनलोड करें (.MD)",
        "empty_title": "अपनी खरीद विनिर्देश के पीछे के मानकों को खोजें",
        "empty_sub": "अंग्रेजी, हिंदी या मराठी में उत्पाद का वर्णन करें, टेंडर अपलोड करें या ऊपर दिए गए उदाहरण चुनें।"
    },
    "मराठी": {
        "subtitle": "खरेदीसाठी एआय-संचालित भारतीय मानके इंटेलिजन्स",
        "sih_badge": "एसआयएच २०२६ • खरेदी इंटेलिजन्स",
        "step_1": "1. आवश्यकता वर्णन करा",
        "step_2": "2. एआय डोमेन विश्लेषण",
        "step_3": "3. लागू भारतीय मानके",
        "step_4": "4. अनुपालन आणि पुरावे",
        "input_card_title": "आपल्याला काय खरेदी करायचे आहे त्याचे वर्णन करा",
        "input_card_sub": "इंग्रजी, हिंदी किंवा मराठीत उत्पादन वर्णन, तांत्रिक निकष, वॅट क्षमता किंवा साहित्य प्रविष्ट करा.",
        "input_placeholder": "उदाहरण: बाहेरील रस्त्यांसाठी ९०W क्षमतेचे १०० एलईडी स्ट्रीट लाइट्स खरेदी करायचे आहेत...",
        "click_sample": "सध्याच्या भाषेत चाचणी करण्यासाठी उदाहरणावर क्लिक करा:",
        "sample_led": "💡 ९०W एलईडी स्ट्रीट लाइट्स",
        "sample_pipe": "💧 एचडीपीई पाण्याच्या पाइप्स",
        "sample_concrete": "🏗️ एम३० कंक्रीट (आरएमसी)",
        "sample_ups": "⚡ १० केव्हीए यूपीएस सिस्टीम",
        "btn_analyze": "✦ लागू भारतीय मानके शोधा व विश्लेषित करा",
        "tab_text": "📝 आवश्यकता इनपुट",
        "tab_pdf": "📄 टेंडर पीडीएफ विश्लेषण",
        "pdf_title": "टेंडर दस्तऐवजाचे विश्लेषण करा",
        "pdf_sub": "खरेदी तपशील किंवा टेंडर पीडीएफ अपलोड करा आणि लागू मानके शोधा.",
        "metrics_standards": "लागू भारतीय मानके",
        "metrics_match": "शीर्ष जुळणी स्कोअर",
        "metrics_cats": "तांत्रिक वर्ग",
        "metrics_time": "विश्लेषण वेळ",
        "results_heading": "लागू भारतीय मानके (BIS)",
        "results_sub": "आपल्या खरेदी आवश्यकतेनुसार तांत्रिक सुसंगततेच्या आधारे रँक केलेली मानके.",
        "why_matches": "🤖 हे मानक आपल्या आवश्यकतेशी का जुळते",
        "related_standards": "🔗 संबंधित मानके",
        "source_evidence": "🏛️ वैधानिक पुरावे आणि स्रोत",
        "matched_signals": "जुळलेले तांत्रिक संकेत:",
        "export_heading": "📄 खरेदी मानके अनुपालन अहवाल तयार करा",
        "export_sub": "शिफारस केलेली भारतीय मानके, सुसंगतता स्पष्टीकरण, वैधानिक पुरावे आणि अहवाल डाउनलोड करा.",
        "btn_download": "↓ अनुपालन अहवाल डाउनलोड करा (.MD)",
        "empty_title": "आपल्या खरेदी तपशीलामागील मानके शोधा",
        "empty_sub": "इंग्रजी, हिंदी किंवा मराठीत उत्पादनाचे वर्णन करा, टेंडर अपलोड करा किंवा वरील उदाहरणे निवडा."
    }
}

def get_translation(lang: str, key: str) -> str:
    """Retrieves localized text string for the specified language and UI key."""
    lang_dict = UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["English"])
    return lang_dict.get(key, UI_TRANSLATIONS["English"].get(key, key))
