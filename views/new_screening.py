"""
pages/new_screening.py
Image upload, quality gate, and preprocessing.
"""

import streamlit as st
import numpy as np
from PIL import Image
import io

from backend.quality_gate import run_quality_gate
from backend.preprocessing import preprocess_image
from backend.database import get_patient, get_all_patients


def _quality_badge(status: str) -> str:
    if status == "PASS":
        return '<span class="badge-green">✓ PASS</span>'
    elif status == "BORDERLINE":
        return '<span class="badge-yellow">⚠ BORDERLINE</span>'
    else:
        return '<span class="badge-red">✗ FAIL</span>'


def _overall_banner(status: str) -> str:
    if status == "PASS":
        return '<div class="quality-banner quality-pass">✅ IMAGE QUALITY ACCEPTED — Ready for AI Analysis</div>'
    elif status == "BORDERLINE":
        return '<div class="quality-banner quality-warn">⚠️ IMAGE QUALITY BORDERLINE — Screening will proceed with caution</div>'
    else:
        return '<div class="quality-banner quality-fail">❌ IMAGE QUALITY FAILED — Please recapture the image</div>'


def render():
    st.markdown('<div class="page-header"><h2>📷 New Screening</h2></div>', unsafe_allow_html=True)

    # ── Step 1: Select Patient ─────────────────────────────────────────────────
    st.markdown("### Step 1 — Select Patient")

    preselected = st.session_state.get("selected_patient_id", "")
    patients = get_all_patients()
    patient_options = {p["patient_id"]: f"{p['patient_id']} — {p['name']}" for p in patients}

    if not patient_options:
        st.warning("No patients registered yet. Please register a patient first.")
        if st.button("👤 Register Patient", key="ns_go_register"):
            st.session_state["page"] = "Patient Registration"
            st.rerun()
        return

    pid_list = list(patient_options.keys())
    default_idx = pid_list.index(preselected) if preselected in pid_list else 0

    selected_pid = st.selectbox(
        "Select Patient",
        options=pid_list,
        format_func=lambda x: patient_options[x],
        index=default_idx,
        key="ns_patient_select"
    )

    patient = get_patient(selected_pid)
    if patient:
        st.markdown(f"""
        <div class="info-card">
            👤 <strong>{patient['name']}</strong> &nbsp;|&nbsp;
            Age: {patient['age']} &nbsp;|&nbsp; Gender: {patient['gender']}
            {f"&nbsp;|&nbsp; Village: {patient['village']}" if patient.get('village') else ""}
        </div>""", unsafe_allow_html=True)

    # Eye side selection
    eye_side = st.radio(
        "👁️ Eye Being Screened",
        ["Right Eye (OD)", "Left Eye (OS)"],
        horizontal=True,
        key="ns_eye_side"
    )
    st.session_state["screening_eye_side"] = "Right" if "Right" in eye_side else "Left"

    st.markdown("---")

    # ── Step 2: Upload Image ───────────────────────────────────────────────────
    st.markdown("### Step 2 — Upload Retinal Image")

    demo_mode = st.session_state.get("demo_mode", False)
    selected_demo = None

    if demo_mode:
        st.markdown("""
        <div class="demo-banner">🎭 DEMO MODE — Select a demo case or upload an image</div>
        """, unsafe_allow_html=True)
        demo_choice = st.radio(
            "Demo Cases",
            ["Upload my own image", "Demo Case 1: No DR", "Demo Case 2: Moderate DR", "Demo Case 3: Severe DR"],
            horizontal=True,
            key="demo_case_radio"
        )
        if demo_choice != "Upload my own image":
            selected_demo = demo_choice

    uploaded_file = None
    if selected_demo is None:
        uploaded_file = st.file_uploader(
            "Upload Fundus Image (JPG / JPEG / PNG)",
            type=["jpg", "jpeg", "png"],
            help="Please upload a clear, well-lit retinal fundus image.",
            key="ns_uploader"
        )

    # ── Load image ─────────────────────────────────────────────────────────────
    pil_image = None
    image_source = None

    if selected_demo:
        # Generate synthetic fundus-like demo image
        pil_image = _create_demo_image(selected_demo)
        image_source = selected_demo
    elif uploaded_file:
        try:
            pil_image = Image.open(uploaded_file).convert("RGB")
            image_source = uploaded_file.name
        except Exception as e:
            st.error(f"❌ Could not open image: {e}")
            return

    if pil_image is None:
        st.info("👆 Please upload a retinal fundus image to begin screening.")
        return

    st.markdown("---")

    # ── Step 3: Display & Quality Gate ────────────────────────────────────────
    st.markdown("### Step 3 — Image Quality Check")

    col_orig, col_info = st.columns([1, 1])
    with col_orig:
        st.markdown("**Uploaded Image**")
        st.image(pil_image, width="stretch")
        st.caption(f"Source: {image_source}")

    with col_info:
        st.markdown("**Running Quality Gate...**")
        img_array = np.array(pil_image)
        qr = run_quality_gate(img_array)

        # Display quality metrics table
        st.markdown(f"""
        <table class="quality-table">
            <thead>
                <tr><th>Metric</th><th>Score</th><th>Status</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td>🔍 Blur (Sharpness)</td>
                    <td>{qr['blur_score']}</td>
                    <td>{_quality_badge(qr['blur_status'])}</td>
                </tr>
                <tr>
                    <td>💡 Illumination</td>
                    <td>{qr['illumination_score']}</td>
                    <td>{_quality_badge(qr['illumination_status'])}</td>
                </tr>
                <tr>
                    <td>📐 Field of View</td>
                    <td>{qr['fov_score']}%</td>
                    <td>{_quality_badge(qr['fov_status'])}</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)

    # Store quality results
    st.session_state["quality_result"] = qr
    st.session_state["original_image"] = pil_image
    st.session_state["screening_patient_id"] = selected_pid

    st.markdown("")
    st.markdown(_overall_banner(qr["overall_status"]), unsafe_allow_html=True)

    if not qr["can_proceed"]:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ❌ Quality Failure Reasons:")
        for reason in qr["fail_reasons"]:
            st.markdown(f"- ⚠️ {reason}")

        st.markdown("""
        <div class="advice-card">
            <strong>Recommended Actions:</strong><br>
            • Ensure the camera is clean and properly focused.<br>
            • Check that the room is adequately lit.<br>
            • Reposition the camera to center the fundus image.<br>
            • Ask the patient to remain still during capture.
        </div>""", unsafe_allow_html=True)

        if st.button("🔄 Upload Another Image", type="primary", key="ns_retry"):
            # Clear cached state and rerun
            for key in ["quality_result", "preprocessed_image", "model_input", "prediction_result", "gradcam_result"]:
                st.session_state.pop(key, None)
            st.rerun()
        return

    # ── Step 4: Preprocessing ─────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Step 4 — Image Preprocessing")

    with st.spinner("Preprocessing image..."):
        processed_pil, description, model_input = preprocess_image(pil_image)

    st.session_state["preprocessed_image"] = processed_pil
    st.session_state["model_input"] = model_input

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Original Image**")
        st.image(pil_image, width="stretch")
    with col_b:
        st.markdown("**Preprocessed Image**")
        st.image(processed_pil, width="stretch")

    st.markdown(f"""
    <div class="info-card">
        <strong>Preprocessing Pipeline:</strong><br>
        <small>{description}</small><br><br>
        Preprocessing improves contrast and highlights clinically relevant retinal structures,
        enabling more reliable AI analysis.
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Proceed button ─────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("🧠 Proceed to AI Analysis", width="stretch",
                     type="primary", key="ns_go_ai"):
            st.session_state["page"] = "AI Analysis"
            st.rerun()


def _create_demo_image(demo_label: str) -> Image.Image:
    """
    Generate a synthetic circular fundus-like image for demo purposes.
    This is clearly a synthetic demo image, not a real retinal photograph.
    """
    import numpy as np
    size = 512
    img = np.zeros((size, size, 3), dtype=np.uint8)

    # Dark background
    img[:, :] = [10, 5, 5]

    # Circular fundus region
    cx, cy, r = size // 2, size // 2, size // 2 - 20
    Y, X = np.ogrid[:size, :size]
    mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r ** 2

    # Base fundus color (reddish-orange)
    base = np.array([180, 80, 40], dtype=np.float32)
    noise = np.random.RandomState(42).randint(-20, 20, (size, size, 3)).astype(np.float32)
    fundus = np.clip(base + noise, 0, 255).astype(np.uint8)
    img[mask] = fundus[mask]

    # Optic disc (bright circle)
    od_cx, od_cy, od_r = int(cx + 0.15 * r), cy, int(0.12 * r)
    od_mask = (X - od_cx) ** 2 + (Y - od_cy) ** 2 <= od_r ** 2
    img[od_mask & mask] = [255, 240, 200]

    # Vessels (dark lines)
    import cv2
    for i in range(5):
        angle = i * 36
        x2 = int(cx + r * 0.8 * np.cos(np.radians(angle)))
        y2 = int(cy + r * 0.8 * np.sin(np.radians(angle)))
        cv2.line(img, (od_cx, od_cy), (x2, y2), (100, 30, 20), 2)

    # Add lesion dots for higher grades
    rng = np.random.RandomState(99)
    if "Moderate" in demo_label or "Severe" in demo_label:
        for _ in range(20 if "Moderate" in demo_label else 50):
            px = rng.randint(cx - r, cx + r)
            py = rng.randint(cy - r, cy + r)
            if (px - cx) ** 2 + (py - cy) ** 2 < r ** 2:
                cv2.circle(img, (px, py), rng.randint(3, 7), (255, 255, 200), -1)

    return Image.fromarray(img)
