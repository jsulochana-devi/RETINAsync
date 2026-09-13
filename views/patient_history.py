"""
pages/patient_history.py
Patient screening history view.
"""

import csv
import io
import os

import streamlit as st
from backend.database import search_patients, get_screenings_for_patient, get_patient
from backend.risk import DR_CLASSES


def render():
    st.markdown('<div class="page-header"><h2>📋 Patient History</h2></div>', unsafe_allow_html=True)

    # Search bar
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        query = st.text_input("🔎 Search by Patient ID or Name",
                               placeholder="e.g. P1001 or Demo Patient",
                               key="history_search")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Search", width="stretch", key="history_search_btn")

    if not query:
        # Show all patients by default
        patients = search_patients("")
    else:
        patients = search_patients(query)

    if not patients:
        st.info("No patients found. Try a different search term.")
        return

    st.markdown(f"**{len(patients)} patient(s) found**")

    for patient in patients:
        pid = patient["patient_id"]
        screenings = get_screenings_for_patient(pid)

        with st.expander(
            f"👤 {patient['name']} ({pid}) — Age: {patient['age']} | {len(screenings)} screening(s)",
            expanded=False
        ):
            # Patient info
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="info-card">
                    <strong>Patient ID:</strong> {pid}<br>
                    <strong>Name:</strong> {patient['name']}<br>
                    <strong>Age:</strong> {patient['age']}<br>
                    <strong>Gender:</strong> {patient['gender']}
                </div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="info-card">
                    <strong>Phone:</strong> {patient.get('phone') or '—'}<br>
                    <strong>Village:</strong> {patient.get('village') or '—'}<br>
                    <strong>Registered:</strong> {patient.get('registration_date','—')}
                </div>""", unsafe_allow_html=True)

            if not screenings:
                st.info("No screenings recorded for this patient.")
                if st.button(f"📷 Start Screening", key=f"hist_screen_{pid}"):
                    st.session_state["selected_patient_id"] = pid
                    st.session_state["page"] = "New Screening"
                    st.rerun()
                continue

            # Screening history table
            st.markdown("#### Screening History")

            rows_html = ""
            for s in screenings:
                grade = s.get("predicted_grade")
                risk = s.get("risk_level", "—")
                conf = s.get("confidence", "—")
                q_status = s.get("quality_status", "—")
                referral = s.get("referral_status", "—")
                date = s.get("screening_date", "—")
                is_demo = s.get("is_demo", 0)
                eye_side = s.get("eye_side") or "—"

                grade_str = f"Grade {grade} — {DR_CLASSES.get(grade, '—')}" if grade is not None else "—"

                risk_color = {"Low": "#22c55e", "Low–Moderate": "#84cc16",
                              "Moderate": "#f59e0b", "High": "#ef4444",
                              "Very High": "#7c3aed"}.get(risk, "#94a3b8")

                q_badge = (
                    '<span class="badge-green">PASS</span>' if q_status == "PASS"
                    else '<span class="badge-yellow">BORDERLINE</span>' if q_status == "BORDERLINE"
                    else '<span class="badge-red">FAIL</span>'
                )

                demo_tag = ' <span class="badge-demo">DEMO</span>' if is_demo else ""

                rows_html += f"""
                <tr>
                    <td>{date[:16] if date else "—"}</td>
                    <td>{grade_str}{demo_tag}</td>
                    <td>{eye_side}</td>
                    <td>{conf}%</td>
                    <td style="color:{risk_color};font-weight:600">{risk}</td>
                    <td>{referral}</td>
                    <td>{q_badge}</td>
                    <td>{s.get('screening_id','—')}</td>
                </tr>"""

            st.markdown(f"""
            <div style="overflow-x:auto">
            <table class="history-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Grade</th>
                        <th>Eye</th>
                        <th>Confidence</th>
                        <th>Risk</th>
                        <th>Referral</th>
                        <th>Quality</th>
                        <th>Screening ID</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Add View Details buttons for each screening
            for s in screenings:
                scr_id = s.get('screening_id')
                if scr_id:
                    if st.button("🔍 View Details", key=f"view_details_{scr_id}"):
                        st.session_state["selected_screening_id"] = scr_id
                        st.session_state["page"] = "AI Analysis"
                        st.rerun()

            col_x, col_y, col_z = st.columns([1, 1, 2])
            with col_x:
                if st.button(f"📷 New Screening", key=f"hist_new_{pid}"):
                    st.session_state["selected_patient_id"] = pid
                    st.session_state["page"] = "New Screening"
                    st.rerun()

            with col_y:
                # CSV export for this patient
                try:
                    csv_buf = io.StringIO()
                    fieldnames = [
                        "screening_id", "screening_date", "eye_side",
                        "predicted_grade", "predicted_class", "confidence",
                        "risk_level", "referral_status",
                        "quality_status", "blur_score", "illumination_score",
                        "fov_score", "is_demo"
                    ]
                    writer = csv.DictWriter(csv_buf, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(screenings)
                    st.download_button(
                        label="📊 Export CSV",
                        data=csv_buf.getvalue().encode("utf-8"),
                        file_name=f"{pid}_screenings.csv",
                        mime="text/csv",
                        key=f"hist_csv_{pid}",
                        width="stretch",
                    )
                except Exception:
                    pass

            # Show report download links if reports exist
            reports_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "reports"
            )
            available_reports = []
            for s in screenings:
                scr_id = s.get("screening_id", "")
                report_file = os.path.join(reports_dir, f"RETINAsync_Report_{scr_id}.pdf")
                if os.path.exists(report_file):
                    available_reports.append((scr_id, report_file))

            if available_reports:
                st.markdown("**📄 Saved Reports:**")
                for scr_id, report_file in available_reports:
                    try:
                        with open(report_file, "rb") as f:
                            pdf_bytes = f.read()
                        st.download_button(
                            label=f"⬇️ Report {scr_id}",
                            data=pdf_bytes,
                            file_name=f"RETINAsync_Report_{scr_id}.pdf",
                            mime="application/pdf",
                            key=f"hist_report_{scr_id}",
                        )
                    except Exception:
                        pass
