"""
pages/patient_registration.py
Patient registration form.
"""

import streamlit as st
from backend.database import save_patient, generate_patient_id, get_patient


def render():
    st.markdown('<div class="page-header"><h2>👤 Patient Registration</h2></div>', unsafe_allow_html=True)

    demo_mode = st.session_state.get("demo_mode", False)

    # Auto-generate patient ID
    new_pid = generate_patient_id()

    st.markdown(f"""
    <div class="info-card">
        <strong>Auto-Generated Patient ID:</strong>
        <span class="badge-blue">{new_pid}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    with st.form("registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Patient Name *", placeholder="Enter full name",
                                 value="Demo Patient D" if demo_mode else "")
            age = st.number_input("Age *", min_value=1, max_value=120,
                                  value=50 if demo_mode else 30)
            gender = st.selectbox("Gender *", ["Select", "Male", "Female", "Other"],
                                  index=1 if demo_mode else 0)

        with col2:
            phone = st.text_input("Phone Number (optional)",
                                  placeholder="+91 XXXXXXXXXX",
                                  value="9876543213" if demo_mode else "")
            village = st.text_input("Village / Location (optional)",
                                    placeholder="e.g., Vijayawada",
                                    value="Guntur" if demo_mode else "")
            states_list = ["Andhra Pradesh", "Telangana", "Tamil Nadu", "Karnataka", "Maharashtra", "Kerala", "Other"]
            state_val = st.selectbox("State", states_list, index=0)

        st.markdown("")
        submitted = st.form_submit_button("✅ Register Patient", width="stretch",
                                          type="primary")

    if submitted:
        # Validate
        errors = []
        if not name.strip():
            errors.append("Patient name is required.")
        if gender == "Select":
            errors.append("Please select a gender.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            try:
                save_patient(
                    patient_id=new_pid,
                    name=name.strip(),
                    age=int(age),
                    gender=gender,
                    phone=phone.strip() if phone else None,
                    village=village.strip() if village else None,
                    state=state_val,
                )
                st.session_state["registered_patient_id"] = new_pid
                st.session_state["registered_patient_name"] = name.strip()

                st.markdown(f"""
                <div class="success-card">
                    <div class="success-icon">✅</div>
                    <div class="success-title">Patient Registered Successfully!</div>
                    <div class="success-detail">
                        <strong>Patient ID:</strong> {new_pid} &nbsp;&nbsp;
                        <strong>Name:</strong> {name.strip()}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📷 Start Screening for this Patient",
                                 width="stretch", type="primary",
                                 key="reg_go_screening"):
                        st.session_state["selected_patient_id"] = new_pid
                        st.session_state["page"] = "New Screening"
                        st.rerun()
                with col_b:
                    if st.button("👤 Register Another Patient",
                                 width="stretch", key="reg_another"):
                        st.rerun()
            except Exception as ex:
                st.error(f"❌ Registration failed: {ex}")

    # Quick lookup
    st.markdown("---")
    st.markdown("### 🔎 Quick Patient Lookup")
    lookup_id = st.text_input("Enter Patient ID to look up", placeholder="e.g. P1001",
                               key="lookup_pid")
    if lookup_id:
        p = get_patient(lookup_id.strip())
        if p:
            st.markdown(f"""
            <div class="info-card">
                <strong>Found:</strong> {p['name']} | Age: {p['age']} | Gender: {p['gender']} |
                Village: {p.get('village','—')} | Registered: {p['registration_date']}
            </div>""", unsafe_allow_html=True)
            if st.button("📷 Screen this Patient", key="lookup_screen"):
                st.session_state["selected_patient_id"] = p["patient_id"]
                st.session_state["page"] = "New Screening"
                st.rerun()
        else:
            st.warning(f"No patient found with ID '{lookup_id.strip()}'")
