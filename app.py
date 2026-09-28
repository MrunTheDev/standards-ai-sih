import time
import json
import streamlit as st
from pathlib import Path
from embeddings_engine import StandardsRecommendationEngine
from llm_explainer import generate_match_explanation, summarize_tender_pdf
from pdf_extractor import extract_text_from_pdf
from i18n import get_translation

# Set Page Config
st.set_page_config(
    page_title="StandardsAI - Multilingual Procurement Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session Language State
if "app_lang" not in st.session_state:
    st.session_state["app_lang"] = "English"

lang = st.session_state["app_lang"]

# Custom CSS for SIH-Level Professional Procurement Intelligence UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #0b1329;
        overflow-x: hidden;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }

    /* Header Container */
    .brand-header {
        background: linear-gradient(135deg, #0b1329 0%, #1e293b 50%, #0369a1 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        padding: 1.8rem 2.2rem;
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .brand-title-group {
        display: flex;
        align-items: center;
        gap: 16px;
    }

    .brand-logo-icon {
        background: linear-gradient(135deg, #06b6d4, #2563eb);
        color: #ffffff;
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        box-shadow: 0 6px 16px rgba(6, 182, 212, 0.4);
        flex-shrink: 0;
    }

    .brand-name {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        background: linear-gradient(90deg, #ffffff, #e0f2fe, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        word-break: break-word;
    }

    .brand-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-top: 2px;
        font-weight: 500;
        word-break: break-word;
    }

    .header-badges {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 6px;
    }

    .sih-badge {
        background: linear-gradient(90deg, rgba(6, 182, 212, 0.15), rgba(37, 99, 235, 0.2));
        border: 1px solid #0284c7;
        color: #38bdf8;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        letter-spacing: 0.04em;
        white-space: nowrap;
    }

    .demo-banner-small {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid #f59e0b;
        color: #fbbf24;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 999px;
        white-space: nowrap;
    }

    /* Workflow Progress Bar */
    .workflow-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 10px 20px;
        margin-bottom: 1.8rem;
        flex-wrap: wrap;
        gap: 10px;
    }

    .workflow-step {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #94a3b8;
        font-size: 0.86rem;
        font-weight: 600;
    }

    .workflow-step.active {
        color: #38bdf8;
    }

    .workflow-number {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #334155;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        flex-shrink: 0;
    }

    .workflow-step.active .workflow-number {
        background: #0284c7;
        color: #ffffff;
    }

    /* Language Selector Card */
    .lang-card {
        background: linear-gradient(90deg, #1e293b, #0f172a);
        border: 1px solid #38bdf8;
        border-radius: 14px;
        padding: 12px 18px;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 8px;
    }

    .lang-badge {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid #0284c7;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
    }

    /* Cards */
    .card-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        word-break: break-word;
    }

    /* Metrics Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 1.5rem;
    }

    .metric-card-modern {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        display: flex;
        align-items: center;
        gap: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .metric-icon-box {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
    }

    .metric-value-text {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }

    .metric-label-text {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        margin-top: 2px;
    }

    /* Recommendation Cards */
    .rec-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.6rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
        word-break: break-word;
    }

    .rank-pill {
        background: #0f172a;
        color: #38bdf8;
        font-size: 0.8rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 8px;
    }

    .rel-badge-high {
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #86efac;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }

    .rel-badge-strong {
        background: #e0f2fe;
        color: #0369a1;
        border: 1px solid #7dd3fc;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }

    .rel-badge-mod {
        background: #fef9c3;
        color: #a16207;
        border: 1px solid #fde047;
        font-size: 0.85rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }

    .signal-chip {
        display: inline-block;
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
        margin-right: 5px;
        margin-bottom: 4px;
        word-break: break-word;
    }

    .tree-item {
        font-family: monospace;
        font-size: 0.86rem;
        color: #334155;
        background: #f8fafc;
        padding: 6px 12px;
        border-left: 3px solid #0284c7;
        border-radius: 4px;
        margin-bottom: 6px;
        word-break: break-word;
    }

    .proto-disclaimer {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        color: #92400e;
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 10px;
        word-break: break-word;
    }

    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #22c55e;
        margin-right: 6px;
    }

    /* Mobile Responsive Overrides (320px - 768px) */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 0.8rem !important;
        }

        .brand-header {
            padding: 1.2rem 1.2rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }

        .brand-title-group {
            gap: 12px;
        }

        .brand-logo-icon {
            width: 44px;
            height: 44px;
            font-size: 20px;
        }

        .brand-name {
            font-size: 1.6rem;
        }

        .brand-subtitle {
            font-size: 0.82rem;
        }

        .header-badges {
            align-items: flex-start;
            width: 100%;
            flex-direction: row;
            flex-wrap: wrap;
            gap: 6px;
        }

        .workflow-container {
            padding: 10px 12px;
            gap: 8px;
        }

        .workflow-step {
            font-size: 0.78rem;
        }

        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .metric-card-modern {
            padding: 0.9rem 1rem;
            gap: 10px;
        }

        .metric-icon-box {
            width: 38px;
            height: 38px;
            font-size: 18px;
        }

        .metric-value-text {
            font-size: 1.3rem;
        }

        .metric-label-text {
            font-size: 0.75rem;
        }

        .rec-card {
            padding: 1.1rem;
        }

        .rec-card > div:first-child {
            flex-direction: column;
            align-items: flex-start !important;
            gap: 8px;
        }

        .stButton>button {
            min-height: 44px;
            font-size: 0.9rem;
        }
    }

    @media (max-width: 480px) {
        .brand-name {
            font-size: 1.4rem;
        }

        .metric-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Load Engine Resource
@st.cache_resource
def get_engine():
    return StandardsRecommendationEngine()

try:
    engine = get_engine()
except Exception as e:
    st.error(f"Error loading recommendation engine: {e}")
    st.stop()

# Header Rendering
st.markdown(f"""
    <div class="brand-header">
        <div class="brand-title-group">
            <div class="brand-logo-icon">🏛️</div>
            <div>
                <h1 class="brand-name">StandardsAI</h1>
                <div class="brand-subtitle">{get_translation(lang, "subtitle")}</div>
            </div>
        </div>
        <div class="header-badges">
            <span class="sih-badge">{get_translation(lang, "sih_badge")}</span>
            <span class="demo-banner-small">⚡ Prototype Dataset (BIS)</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Workflow Navigation Bar
st.markdown(f"""
    <div class="workflow-container">
        <div class="workflow-step active">
            <div class="workflow-number">1</div>
            <span>{get_translation(lang, "step_1")}</span>
        </div>
        <div style="color: #475569;">➔</div>
        <div class="workflow-step active">
            <div class="workflow-number">2</div>
            <span>{get_translation(lang, "step_2")}</span>
        </div>
        <div style="color: #475569;">➔</div>
        <div class="workflow-step active">
            <div class="workflow-number">3</div>
            <span>{get_translation(lang, "step_3")}</span>
        </div>
        <div style="color: #475569;">➔</div>
        <div class="workflow-step active">
            <div class="workflow-number">4</div>
            <span>{get_translation(lang, "step_4")}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar Control Panel
with st.sidebar:
    st.markdown("### ⚙️ Engine Controls")
    
    categories = engine.get_categories()
    selected_category = st.selectbox("Category Filter", categories, index=0)
    top_k = st.slider("Max Recommendations", min_value=1, max_value=10, value=5)
    min_threshold = st.slider("Min Relevance Threshold (%)", min_value=0, max_value=50, value=10) / 100.0

    st.markdown("---")
    st.markdown("### 🖥️ System Status")
    st.markdown("""
    <div style="font-size: 0.85rem; line-height: 1.8; color: #cbd5e1;">
        <div><span class="status-dot"></span><b>Retrieval Engine:</b> <span style="color:#4ade80;">Online</span></div>
        <div><span class="status-dot"></span><b>Knowledge Base:</b> <span style="color:#4ade80;">Loaded</span></div>
        <div><span class="status-dot"></span><b>Multilingual i18n:</b> <span style="color:#4ade80;">Active</span></div>
        <div><span class="status-dot"></span><b>Domain Compatibility:</b> <span style="color:#4ade80;">Enforced</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📚 Knowledge Base Stats")
    st.caption(f"Loaded Standards: **{len(engine.standards)}** BIS Specifications")
    st.caption("Active Language: **English | हिंदी | मराठी**")
    
    st.markdown("---")
    st.markdown("""
        <div class="proto-disclaimer">
            <b>PROTOTYPE DATASET</b><br>
            Current results use a demonstration subset of Indian Standards. Production deployment should connect to verified live BIS data.
        </div>
    """, unsafe_allow_html=True)


# Interactive Multilingual Language Selector Bar
st.markdown("""
    <div class="lang-card">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:1.2rem;">🌐</span>
            <span style="color:#ffffff; font-weight:700; font-size:0.95rem;">Select Procurement Input Language</span>
            <span class="lang-badge">Multilingual Procurement Active</span>
        </div>
    </div>
""", unsafe_allow_html=True)

lang_cols = st.columns([1, 1, 1, 3])
with lang_cols[0]:
    if st.button("🇬🇧 English", use_container_width=True, type="primary" if lang == "English" else "secondary"):
        st.session_state["app_lang"] = "English"
        st.rerun()
with lang_cols[1]:
    if st.button("🇮🇳 हिंदी", use_container_width=True, type="primary" if lang == "हिंदी" else "secondary"):
        st.session_state["app_lang"] = "हिंदी"
        st.rerun()
with lang_cols[2]:
    if st.button("🇮🇳 मराठी", use_container_width=True, type="primary" if lang == "मराठी" else "secondary"):
        st.session_state["app_lang"] = "मराठी"
        st.rerun()

st.markdown(" ")

# Input Tabs
tab1, tab2 = st.tabs([get_translation(lang, "tab_text"), get_translation(lang, "tab_pdf")])

query_text = ""

with tab1:
    st.markdown(f"### {get_translation(lang, 'input_card_title')}")
    st.caption(get_translation(lang, "input_card_sub"))

    # Preset Sample Queries localized for selected language
    st.markdown(f"**{get_translation(lang, 'click_sample')}**")
    col1, col2, col3, col4 = st.columns(4)
    
    if lang == "हिंदी":
        if col1.button(get_translation(lang, "sample_led")):
            st.session_state["spec_input"] = "मुझे बाहरी सड़कों के लिए 90W की 100 एलईडी स्ट्रीट लाइट खरीदनी हैं।"
        if col2.button(get_translation(lang, "sample_pipe")):
            st.session_state["spec_input"] = "मुझे नगरपालिका जल आपूर्ति के लिए HDPE पानी की पाइप चाहिए।"
        if col3.button(get_translation(lang, "sample_concrete")):
            st.session_state["spec_input"] = "मुझे फ्लाईओवर पिलर निर्माण के लिए एम30 ग्रेड आरएमसी कंक्रीट चाहिए।"
        if col4.button(get_translation(lang, "sample_ups")):
            st.session_state["spec_input"] = "सर्वर रूम के लिए 10 केवीए ऑनलाइन यूपीएस सिस्टम की खरीद।"
    elif lang == "मराठी":
        if col1.button(get_translation(lang, "sample_led")):
            st.session_state["spec_input"] = "मला बाहेरील रस्त्यांसाठी 90W क्षमतेचे 100 एलईडी स्ट्रीट लाइट्स खरेदी करायचे आहेत."
        if col2.button(get_translation(lang, "sample_pipe")):
            st.session_state["spec_input"] = "मला नगरपालिका पाणीपुरवठ्यासाठी HDPE पाण्याच्या पाइप्सची आवश्यकता आहे."
        if col3.button(get_translation(lang, "sample_concrete")):
            st.session_state["spec_input"] = "मला फ्लायओव्हर पिलर बांधकामासाठी एम३० ग्रेड आरएमसी कंक्रीट खरेदी करायचे आहे."
        if col4.button(get_translation(lang, "sample_ups")):
            st.session_state["spec_input"] = "सर्व्हर रूमसाठी १० केव्हीए ऑनलाईन यूपीएस सिस्टीम खरेदी."
    else: # English
        if col1.button(get_translation(lang, "sample_led")):
            st.session_state["spec_input"] = "I want to procure 100 LED street lights, 90W, for outdoor road use."
        if col2.button(get_translation(lang, "sample_pipe")):
            st.session_state["spec_input"] = "Supply of 500 meters HDPE pipes PE100 PN10 for municipal water supply."
        if col3.button(get_translation(lang, "sample_concrete")):
            st.session_state["spec_input"] = "Procurement of Ready Mix Concrete (RMC) M30 Grade for flyover bridge piers."
        if col4.button(get_translation(lang, "sample_ups")):
            st.session_state["spec_input"] = "Procurement of 10 KVA online Uninterruptible Power Supply (UPS) for server room."

    # Default input assignment
    if lang == "हिंदी":
        default_val = st.session_state.get("spec_input", "मुझे बाहरी सड़कों के लिए 90W की 100 एलईडी स्ट्रीट लाइट खरीदनी हैं।")
    elif lang == "मराठी":
        default_val = st.session_state.get("spec_input", "मला बाहेरील रस्त्यांसाठी 90W क्षमतेचे 100 एलईडी स्ट्रीट लाइट्स खरेदी करायचे आहेत.")
    else:
        default_val = st.session_state.get("spec_input", "I want to procure 100 LED street lights, 90W, for outdoor road use.")

    user_input = st.text_area(
        get_translation(lang, "input_card_title"),
        value=default_val,
        height=110,
        placeholder=get_translation(lang, "input_placeholder")
    )
    query_text = user_input

with tab2:
    st.markdown(f"### {get_translation(lang, 'pdf_title')}")
    st.caption(get_translation(lang, "pdf_sub"))
    
    uploaded_file = st.file_uploader("Upload Tender PDF Specification", type=["pdf"])
    st.markdown("""
        <div style="display:flex; gap:10px; margin-top:8px;">
            <span class="signal-chip">📄 Supported: PDF</span>
            <span class="signal-chip">🔍 Auto Parameter Extraction</span>
            <span class="signal-chip">🌐 Multilingual i18n</span>
            <span class="signal-chip">📑 Compliance Report</span>
        </div>
    """, unsafe_allow_html=True)
    
    if uploaded_file is not None:
        with st.spinner("Extracting requirement parameters from PDF..."):
            pdf_bytes = uploaded_file.read()
            success, text_or_err = extract_text_from_pdf(pdf_bytes)
            if success:
                st.success(f"✓ Extracted text from '{uploaded_file.name}' ({len(text_or_err.split())} words)")
                st.markdown(summarize_tender_pdf(text_or_err))
                query_text = text_or_err
            else:
                st.error(text_or_err)

# Primary Analyze Action Button
st.markdown(" ")
analyze_clicked = st.button(get_translation(lang, "btn_analyze"), type="primary", use_container_width=True)

# Process Query
if analyze_clicked or st.session_state.get("auto_run", False):
    if not query_text or not query_text.strip():
        st.warning("Please enter a procurement requirement or upload a tender PDF.")
    else:
        start_t = time.time()
        
        with st.status("StandardsAI Procurement Analysis...", expanded=True) as status_box:
            st.write("1. Normalizing multilingual procurement terms (English / हिंदी / मराठी)...")
            time.sleep(0.2)
            st.write("2. Evaluating domain compatibility & suppressing cross-domain noise...")
            time.sleep(0.2)
            st.write("3. Computing hybrid vector similarity against BIS database...")
            
            results = engine.search_standards(
                query=query_text,
                top_k=top_k,
                min_score_threshold=min_threshold,
                category_filter=selected_category
            )
            time.sleep(0.2)
            st.write("4. Synthesizing compliance rationale in selected language...")
            time.sleep(0.15)
            status_box.update(label="✓ Analysis Complete", state="complete", expanded=False)

        elapsed = round(time.time() - start_t, 2)

        if results:
            top_score = results[0]["relevance_score"]
            cats_count = len(set(r["category"] for r in results))

            # Modern Metric Cards Grid
            st.markdown(f"""
                <div class="metric-grid">
                    <div class="metric-card-modern">
                        <div class="metric-icon-box" style="background: #e0f2fe; color: #0284c7;">📚</div>
                        <div>
                            <div class="metric-value-text">{len(results)}</div>
                            <div class="metric-label-text">{get_translation(lang, "metrics_standards")}</div>
                        </div>
                    </div>
                    <div class="metric-card-modern">
                        <div class="metric-icon-box" style="background: #dcfce7; color: #166534;">🎯</div>
                        <div>
                            <div class="metric-value-text">{top_score}%</div>
                            <div class="metric-label-text">{get_translation(lang, "metrics_match")}</div>
                        </div>
                    </div>
                    <div class="metric-card-modern">
                        <div class="metric-icon-box" style="background: #f3e8ff; color: #7e22ce;">🏷️</div>
                        <div>
                            <div class="metric-value-text">{cats_count}</div>
                            <div class="metric-label-text">{get_translation(lang, "metrics_cats")}</div>
                        </div>
                    </div>
                    <div class="metric-card-modern">
                        <div class="metric-icon-box" style="background: #fef3c7; color: #b45309;">⚡</div>
                        <div>
                            <div class="metric-value-text">{elapsed}s</div>
                            <div class="metric-label-text">{get_translation(lang, "metrics_time")}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"## {get_translation(lang, 'results_heading')}")
            st.caption(get_translation(lang, "results_sub"))

            # Render Recommendation Cards
            for idx, item in enumerate(results, 1):
                score = item["relevance_score"]
                match_lvl = item.get("match_level", "Match")
                badge_style = "rel-badge-high" if score >= 85 else ("rel-badge-strong" if score >= 70 else "rel-badge-mod")

                with st.container():
                    st.markdown(f"""
                        <div class="rec-card">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                <div>
                                    <span class="rank-pill">#{idx}</span>
                                    <span style="font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-left: 8px;">{item['standard_number']}</span>
                                    <span style="font-size: 0.8rem; background:#f1f5f9; color:#475569; padding: 2px 8px; border-radius: 6px; font-weight:600; margin-left:6px;">{item['status']}</span>
                                    <span style="font-size: 0.8rem; background:#f1f5f9; color:#475569; padding: 2px 8px; border-radius: 6px; font-weight:600; margin-left:4px;">Year: {item['version_year']}</span>
                                </div>
                                <div>
                                    <span class="{badge_style}">{score}% &bull; {match_lvl}</span>
                                </div>
                            </div>
                            <h3 style="color: #0f172a; font-size: 1.15rem; margin-top: 0.4rem; margin-bottom: 0.4rem;">{item['title']}</h3>
                            <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 0.6rem;"><b>Category:</b> {item['category']} &bull; <b>Sub-Category:</b> {item.get('sub_category', 'N/A')}</p>
                            <p style="color: #334155; font-size: 0.92rem; line-height: 1.5;">{item['description']}</p>
                    """, unsafe_allow_html=True)

                    if item.get("matched_terms"):
                        signals_html = "".join([f'<span class="signal-chip">✓ {t}</span>' for t in item["matched_terms"]])
                        st.markdown(f'<div style="margin-top:0.4rem; margin-bottom:0.8rem;"><b>{get_translation(lang, "matched_signals")}</b> {signals_html}</div>', unsafe_allow_html=True)

                    # Localized Why this matches checkmark rationale
                    with st.expander(get_translation(lang, "why_matches"), expanded=(idx == 1)):
                        explanation = generate_match_explanation(query_text, item, lang=lang)
                        st.markdown(explanation)

                    # Related Standards & Source Box
                    col_rel, col_src = st.columns(2)
                    with col_rel:
                        with st.expander(get_translation(lang, "related_standards")):
                            related = item.get("related_standards", [])
                            if related:
                                for rel in related:
                                    st.markdown(f'<div class="tree-item">├── {rel}</div>', unsafe_allow_html=True)
                            else:
                                st.caption("No direct related standards listed.")

                    with col_src:
                        with st.expander(get_translation(lang, "source_evidence")):
                            st.markdown(f"**Reference:** {item.get('source_evidence', 'Bureau of Indian Standards (BIS)')}")
                            st.markdown("""
                                <div class="proto-disclaimer" style="margin-top:4px;">
                                    PROTOTYPE DATASET — Verify against official BIS sources before procurement use.
                                </div>
                            """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

            # Report Export Card
            st.markdown("---")
            st.markdown(f"""
                <div class="card-box" style="background: linear-gradient(135deg, #0f172a, #1e293b); color: #ffffff;">
                    <h3 style="margin-top:0; color:#38bdf8;">{get_translation(lang, 'export_heading')}</h3>
                    <p style="color:#94a3b8; font-size:0.9rem;">
                        {get_translation(lang, 'export_sub')}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            report_lines = [
                f"# StandardsAI Procurement Compliance Report ({lang})",
                f"Generated On: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"Requirement: {query_text}",
                f"\n## Top Recommended Indian Standards (BIS):\n"
            ]
            for r in results:
                report_lines.append(f"### {r['standard_number']} - {r['title']}")
                report_lines.append(f"- Retrieval Relevance Score: {r['relevance_score']}% ({r.get('match_level', '')})")
                report_lines.append(f"- Category: {r['category']} ({r.get('sub_category','')})")
                report_lines.append(f"- Version/Year: {r['version_year']}")
                report_lines.append(f"- Status: {r['status']}")
                report_lines.append(f"- Scope: {r['description']}")
                report_lines.append(f"- Statutory Evidence: {r['source_evidence']}\n")

            report_content = "\n".join(report_lines)
            st.download_button(
                label=get_translation(lang, "btn_download"),
                data=report_content,
                file_name=f"StandardsAI_Procurement_Report_{lang}.md",
                mime="text/markdown"
            )

        else:
            st.info("No matching Indian Standards found for the specified query and threshold. Try adjusting the category filter or reducing the minimum relevance threshold.")

else:
    # Empty State Display (Before Search)
    st.markdown(f"""
        <div class="card-box" style="text-align: center; padding: 2.5rem 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">📜</div>
            <h2 style="color: #0f172a; font-weight: 800; margin-bottom: 0.5rem;">{get_translation(lang, 'empty_title')}</h2>
            <p style="color: #64748b; max-width: 650px; margin: 0 auto 1.5rem auto; font-size: 0.95rem;">
                {get_translation(lang, 'empty_sub')}
            </p>
        </div>
    """, unsafe_allow_html=True)
