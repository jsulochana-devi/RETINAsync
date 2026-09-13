"""
pages/about.py
About RETINAsync page.
"""

import streamlit as st


def render():
    st.markdown('<div class="page-header"><h2>ℹ️ About RETINAsync</h2></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section" style="padding:32px; text-align:center">
        <div class="hero-logo" style="font-size:2.5rem"><span style="-webkit-text-fill-color:initial;background:none">👁️ </span>RETINAsync</div>
        <div class="hero-tagline">Explainable AI for Diabetic Retinopathy Screening in Rural India</div>
        <div class="prototype-badge">Smart India Hackathon 2026 — Problem Statement SIH26038</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # About section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Problem Statement")
        st.markdown("""
        <div class="about-card">
        Diabetic Retinopathy (DR) is a leading cause of preventable blindness worldwide,
        disproportionately affecting rural populations in India who lack access to specialist
        ophthalmological care.<br><br>
        <strong>SIH26038</strong> challenges innovators to create an explainable, accessible,
        AI-powered screening tool that community health workers can use in low-resource settings
        to identify at-risk patients and connect them to appropriate care before vision loss occurs.
        </div>""", unsafe_allow_html=True)

        st.markdown("### 🧠 How It Works")
        st.markdown("""
        <div class="about-card">
        <ol>
        <li><strong>Image Capture</strong> — Upload or capture a fundus photograph.</li>
        <li><strong>Quality Gate</strong> — Automatic blur, illumination, and FOV assessment.</li>
        <li><strong>Preprocessing</strong> — CLAHE, denoising, and normalization pipeline.</li>
        <li><strong>CNN Classification</strong> — 5-class DR severity prediction.</li>
        <li><strong>Grad-CAM</strong> — Visual heatmap explaining the AI decision.</li>
        <li><strong>Risk Stratification</strong> — Grade mapped to referral recommendation.</li>
        <li><strong>Report</strong> — PDF report for clinician handoff.</li>
        </ol>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("### 🏗️ Technology Stack")
        st.markdown("""
        <div class="about-card">
        <table style="width:100%; border-collapse:collapse; font-size:0.88rem">
            <tr><td><strong>Frontend</strong></td><td>Python · Streamlit · Custom CSS · Plotly</td></tr>
            <tr><td><strong>AI / ML</strong></td><td>TensorFlow/Keras · CNN · Grad-CAM</td></tr>
            <tr><td><strong>Image Processing</strong></td><td>OpenCV · CLAHE · PIL</td></tr>
            <tr><td><strong>Database</strong></td><td>SQLite (local, offline-ready)</td></tr>
            <tr><td><strong>Reports</strong></td><td>ReportLab PDF</td></tr>
            <tr><td><strong>Deployment</strong></td><td>Local laptop · No cloud required</td></tr>
        </table>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📐 DR Classification")
        st.markdown("""
        <div class="about-card">
        <table style="width:100%; font-size:0.88rem; border-collapse:collapse">
            <tr><th>Grade</th><th>Classification</th><th>Risk</th></tr>
            <tr><td>0</td><td>No DR</td><td style="color:#22c55e">Low</td></tr>
            <tr><td>1</td><td>Mild DR</td><td style="color:#84cc16">Low–Moderate</td></tr>
            <tr><td>2</td><td>Moderate DR</td><td style="color:#f59e0b">Moderate</td></tr>
            <tr><td>3</td><td>Severe DR</td><td style="color:#ef4444">High</td></tr>
            <tr><td>4</td><td>Proliferative DR</td><td style="color:#7c3aed">Very High</td></tr>
        </table>
        </div>""", unsafe_allow_html=True)

    # Disclaimer
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-card">
        <h4>⚠️ Important Medical Disclaimer</h4>
        <p>
        RETINAsync is a <strong>research and hackathon prototype</strong> created for the Smart India Hackathon 2026.
        It is <strong>NOT a certified medical device</strong> and has <strong>NOT been clinically validated</strong>.
        </p>
        <p>
        All AI predictions, Grad-CAM visualizations, and risk stratification results produced by this prototype
        are for <strong>demonstration and research purposes only</strong>. They do not constitute medical advice,
        clinical diagnosis, or a substitute for professional ophthalmological assessment.
        </p>
        <p>
        This system must <strong>NOT</strong> be used to make real patient care decisions without review by
        a qualified healthcare professional.
        </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>")
    st.caption("RETINAsync v1.0 — SIH 2026 Prototype — Problem Statement SIH26038")
