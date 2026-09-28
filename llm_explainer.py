import os
from typing import Dict, Any, List

def generate_match_explanation(procurement_req: str, standard: Dict[str, Any], lang: str = "English") -> str:
    """
    Generates a natural language explanation of why a specific Indian Standard 
    is applicable to the given procurement requirement in the selected language.
    Supports lang codes: 'English', 'en', 'हिंदी', 'hi', 'मराठी', 'mr'.
    """
    std_num = standard.get("standard_number", "")
    std_title = standard.get("title", "")
    category = standard.get("category", "")
    description = standard.get("description", "")
    key_specs = standard.get("key_specifications", [])
    matched_terms = standard.get("matched_terms", [])

    # Normalize language string
    lang_str = str(lang).strip().lower() if lang else "english"
    if lang_str in ["hi", "hindi", "हिंदी"]:
        target_lang = "हिंदी"
    elif lang_str in ["mr", "marathi", "मराठी"]:
        target_lang = "मराठी"
    else:
        target_lang = "English"

    # 1. Check if Gemini API key exists for LLM translation
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""
            You are an expert Procurement Officer & BIS Technical Consultant.
            Explain concisely in 2-3 bullet points in language '{target_lang}' why the Indian Standard below is relevant.

            PROCUREMENT SPECIFICATION: "{procurement_req}"
            STANDARD: {std_num} - {std_title} ({category})
            SCOPE: {description}
            """
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception:
            pass

    # 2. Localized Structured Fallback Engine
    explanation_parts = []
    
    if target_lang == "हिंदी":
        if matched_terms:
            terms_str = ", ".join([f"'{t}'" for t in matched_terms[:4]])
            explanation_parts.append(f"✓ **प्रत्यक्ष तकनीकी संरेखण:** निकाली गई तकनीकी आवश्यकताओं ({terms_str}) से सटीक मेल खाता है।")
        else:
            explanation_parts.append(f"✓ **श्रेणी एवं दायरा अनुपालन:** **{category}** क्षेत्र के अंतर्गत खरीद विनिर्देशों को नियंत्रित करता है।")

        explanation_parts.append(f"✓ **आवेदन एवं क्षेत्र कवरेज:** {description}")
        
        if key_specs:
            explanation_parts.append(f"✓ **प्रमुख तकनीकी मानक:** मुख्य रूप से {', '.join(key_specs[:4])} मापदंडों का नियमन करता है।")
        
        explanation_parts.append(f"✓ **अनुपालन सलाह:** सार्वजनिक खरीद प्रक्रियाओं के तहत इस मानक का पालन अनिवार्य है।")

    elif target_lang == "मराठी":
        if matched_terms:
            terms_str = ", ".join([f"'{t}'" for t in matched_terms[:4]])
            explanation_parts.append(f"✓ **थेट तांत्रिक सुसंगतता:** काढलेल्या तांत्रिक निकषांशी ({terms_str}) तंतोतंत जुळते.")
        else:
            explanation_parts.append(f"✓ **वर्ग आणि व्याप्ती शासन:** **{category}** क्षेत्रातील खरेदी आवश्यकता नियंत्रित करते.")

        explanation_parts.append(f"✓ **अर्जाची व्याप्ती:** {description}")
        
        if key_specs:
            explanation_parts.append(f"✓ **प्रमुख तांत्रिक मानके:** मुख्यत्वे {', '.join(key_specs[:4])} मानकांचे नियंत्रण करते.")
            
        explanation_parts.append(f"✓ **अनुपालन सल्ला:** सार्वजनिक खरेदी प्रक्रियेत या मानकाचे पालन करणे बंधनकारक आहे.")

    else: # English
        if matched_terms:
            terms_str = ", ".join([f"'{t}'" for t in matched_terms[:4]])
            explanation_parts.append(f"✓ **Direct Technical Alignment:** Explicitly matches extracted technical parameters ({terms_str}).")
        else:
            explanation_parts.append(f"✓ **Category & Scope Governance:** Governs procurement specifications within **{category}** ({standard.get('sub_category', '')}).")

        explanation_parts.append(f"✓ **Application & Scope Coverage:** {description}")

        if key_specs:
            explanation_parts.append(f"✓ **Key Technical Standards:** Regulates {', '.join(key_specs[:4])} parameters.")

        if "led" in procurement_req.lower() or "led" in std_title.lower():
            explanation_parts.append("✓ **Compliance Advisory:** Mandatory under MeitY and BIS Quality Control Orders (QCO) for public sector LED procurement.")
        elif "concrete" in procurement_req.lower() or "steel" in procurement_req.lower() or "pipe" in procurement_req.lower():
            explanation_parts.append("✓ **Compliance Advisory:** Mandatory standard referenced in CPWD/PWD structural safety guidelines.")
        elif "pump" in procurement_req.lower() or "solar" in procurement_req.lower():
            explanation_parts.append("✓ **Compliance Advisory:** Required for BEE Star Labeling and PM-KUSUM scheme tender submissions.")
        else:
            explanation_parts.append("✓ **Compliance Advisory:** Standard inclusion protects against non-compliant vendors and guarantees warranty enforcement.")

    return "\n".join(explanation_parts)


def summarize_tender_pdf(extracted_text: str) -> str:
    """
    Summarizes key technical requirements from a PDF tender document.
    """
    if len(extracted_text) < 300:
        return extracted_text.strip()
        
    lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
    header_preview = " ".join(lines[:10])
    
    # Try finding technical requirement sections
    tech_keywords = ["specifications", "scope of work", "technical requirement", "product specification", "item description", "supply of"]
    extracted_bullets = []
    
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in tech_keywords) or any(char in line for char in [':', 'W', 'V', 'HP', 'grade', 'mm', 'kg', 'LED', 'HDPE']):
            if len(line) > 15 and len(line) < 150:
                extracted_bullets.append(f"• {line}")
                if len(extracted_bullets) >= 5:
                    break

    summary = f"**Document Summary Preview:**\n{header_preview[:250]}...\n\n"
    if extracted_bullets:
        summary += "**Extracted Key Technical Phrases:**\n" + "\n".join(extracted_bullets)
    else:
        summary += f"**Full Content Snippet:**\n{extracted_text[:400]}..."

    return summary
