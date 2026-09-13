"""
pages/ai_analysis.py
CNN classification, Grad-CAM, risk stratification, and result display.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from PIL import Image
import os
from datetime import datetime

from backend.model import predict_dr_grade, load_model, get_model, is_demo_mode
from backend.gradcam import generate_gradcam
from backend.risk import calculate_risk, DR_CLASSES
from backend.database import (
    save_screening, generate_screening_id, get_patient
)
from backend.report import generate_report
from backend.i18n import get_result_speech_text


def _progress_step(label: str, done: bool = True) -> str:
    icon = "✅" if done else "⏳"
    cls = "done" if done else "pending"
    return f'<div class="progress-step {cls}">{icon} {label}</div>'


def _confidence_color(conf: float) -> str:
    if conf >= 80:
        return "#22c55e"
    elif conf >= 60:
        return "#f59e0b"
    else:
        return "#ef4444"


def render():
    st.markdown('<div class="page-header"><h2>🧠 AI Analysis</h2></div>', unsafe_allow_html=True)

    # Determine if we are in review mode (navigated from history)
    is_review = st.session_state.get("selected_screening_id") is not None
    if not is_review:
        # Guard — check prerequisites for a fresh screening
        if "model_input" not in st.session_state or st.session_state["model_input"] is None:
            st.warning("⚠️ No preprocessed image found. Please complete the screening workflow first.")
            if st.button("📷 Go to New Screening", key="ai_go_screening"):
                st.session_state["page"] = "New Screening"
                st.rerun()
            return

    model_input = st.session_state["model_input"]
    original_img = st.session_state.get("original_image")
    preprocessed_img = st.session_state.get("preprocessed_image")
    quality_result = st.session_state.get("quality_result", {})
    patient_id = st.session_state.get("screening_patient_id", "UNKNOWN")
    eye_side = st.session_state.get("screening_eye_side", "Unknown")

    patient = get_patient(patient_id) if patient_id != "UNKNOWN" else None

    # ── Load model ─────────────────────────────────────────────────────────────
    model, demo = load_model()
    demo_flag = is_demo_mode()

    if demo_flag:
        st.markdown("""
        <div class="demo-banner">
            🎭 DEMO MODE — Predictions are demonstration values, NOT real clinical AI output.
            Connect a trained <code>models/dr_model.keras</code> to enable real inference.
        </div>""", unsafe_allow_html=True)

    # ── Progress tracker ───────────────────────────────────────────────────────
    st.markdown("#### Analysis Pipeline")
    steps_html = "".join([
        _progress_step("Quality Gate"),
        _progress_step("Preprocessing"),
        _progress_step("CNN Classification"),
    ])
    st.markdown(f'<div class="progress-bar">{steps_html}</div>', unsafe_allow_html=True)

    # ── Run inference ──────────────────────────────────────────────────────────
    with st.spinner("Running AI classification..."):
        prediction = predict_dr_grade(model_input)

    # Store in session
    st.session_state["prediction_result"] = prediction

    grade = prediction["grade"]
    confidence = prediction["confidence"]
    probs = prediction["probabilities"]
    class_full = prediction["class_name_full"]

    # ── Progress: Grad-CAM ─────────────────────────────────────────────────────
    steps_html2 = steps_html + _progress_step("Grad-CAM Explainability")
    st.markdown(f'<div class="progress-bar">{steps_html2}</div>', unsafe_allow_html=True)

    with st.spinner("Generating Grad-CAM visualization..."):
        gradcam_result = generate_gradcam(
            model=model,
            image_array=model_input,
            grade=grade,
            is_demo=demo_flag
        )

    st.session_state["gradcam_result"] = gradcam_result

    # ── Progress: Risk ─────────────────────────────────────────────────────────
    risk_info = calculate_risk(grade)
    steps_html3 = steps_html2 + _progress_step("Risk Stratification")
    st.markdown(f'<div class="progress-bar">{steps_html3}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Main result cards ──────────────────────────────────────────────────────
    st.markdown("### 📊 Screening Result")

    col_grade, col_conf, col_risk = st.columns(3)

    with col_grade:
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Predicted Grade</div>
            <div class="result-grade">Grade {grade}</div>
            <div class="result-class">{class_full}</div>
            {"<div class='demo-label'>DEMONSTRATION</div>" if demo_flag else ""}
        </div>""", unsafe_allow_html=True)

    with col_conf:
        conf_color = _confidence_color(confidence)
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">Confidence Score</div>
            <div class="result-grade" style="color:{conf_color}">{confidence}%</div>
            <div class="result-class">Model Confidence</div>
            {"<div class='demo-label'>DEMONSTRATION</div>" if demo_flag else ""}
        </div>""", unsafe_allow_html=True)

    with col_risk:
        st.markdown(f"""
        <div class="result-card" style="border-left: 4px solid {risk_info['risk_color']}">
            <div class="result-label">Risk Level</div>
            <div class="result-grade" style="color:{risk_info['risk_color']}">{risk_info['risk_level']}</div>
            <div class="result-class">{risk_info['referral_text']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Probability bar chart ──────────────────────────────────────────────────
    st.markdown("#### 📈 Class Probability Distribution")
    if demo_flag:
        st.caption("⚠️ These are demonstration probabilities, not real clinical AI predictions.")

    class_names = ["No DR", "Mild DR", "Moderate DR", "Severe DR", "Proliferative DR"]
    colors_bar = ["#22c55e", "#84cc16", "#f59e0b", "#ef4444", "#7c3aed"]
    bar_colors = [colors_bar[i] if i == grade else "#334155" for i in range(5)]

    fig = go.Figure(go.Bar(
        x=class_names,
        y=[p * 100 for p in probs],
        marker_color=bar_colors,
        text=[f"{p*100:.1f}%" for p in probs],
        textposition="outside",
    ))
    fig.update_layout(
        yaxis_title="Probability (%)",
        yaxis=dict(range=[0, 110]),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=300,
        showlegend=False,
    )
    st.plotly_chart(fig, width="stretch")

    # ── Risk stratification card ───────────────────────────────────────────────
    st.markdown("#### 📋 Risk Stratification & Referral Support")
    st.markdown(f"""
    <div class="risk-card" style="border-left: 5px solid {risk_info['risk_color']}">
        <div class="risk-header">{risk_info['risk_badge']} — {risk_info['urgency']}</div>
        <div class="risk-referral">{risk_info['referral_text']}</div>
        <div class="risk-advice">{risk_info['advice']}</div>
        <div class="risk-footer">
            ⚠️ Prototype referral-support logic — NOT an official clinical protocol.<br>
            All findings must be reviewed by a qualified ophthalmologist.
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Grad-CAM section ───────────────────────────────────────────────────────
    st.markdown("#### 🗺️ Explainable AI — Grad-CAM")

    if gradcam_result.get("is_demo"):
        st.markdown("""
        <div class="demo-banner">
            🎭 Grad-CAM Demonstration Visualization — This heatmap is synthetically generated
            for demonstration. Connect a trained model for real gradient-based explanations.
        </div>""", unsafe_allow_html=True)
    else:
        st.success("✅ Real Grad-CAM computed from model gradients.")

    col_o, col_h, col_ov = st.columns(3)
    with col_o:
        st.markdown('<div class="img-label">Original Image</div>', unsafe_allow_html=True)
        if original_img:
            st.image(original_img, width="stretch")
    with col_h:
        st.markdown('<div class="img-label">Grad-CAM Heatmap</div>', unsafe_allow_html=True)
        if gradcam_result.get("heatmap_pil"):
            st.image(gradcam_result["heatmap_pil"], width="stretch")
    with col_ov:
        st.markdown('<div class="img-label">Heatmap Overlay</div>', unsafe_allow_html=True)
        if gradcam_result.get("overlay_pil"):
            st.image(gradcam_result["overlay_pil"], width="stretch")

    st.markdown("""
    <div class="info-card" style="margin-top:12px">
        <small>
        Highlighted regions (warm colours = red/yellow) indicate image areas that contributed most strongly
        to the model's prediction. This visualization supports clinician review and does not independently
        establish a diagnosis. Gradient-based explanations are interpretive aids only.
        </small>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Post-Screening Voice Assistant ─────────────────────────────────────────
    lang = st.session_state.get("language", "English")
    result_speech_text = get_result_speech_text(grade, class_full, risk_info["risk_level"], lang)
    lang_code = "te-IN" if "Telugu" in lang else "hi-IN" if "Hindi" in lang else "en-IN"

    # Sanitise text for safe JS embedding
    safe_text = (result_speech_text
                 .replace("\\", "")
                 .replace('"', "'")
                 .replace("\n", " ")
                 .replace("\r", ""))

    btn_listen = "ఆడియో వినండి" if "Telugu" in lang else "ऑडियो सुनें" if "Hindi" in lang else "Listen to Diagnosis"
    btn_stop   = "ఆపు"           if "Telugu" in lang else "रोकें"         if "Hindi" in lang else "Stop"

    st.markdown(f"#### 🗣️ Voice Assistant — {lang} Diagnosis Explanation")
    st.markdown(f"""
    <div class="info-card" style="background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); margin-bottom:10px;">
        <strong>🔊 Audio Summary ({lang}):</strong><br>
        <em>"{result_speech_text}"</em>
    </div>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    voice_html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:transparent;">
<script>
  var SPEECH_TEXT = "{safe_text}";
  var SPEECH_LANG = "{lang_code}";
  var SPEECH_RATE = 0.92;

  function doSpeak() {{
    if (!('speechSynthesis' in window)) {{
      alert('Speech synthesis not supported in this browser.');
      return;
    }}
    window.speechSynthesis.cancel();
    var utter = new SpeechSynthesisUtterance(SPEECH_TEXT);
    utter.lang = SPEECH_LANG;
    utter.rate = SPEECH_RATE;
    window.speechSynthesis.speak(utter);
  }}

  function doStop() {{
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }}

  // Auto-speak on load (first load only, driven by Python flag)
  window.addEventListener('load', function() {{
    {"doSpeak();" if not st.session_state.get(f"voice_spoken_{st.session_state.get('current_screening_id','pending')+'_done'}", False) else "// already spoken"}
  }});
</script>
<button id="btn-speak"
  onclick="doSpeak()"
  style="background:linear-gradient(135deg,#0e7490,#06b6d4);
         color:white; border:none; padding:10px 22px; border-radius:10px;
         font-weight:700; cursor:pointer; font-size:0.9rem;
         box-shadow:0 4px 15px rgba(6,182,212,0.3); margin-right:10px;">
  🔊 {btn_listen}
</button>
<button id="btn-stop"
  onclick="doStop()"
  style="background:rgba(60,60,80,0.9); color:#94a3b8;
         border:1px solid rgba(255,255,255,0.2); padding:10px 18px;
         border-radius:10px; font-weight:600; cursor:pointer; font-size:0.9rem;">
  ⏹ {btn_stop}
</button>
</body>
</html>
"""
    # Mark as spoken so auto-play doesn't repeat on rerun
    st.session_state[f"voice_spoken_{st.session_state.get('current_screening_id','pending')+'_done'}"] = True
    components.html(voice_html, height=60, scrolling=False)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # ── Patient summary card ───────────────────────────────────────────────────
    if patient:
        st.markdown("#### 📄 Screening Summary")
        st.markdown(f"""
        <div class="summary-card">
            <div class="summary-row">
                <span class="summary-label">Patient ID</span>
                <span class="summary-value">{patient['patient_id']}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Patient Name</span>
                <span class="summary-value">{patient['name']}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">DR Grade</span>
                <span class="summary-value">Grade {grade} — {class_full}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Confidence</span>
                <span class="summary-value">{confidence}% {"(DEMO)" if demo_flag else ""}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Risk Level</span>
                <span class="summary-value" style="color:{risk_info['risk_color']}">{risk_info['risk_level']}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Referral</span>
                <span class="summary-value">{risk_info['referral_text']}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Eye Side</span>
                <span class="summary-value">{eye_side} Eye</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Image Quality</span>
                <span class="summary-value">{quality_result.get('overall_status','PASS')}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Action buttons ─────────────────────────────────────────────────────────
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        if st.button("💾 Save Screening", width="stretch", type="primary",
                     key="ai_save"):
            _save_screening(patient_id, quality_result, prediction, risk_info,
                            original_img, demo_flag, eye_side)

    with btn_col2:
        if st.button("📄 Generate Report", width="stretch", key="ai_report"):
            _generate_report_action(patient, quality_result, prediction,
                                    risk_info, gradcam_result, original_img, demo_flag)

    with btn_col3:
        if st.button("🔄 New Screening", width="stretch", key="ai_new"):
            for key in ["quality_result", "original_image", "preprocessed_image",
                        "model_input", "prediction_result", "gradcam_result",
                        "screening_patient_id", "selected_patient_id", "current_screening_id"]:
                st.session_state.pop(key, None)
            st.session_state["page"] = "New Screening"
            st.rerun()


def _save_screening(patient_id, quality_result, prediction, risk_info,
                    original_img, is_demo, eye_side="Unknown"):
    try:
        scr_id = st.session_state.get("current_screening_id") or generate_screening_id()
        st.session_state["current_screening_id"] = scr_id

        # Save image
        img_path = ""
        if original_img:
            img_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, f"{scr_id}.png")
            original_img.save(img_path)

        save_screening(
            screening_id=scr_id,
            patient_id=patient_id,
            image_path=img_path,
            blur_score=quality_result.get("blur_score", 0),
            illumination_score=quality_result.get("illumination_score", 0),
            fov_score=quality_result.get("fov_score", 0),
            quality_status=quality_result.get("overall_status", "PASS"),
            quality_fail_reason="; ".join(quality_result.get("fail_reasons", [])),
            predicted_grade=prediction["grade"],
            predicted_class=prediction["class_name_full"],
            confidence=prediction["confidence"],
            risk_level=risk_info["risk_level"],
            referral_status=risk_info["referral_text"],
            report_path="",
            is_demo=is_demo,
            eye_side=eye_side,
        )
        st.success(f"✅ Screening saved! ID: {scr_id}")
    except Exception as e:
        st.error(f"❌ Save failed: {e}")


def _generate_report_action(patient, quality_result, prediction, risk_info,
                             gradcam_result, original_img, is_demo):
    try:
        scr_id = st.session_state.get("current_screening_id") or generate_screening_id()
        st.session_state["current_screening_id"] = scr_id

        screening_data = {
            "screening_id": scr_id,
            "screening_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "blur_score": quality_result.get("blur_score", 0),
            "illumination_score": quality_result.get("illumination_score", 0),
            "fov_score": quality_result.get("fov_score", 0),
            "quality_status": quality_result.get("overall_status", "PASS"),
            "predicted_grade": prediction["grade"],
            "predicted_class": prediction["class_name_full"],
            "confidence": prediction["confidence"],
            "risk_level": risk_info["risk_level"],
            "referral_status": risk_info["referral_text"],
            "is_demo": is_demo,
        }

        with st.spinner("Generating PDF report..."):
            report_path = generate_report(
                patient=patient or {"patient_id": "UNKNOWN", "name": "Unknown"},
                screening=screening_data,
                gradcam_result=gradcam_result,
                original_img=original_img,
            )

        if report_path and os.path.exists(report_path):
            with open(report_path, "rb") as f:
                pdf_bytes = f.read()
            st.success(f"✅ Report generated: {os.path.basename(report_path)}")
            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_bytes,
                file_name=os.path.basename(report_path),
                mime="application/pdf",
                key="download_pdf_btn"
            )
        else:
            st.error("❌ Report generation failed. Check that ReportLab is installed.")
    except Exception as e:
        st.error(f"❌ Report error: {e}")
