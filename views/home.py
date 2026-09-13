import streamlit as st
from backend.database import get_dashboard_stats
from backend.i18n import t


def render():
    lang = st.session_state.get("language", "English")
    # Hero section
    st.markdown(f"""
    <div class="hero-section">
        <div class="hero-logo"><span style="-webkit-text-fill-color:initial;background:none">👁️ </span>{t('app_title', lang)}</div>
        <div class="hero-tagline">{t('app_subtitle', lang)}</div>
        <div class="hero-subtitle">Capture &nbsp;·&nbsp; Validate &nbsp;·&nbsp; Screen &nbsp;·&nbsp; Explain &nbsp;·&nbsp; Refer</div>
        <div class="prototype-badge">🔬 Research Prototype &nbsp;|&nbsp; Smart India Hackathon 2026 &nbsp;|&nbsp; SIH26038</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats bar
    try:
        stats = get_dashboard_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_patients']}</div>
                <div class="stat-label">Patients Screened</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['total_screenings']}</div>
                <div class="stat-label">Total Screenings</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['quality_pass_rate']}%</div>
                <div class="stat-label">Quality Pass Rate</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{stats['referrals_needed']}</div>
                <div class="stat-label">Referrals Required</div>
            </div>""", unsafe_allow_html=True)
    except Exception:
        pass

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    st.markdown("### ✨ Key Features")
    c1, c2, c3, c4 = st.columns(4)

    features = [
        (c1, "🔍", "Instant Quality Check",
         "Automatic blur, illumination & field-of-view validation before analysis."),
        (c2, "🧠", "5-Level DR Screening",
         "CNN classifies No DR through Proliferative DR with confidence scoring."),
        (c3, "🗺️", "Explainable AI (Grad-CAM)",
         "Visual heatmaps highlight regions driving the prediction."),
        (c4, "📋", "Risk-Based Referral",
         "Automated referral-support from Grade 0 to Grade 4."),
    ]
    for col, icon, title, desc in features:
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA button
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("🚀 Start New Screening", width="stretch", type="primary",
                     key="home_start_screening"):
            st.session_state["page"] = "New Screening"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Creative Screening Workflow ──────────────────────────────
    st.markdown(f"### 📍 {t('screening_workflow', lang)}")
    st.markdown("""
    <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:16px;">
        Click any stage below to explore detailed information, clinical recommendations, or navigate directly to that phase of the screening system.
    </div>
    """, unsafe_allow_html=True)

    wf_steps = [
        ("📸", "01. Capture", "Upload Fundus Image", "New Screening",
         "Captures digital retinal image using a non-mydriatic fundus camera or smartphone attachment at the Primary Health Center (PHC)."),
        ("✅", "02. Quality", "Instant Quality Gate", "New Screening",
         "Performs automated blur, illumination, and field-of-view assessment to prevent poor quality uploads from reaching the AI model."),
        ("⚙️", "03. Preprocess", "CLAHE Enhancement", "New Screening",
         "Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) and Gaussian noise reduction for high-contrast retinal structure extraction."),
        ("🧠", "04. AI Classify", "5-Level Severity", "AI Analysis",
         "Deep Convolutional Neural Network predicts Diabetic Retinopathy severity across Grades 0 (No DR) to 4 (Proliferative DR)."),
        ("🗺️", "05. Grad-CAM", "XAI Heatmap", "AI Analysis",
         "Generates Gradient-weighted Class Activation Mapping (Grad-CAM) visual overlays proving model reasoning for clinician validation."),
        ("📋", "06. Risk Triage", "Referral Protocol", "AI Analysis",
         "Stratifies patient risk level into Low, Moderate, High, or Very High and recommends immediate, 6-month, or routine specialist referrals."),
        ("📄", "07. Report", "ISO Medical PDF", "Dashboard",
         "Generates a verified, downloadable PDF report with embedded Grad-CAM overlays and unique QR verification for district hospital handoff.")
    ]

    # First row: 4 workflow steps
    row1_cols = st.columns(4)
    for col, (icon, step_no, title, target_page, desc) in zip(row1_cols, wf_steps[:4]):
        num = step_no.split(".")[0].lstrip("0") or "0"
        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, rgba(15,23,42,0.85), rgba(22,34,60,0.9));
                        border:1px solid rgba(56,189,248,0.22); border-radius:16px; padding:22px 14px 16px;
                        text-align:center; min-height:200px; display:flex; flex-direction:column;
                        align-items:center; justify-content:flex-start; gap:10px; transition:all 0.25s;
                        box-shadow:0 4px 18px rgba(0,0,0,0.35);">
                <div style="
                    width:46px; height:46px; border-radius:50%;
                    background:linear-gradient(135deg, #0d9488, #0891b2);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.25rem; font-weight:900; color:#fff;
                    box-shadow:0 0 14px rgba(56,189,248,0.45);
                    flex-shrink:0;
                ">{num}</div>
                <div style="font-size:0.95rem; font-weight:800; color:#e2e8f0; margin-top:2px; line-height:1.3;">{title}</div>
                <div style="font-size:0.78rem; color:#94a3b8; line-height:1.4; flex:1;">{desc[:90] + ('...' if len(desc)>90 else '')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go to {step_no.split('.')[1].strip()}", use_container_width=True, key=f"btn_{step_no}"):
                st.session_state["page"] = target_page
                st.rerun()
    # Second row: remaining 3 workflow steps
    row2_cols = st.columns(3)
    for col, (icon, step_no, title, target_page, desc) in zip(row2_cols, wf_steps[4:]):
        num = step_no.split(".")[0].lstrip("0") or "0"
        with col:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, rgba(15,23,42,0.85), rgba(22,34,60,0.9));
                        border:1px solid rgba(56,189,248,0.22); border-radius:16px; padding:22px 14px 16px;
                        text-align:center; min-height:200px; display:flex; flex-direction:column;
                        align-items:center; justify-content:flex-start; gap:10px; transition:all 0.25s;
                        box-shadow:0 4px 18px rgba(0,0,0,0.35);">
                <div style="
                    width:46px; height:46px; border-radius:50%;
                    background:linear-gradient(135deg, #0d9488, #0891b2);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.25rem; font-weight:900; color:#fff;
                    box-shadow:0 0 14px rgba(56,189,248,0.45);
                    flex-shrink:0;
                ">{num}</div>
                <div style="font-size:0.95rem; font-weight:800; color:#e2e8f0; margin-top:2px; line-height:1.3;">{title}</div>
                <div style="font-size:0.78rem; color:#94a3b8; line-height:1.4; flex:1;">{desc[:90] + ('...' if len(desc)>90 else '')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go to {step_no.split('.')[1].strip()}", use_container_width=True, key=f"btn_{step_no}"):
                st.session_state["page"] = target_page
                st.rerun()


    # Step Deep Dive Information Expander
    st.markdown("<br>", unsafe_allow_html=True)
    selected_step_info = st.selectbox(
        "🔍 Select a Stage to View Detailed Technical & Clinical Details:",
        [f"{s[1]} — {s[2]}" for s in wf_steps],
        key="wf_info_select"
    )
    for s in wf_steps:
        if f"{s[1]} — {s[2]}" == selected_step_info:
            st.markdown(f"""
            <div class="info-card" style="border-left:4px solid #38bdf8; background:rgba(56,189,248,0.06);">
                <h4 style="margin:0 0 6px 0; color:#38bdf8;">{s[0]} Stage {s[1]}: {s[2]}</h4>
                <p style="margin:0 0 10px 0; font-size:0.9rem; color:#cbd5e1;">{s[4]}</p>
                <div style="font-size:0.8rem; color:#94a3b8;">
                    <strong>Target Application Page:</strong> <span class="badge-blue">{s[3]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Offline & disclaimer notice
    col_x, col_y = st.columns(2)
    with col_x:
        st.markdown("""
        <div class="offline-banner">
            📶 <strong>Offline-Ready Prototype</strong><br>
            All processing runs locally. No cloud connectivity required.
            Local SQLite database — no patient data leaves the device.
        </div>""", unsafe_allow_html=True)
    with col_y:
        st.markdown("""
        <div class="disclaimer-banner">
            ⚠️ <strong>Medical Disclaimer</strong><br>
            Research prototype — not a certified medical device.
            All results require review by a qualified ophthalmologist.
            Do not use for clinical diagnosis.
        </div>""", unsafe_allow_html=True)
