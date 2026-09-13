import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from backend.database import (
    get_dashboard_stats, get_recent_screenings, get_priority_referrals,
    get_screenings_date_series, get_all_screenings_csv, get_state_wise_stats
)
from backend.risk import DR_CLASSES
from backend.i18n import t


def render():
    lang = st.session_state.get("language", "English")
    st.markdown(f'<div class="page-header"><h2>📊 {t("nav_dashboard", lang)}</h2></div>',
                unsafe_allow_html=True)

    try:
        stats = get_dashboard_stats()
        recent = get_recent_screenings(10)
        priority = get_priority_referrals(5)
        date_series = get_screenings_date_series()
        state_stats = get_state_wise_stats()
    except Exception as e:
        st.error(f"Dashboard error: {e}")
        return

    # ── KPI Cards ──────────────────────────────────────────────────────────────
    st.markdown("### Key Metrics")
    c1, c2, c3, c4 = st.columns(4)

    kpis = [
        (c1, "👥", t("patients_screened", lang),  str(stats["total_patients"]),  "#1a73a7"),
        (c2, "🔬", t("total_screenings", lang),   str(stats["total_screenings"]), "#0891b2"),
        (c3, "✅", t("quality_pass_rate", lang),  f"{stats['quality_pass_rate']}%", "#16a34a"),
        (c4, "🚨", t("referrals_required", lang), str(stats["referrals_needed"]), "#dc2626"),
    ]

    for col, icon, label, value, color in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top: 4px solid {color}">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-value" style="color:{color}">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── State-Wise Report Section ──────────────────────────────────────────────
    st.markdown(f"### 🗺️ {t('state_wise_report', lang)}")
    if state_stats:
        col_st_left, col_st_right = st.columns([3, 2])
        states = [s["state_name"] for s in state_stats]
        totals = [s["total_screenings"] for s in state_stats]
        high_risks = [s["high_risk_count"] for s in state_stats]

        with col_st_left:
            fig_state = go.Figure()
            fig_state.add_trace(go.Bar(
                x=states, y=totals, name="Total Screenings", marker_color="#38bdf8"
            ))
            fig_state.add_trace(go.Bar(
                x=states, y=high_risks, name="High Risk Referrals", marker_color="#ef4444"
            ))
            fig_state.update_layout(
                barmode="group",
                xaxis_title="State",
                yaxis_title="Count",
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font=dict(color="#e2e8f0"),
                margin=dict(t=20, b=20, l=20, r=20),
                height=300,
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig_state, width="stretch")

        with col_st_right:
            st_rows = ""
            for s in state_stats:
                st_rows += f"""<tr>
                    <td><strong>{s['state_name']}</strong></td>
                    <td style="text-align:center">{s['total_screenings']}</td>
                    <td style="text-align:center; color:#f87171; font-weight:700">{s['high_risk_count']}</td>
                </tr>"""
            st.markdown(f"""
            <div style="overflow-x:auto">
            <table class="history-table">
                <thead><tr>
                    <th>State</th><th>Total Screenings</th><th>High Risk Referrals</th>
                </tr></thead>
                <tbody>{st_rows}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No state data available yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ─────────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### DR Grade Distribution")
        grade_dist = stats["grade_distribution"]
        labels = [f"Grade {g}: {DR_CLASSES[g]}" for g in range(5)]
        values = [grade_dist[g] for g in range(5)]
        colors = ["#22c55e", "#84cc16", "#f59e0b", "#ef4444", "#7c3aed"]

        fig_bar = go.Figure(go.Bar(
            x=[f"Grade {g}" for g in range(5)],
            y=values,
            marker_color=colors,
            text=values,
            textposition="outside",
        ))
        fig_bar.update_layout(
            xaxis_title="DR Grade",
            yaxis_title="Number of Screenings",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"),
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            showlegend=False,
        )
        st.plotly_chart(fig_bar, width="stretch")

    with col_right:
        st.markdown("### Grade Breakdown")
        non_zero_labels = [labels[i] for i in range(5) if values[i] > 0]
        non_zero_values = [values[i] for i in range(5) if values[i] > 0]
        non_zero_colors = [colors[i] for i in range(5) if values[i] > 0]

        if sum(non_zero_values) > 0:
            fig_pie = go.Figure(go.Pie(
                labels=non_zero_labels,
                values=non_zero_values,
                marker=dict(colors=non_zero_colors),
                hole=0.45,
            ))
            fig_pie.update_layout(
                plot_bgcolor="#0f172a",
                paper_bgcolor="#0f172a",
                font=dict(color="#e2e8f0"),
                margin=dict(t=20, b=20, l=20, r=20),
                height=300,
                showlegend=True,
                legend=dict(font=dict(size=9)),
            )
            st.plotly_chart(fig_pie, width="stretch")
        else:
            st.info("No screening data yet.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Screening Trends ───────────────────────────────────────────────────────
    if date_series:
        st.markdown("### 📈 Screening Trends Over Time")
        dates = [d["day"] for d in date_series]
        counts = [d["count"] for d in date_series]
        fig_trend = go.Figure(go.Scatter(
            x=dates,
            y=counts,
            mode="lines+markers",
            line=dict(color="#38bdf8", width=2),
            marker=dict(color="#38bdf8", size=7),
            fill="tozeroy",
            fillcolor="rgba(56,189,248,0.08)",
            name="Screenings",
        ))
        fig_trend.update_layout(
            xaxis_title="Date",
            yaxis_title="Screenings (PASS)",
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"),
            margin=dict(t=20, b=20, l=20, r=20),
            height=250,
            showlegend=False,
        )
        st.plotly_chart(fig_trend, width="stretch")
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent Screenings ──────────────────────────────────────────────────────
    col_rec, col_pri = st.columns([3, 2])

    with col_rec:
        st.markdown("### 🕒 Recent Screenings")
        if recent:
            rows = ""
            for s in recent:
                grade = s.get("predicted_grade")
                grade_str = f"G{grade}" if grade is not None else "—"
                risk = s.get("risk_level", "—")
                risk_color = {"Low": "#22c55e", "Low–Moderate": "#84cc16",
                              "Moderate": "#f59e0b", "High": "#ef4444",
                              "Very High": "#7c3aed"}.get(risk, "#94a3b8")
                date = s.get("screening_date", "—")[:16]
                demo = "✦" if s.get("is_demo") else ""
                rows += f"""<tr>
                    <td>{s.get('screening_id','—')}</td>
                    <td>{s.get('patient_name','—')}</td>
                    <td>{grade_str} {demo}</td>
                    <td style="color:{risk_color};font-weight:600">{risk}</td>
                    <td>{date}</td>
                </tr>"""
            st.markdown(f"""
            <div style="overflow-x:auto">
            <table class="history-table">
                <thead><tr>
                    <th>ID</th><th>Patient</th><th>Grade</th><th>Risk</th><th>Date</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("No screenings recorded yet.")

    with col_pri:
        st.markdown("### 🚨 Priority Referrals")
        if priority:
            for s in priority:
                risk = s.get("risk_level", "—")
                risk_color = "#ef4444" if risk == "High" else "#7c3aed"
                st.markdown(f"""
                <div class="priority-card" style="border-left:4px solid {risk_color}">
                    <div class="priority-name">{s.get('patient_name','—')}</div>
                    <div class="priority-id">{s.get('patient_id','—')}</div>
                    <div class="priority-risk" style="color:{risk_color}">{risk}</div>
                    <div class="priority-ref">{s.get('referral_status','—')}</div>
                    <div class="priority-date">{s.get('screening_date','—')[:16]}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("✅ No high-priority referrals outstanding.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CSV Export ─────────────────────────────────────────────────────────────
    st.markdown("### 📥 Export Data")
    col_exp, _ = st.columns([1, 3])
    with col_exp:
        try:
            import csv, io as _io
            rows = get_all_screenings_csv()
            if rows:
                csv_buf = _io.StringIO()
                writer = csv.DictWriter(csv_buf, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                st.download_button(
                    label="⬇️ Download All Screenings (CSV)",
                    data=csv_buf.getvalue().encode("utf-8"),
                    file_name="retinasync_screenings.csv",
                    mime="text/csv",
                    width="stretch",
                )
            else:
                st.info("No screening data to export.")
        except Exception as e:
            st.error(f"Export error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("❆ DEMO = demonstration screening data. Dashboard powered by local SQLite database.")
