"""
app.py — RETINAsync Main Entry Point
Explainable AI for Diabetic Retinopathy Screening in Rural India
Smart India Hackathon 2026 | SIH26038

ARCHITECTURE NOTE:
  All UI page modules live in views/ (NOT pages/) to prevent Streamlit's
  automatic multipage file-based routing from hijacking navigation.
  All routing is done via st.session_state["page"] in this single entry point.
"""

import os
import sys

# Ensure module import paths resolve correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from backend.database import init_db, authenticate_user
from backend.i18n import t

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RETINAsync — DR Screening",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Premium CSS ────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Root & Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Dark App Background ── */
.stApp {
    background: #050d1a !important;
    background-image:
        radial-gradient(ellipse at 20% 10%, rgba(56,189,248,0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(129,140,248,0.04) 0%, transparent 50%) !important;
    color: #e2e8f0 !important;
    min-height: 100vh;
}

/* ── Hide Streamlit Chrome ── */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Hide Sidebar & Expand Full Width ── */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Main Content Padding ── */
.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1400px !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
    letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0e7490 0%, #0891b2 60%, #06b6d4 100%) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(8,145,178,0.25), 0 1px 3px rgba(0,0,0,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(8,145,178,0.35), 0 2px 6px rgba(0,0,0,0.3) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0px) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    color: #94a3b8 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(56,189,248,0.08) !important;
    color: #38bdf8 !important;
    border-color: rgba(56,189,248,0.3) !important;
}

/* ── Nav button active state ── */
.nav-btn-active > .stButton > button {
    background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(56,189,248,0.08)) !important;
    color: #38bdf8 !important;
    border: 1px solid rgba(56,189,248,0.35) !important;
    box-shadow: 0 0 0 1px rgba(56,189,248,0.1) inset !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 9px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
    background: rgba(56,189,248,0.04) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 9px !important;
    color: #e2e8f0 !important;
}

/* ── Form container ── */
[data-testid="stForm"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    padding: 1.5rem !important;
}

/* ── Radio / Toggle ── */
.stRadio > div { gap: 8px !important; }
.stRadio label {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    padding: 6px 14px !important;
    color: #94a3b8 !important;
    transition: all 0.15s !important;
    cursor: pointer !important;
}
.stRadio label:hover {
    border-color: rgba(56,189,248,0.3) !important;
    color: #38bdf8 !important;
}

/* ============================================================
   SIDEBAR COMPONENTS
   ============================================================ */
.sidebar-logo-wrap {
    padding: 24px 20px 16px;
    border-bottom: 1px solid rgba(56,189,248,0.1);
    margin-bottom: 8px;
}
.sidebar-logo-text {
    font-size: 1.45rem;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.sidebar-tagline {
    font-size: 0.68rem;
    color: #334155;
    margin-top: 3px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.sidebar-user {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px;
    margin: 4px 0 12px;
    background: rgba(56,189,248,0.04);
    border-radius: 10px;
    font-size: 0.82rem;
    color: #64748b;
}
.sidebar-user strong { color: #94a3b8; }
.sidebar-nav-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #334155;
    padding: 8px 20px 4px;
}
.sidebar-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin: 10px 12px;
}
.sidebar-status {
    margin: 4px 12px;
    padding: 8px 12px;
    border-radius: 8px;
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.15);
    font-size: 0.72rem;
    color: #34d399;
    text-align: center;
    letter-spacing: 0.03em;
}

/* ============================================================
   PAGE HEADER
   ============================================================ */
.page-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(56,189,248,0.12);
}
.page-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
    letter-spacing: -0.02em;
}

/* ============================================================
   HERO SECTION
   ============================================================ */
.hero-section {
    background: linear-gradient(135deg, #071020 0%, #0e2040 50%, #081830 100%);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 20px;
    padding: 52px 40px 44px;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin-bottom: 28px;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -30%;
    right: -10%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(56,189,248,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -20%;
    left: 5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(129,140,248,0.05) 0%, transparent 70%);
    pointer-events: none;
}
.hero-logo {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 60%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    letter-spacing: -0.03em;
    line-height: 1.1;
}
.hero-tagline {
    font-size: 1.05rem;
    color: #64748b;
    margin-bottom: 6px;
    font-weight: 400;
}
.hero-subtitle {
    font-size: 0.85rem;
    font-weight: 600;
    color: #38bdf8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 18px;
}
.prototype-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 0.78rem;
    color: #7dd3fc;
    letter-spacing: 0.02em;
}

/* ============================================================
   STAT / KPI CARDS
   ============================================================ */
.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.stat-card:hover {
    border-color: rgba(56,189,248,0.2);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.2);
}
.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    color: #38bdf8;
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
}
.stat-label {
    font-size: 0.75rem;
    color: #475569;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.kpi-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: all 0.2s ease;
    border-top-width: 3px;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    border-color: rgba(56,189,248,0.2);
    border-top-width: 3px;
}
.kpi-icon { font-size: 1.6rem; margin-bottom: 8px; }
.kpi-value { font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 6px; letter-spacing: -0.03em; }
.kpi-label { font-size: 0.75rem; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; }

/* ============================================================
   FEATURE CARDS
   ============================================================ */
.feature-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px 16px;
    text-align: center;
    transition: all 0.2s ease;
    height: 165px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.feature-card:hover {
    border-color: rgba(56,189,248,0.3);
    background: rgba(56,189,248,0.04);
    transform: translateY(-3px);
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}
.feature-icon { font-size: 2rem; margin-bottom: 10px; }
.feature-title { font-size: 0.85rem; font-weight: 700; color: #e2e8f0; margin-bottom: 6px; }
.feature-desc { font-size: 0.75rem; color: #475569; line-height: 1.5; }

/* ============================================================
   PIPELINE BAR
   ============================================================ */
.pipeline-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    flex-wrap: wrap;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 18px;
    margin: 4px 0;
}
.pipeline-step {
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 9px;
    padding: 10px 14px;
    text-align: center;
    font-size: 0.78rem;
    color: #cbd5e1;
    min-width: 80px;
    line-height: 1.5;
}
.pipeline-arrow { color: rgba(56,189,248,0.5); font-size: 1rem; }

/* ============================================================
   INFO / RESULT CARDS
   ============================================================ */
.info-card {
    background: rgba(56,189,248,0.05);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 11px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #cbd5e1;
    margin: 6px 0;
    line-height: 1.7;
}
.success-card {
    background: rgba(34,197,94,0.06);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 14px;
    padding: 28px;
    text-align: center;
}
.success-icon { font-size: 2.5rem; margin-bottom: 10px; }
.success-title { font-size: 1.15rem; font-weight: 700; color: #4ade80; margin-bottom: 8px; }
.success-detail { font-size: 0.88rem; color: #64748b; }

.result-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
}
.result-label {
    font-size: 0.68rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 10px;
    font-weight: 700;
}
.result-grade {
    font-size: 2rem;
    font-weight: 800;
    color: #38bdf8;
    line-height: 1.1;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
}
.result-class { font-size: 0.82rem; color: #64748b; }
.demo-label {
    display: inline-block;
    margin-top: 8px;
    background: rgba(245,158,11,0.12);
    border: 1px solid rgba(245,158,11,0.3);
    color: #fbbf24;
    border-radius: 5px;
    padding: 2px 8px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
}

/* ============================================================
   RISK CARD
   ============================================================ */
.risk-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 8px 0;
    border-left-width: 4px;
}
.risk-header { font-size: 1.05rem; font-weight: 700; color: #e2e8f0; margin-bottom: 6px; }
.risk-referral { font-size: 0.95rem; color: #cbd5e1; margin-bottom: 8px; font-weight: 500; }
.risk-advice { font-size: 0.85rem; color: #64748b; margin-bottom: 10px; line-height: 1.6; }
.risk-footer {
    font-size: 0.72rem;
    color: #334155;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 10px;
    line-height: 1.5;
}

/* ============================================================
   QUALITY GATE
   ============================================================ */
.quality-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
}
.quality-table th {
    background: rgba(15,52,96,0.5);
    color: #64748b;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.quality-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #e2e8f0;
}
.quality-banner {
    border-radius: 11px;
    padding: 14px 20px;
    font-size: 0.95rem;
    font-weight: 600;
    text-align: center;
    margin: 12px 0;
}
.quality-pass { background: rgba(34,197,94,0.08); border: 1.5px solid rgba(34,197,94,0.3); color: #4ade80; }
.quality-warn { background: rgba(245,158,11,0.08); border: 1.5px solid rgba(245,158,11,0.3); color: #fbbf24; }
.quality-fail { background: rgba(239,68,68,0.08); border: 1.5px solid rgba(239,68,68,0.3); color: #f87171; }

/* ============================================================
   BADGES
   ============================================================ */
.badge-green  { background:rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.35); color:#4ade80; border-radius:6px; padding:3px 10px; font-size:0.75rem; font-weight:700; }
.badge-yellow { background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.35); color:#fbbf24; border-radius:6px; padding:3px 10px; font-size:0.75rem; font-weight:700; }
.badge-red    { background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.35); color:#f87171; border-radius:6px; padding:3px 10px; font-size:0.75rem; font-weight:700; }
.badge-blue   { background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.35); color:#38bdf8; border-radius:6px; padding:3px 10px; font-size:0.82rem; font-weight:700; }
.badge-demo   { background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.35); color:#fbbf24; border-radius:4px; padding:2px 6px; font-size:0.65rem; font-weight:700; letter-spacing:0.06em; }

/* ============================================================
   INFO / DEMO BANNERS
   ============================================================ */
.demo-banner {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px;
    padding: 12px 18px;
    color: #fcd34d;
    font-size: 0.84rem;
    margin: 8px 0;
    line-height: 1.5;
}
.offline-banner {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 10px;
    padding: 14px 18px;
    color: #6ee7b7;
    font-size: 0.84rem;
    line-height: 1.6;
}
.disclaimer-banner {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.2);
    border-radius: 10px;
    padding: 14px 18px;
    color: #fcd34d;
    font-size: 0.84rem;
    line-height: 1.6;
}
.info-banner { border-radius: 10px; padding: 14px 18px; font-size: 0.84rem; line-height: 1.6; }
.advice-card {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.18);
    border-radius: 11px;
    padding: 16px 18px;
    font-size: 0.85rem;
    color: #fca5a5;
    margin: 10px 0;
    line-height: 1.8;
}

/* ============================================================
   SUMMARY / HISTORY TABLE
   ============================================================ */
.summary-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px;
}
.summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.88rem;
}
.summary-row:last-child { border-bottom: none; }
.summary-label { color: #475569; font-weight: 500; }
.summary-value { color: #e2e8f0; font-weight: 600; }

.history-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.history-table th {
    background: rgba(10,30,60,0.8);
    color: #475569;
    padding: 10px 14px;
    text-align: left;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    white-space: nowrap;
}
.history-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #e2e8f0;
    vertical-align: middle;
}
.history-table tr:hover td { background: rgba(56,189,248,0.03); }

/* ============================================================
   PROGRESS STEPS
   ============================================================ */
.progress-bar { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 16px; }
.progress-step {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 0.78rem;
    color: #475569;
}
.progress-step.done {
    background: rgba(34,197,94,0.07);
    border-color: rgba(34,197,94,0.25);
    color: #4ade80;
}

/* ============================================================
   PRIORITY / ABOUT CARDS
   ============================================================ */
.priority-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 11px;
    padding: 14px 16px;
    margin-bottom: 8px;
    border-left-width: 3px;
}
.priority-name { font-weight: 600; color: #e2e8f0; font-size: 0.88rem; }
.priority-id   { font-size: 0.72rem; color: #475569; }
.priority-risk { font-weight: 700; font-size: 0.84rem; margin-top: 4px; }
.priority-ref  { font-size: 0.78rem; color: #64748b; }
.priority-date { font-size: 0.72rem; color: #334155; margin-top: 4px; }

.about-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px;
    font-size: 0.86rem;
    color: #94a3b8;
    line-height: 1.8;
    margin-bottom: 16px;
}
.disclaimer-card {
    background: rgba(239,68,68,0.05);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 14px;
    padding: 24px;
    color: #fca5a5;
    font-size: 0.85rem;
    line-height: 1.8;
}
.disclaimer-card h4 { color: #f87171; margin-bottom: 12px; font-size: 1rem; }

/* ============================================================
   IMAGE LABEL
   ============================================================ */
.img-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #475569;
    text-align: center;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ============================================================
   LOGIN
   ============================================================ */
.login-wrap {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(ellipse at 30% 20%, rgba(56,189,248,0.06) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 80%, rgba(129,140,248,0.05) 0%, transparent 50%);
}
.login-container {
    width: 100%;
    max-width: 420px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 44px 40px;
    box-shadow: 0 25px 80px rgba(0,0,0,0.4);
}
.login-logo {
    font-size: 2.6rem;
    font-weight: 900;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 4px;
    letter-spacing: -0.03em;
}
.login-subtitle { font-size: 0.84rem; color: #475569; margin-bottom: 0; }

/* ============================================================
   SCROLLBAR
   ============================================================ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(56,189,248,0.4); }

/* ============================================================
   PLOTLY CHART CONTAINER
   ============================================================ */
.js-plotly-plot { border-radius: 12px; overflow: hidden; }
</style>
"""

# ── Initialize DB ──────────────────────────────────────────────────────────────
@st.cache_resource
def initialize_db():
    init_db()
    return True

initialize_db()

# ── Session state defaults ────────────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "page": "Home",
        "demo_mode": True,
        "language": "English",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ── Inject CSS ─────────────────────────────────────────────────────────────────
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── Login Screen ───────────────────────────────────────────────────────────────
def show_login():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div style="text-align:center; margin-bottom:28px;">
                <div class="login-logo">👁️ RETINAsync</div>
                <div class="login-subtitle">Explainable AI · Diabetic Retinopathy Screening</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔐 Healthcare Worker Login")
        st.markdown("""
        <div class="demo-banner">
            Demo credentials: <strong>healthworker</strong> / <strong>demo123</strong><br>
            <small style="opacity:0.7">⚠️ Prototype demonstration authentication only.</small>
        </div>""", unsafe_allow_html=True)

        st.markdown("")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="healthworker")
            password = st.text_input("Password", type="password", placeholder="demo123")
            login_btn = st.form_submit_button("🔐 Login", use_container_width=True, type="primary")

        if login_btn:
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                user = authenticate_user(username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = user
                    st.success(f"✅ Welcome, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Use: healthworker / demo123")

        st.markdown("""
        <div style="text-align:center; font-size:0.72rem; color:#1e3a5f; margin-top:20px;">
            RETINAsync · SIH 2026 Prototype · SIH26038<br>Research &amp; demonstration purposes only
        </div>""", unsafe_allow_html=True)


# ── Top Navbar Navigation ──────────────────────────────────────────────────────
def show_navbar():
    lang_current = st.session_state.get("language", "English")
    user = st.session_state.get("user", {})
    user_name = user.get('full_name', 'Health Worker')
    user_role = user.get('role', 'health_worker').replace('_', ' ').title()
    current = st.session_state.get("page", "Home")
    demo_mode = st.session_state.get("demo_mode", True)

    # Top Brand Header & User Info Bar
    c_brand, c_controls = st.columns([3, 2], vertical_alignment="center")

    with c_brand:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:2.2rem; line-height:1;">👁️</span>
            <div>
                <div style="font-size:1.6rem; font-weight:800; background:linear-gradient(135deg,#38bdf8 0%,#818cf8 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-0.02em;">
                    {t('app_title', lang_current)}
                </div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:500; letter-spacing:0.04em;">
                    Capture · Validate · Screen · Explain · Refer
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c_controls:
        sub_c1, sub_c2, sub_c3 = st.columns([1.5, 1.2, 0.8], vertical_alignment="center")
        with sub_c1:
            lang_options = ["English", "తెలుగు (Telugu)", "हिन्दी (Hindi)"]
            try:
                lang_idx = lang_options.index(st.session_state.get("language", "English"))
            except ValueError:
                lang_idx = 0
            lang = st.selectbox(
                f"🌐 {t('language', lang_current)}",
                lang_options,
                index=lang_idx,
                key="lang_select",
                label_visibility="collapsed"
            )
            if lang != st.session_state.get("language"):
                st.session_state["language"] = lang
                st.rerun()

        with sub_c2:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; background:rgba(56,189,248,0.06); padding:6px 12px; border-radius:8px; border:1px solid rgba(56,189,248,0.15);">
                <span style="font-size:1.1rem;">👤</span>
                <div style="line-height:1.2;">
                    <div style="font-size:0.8rem; font-weight:600; color:#e2e8f0;">{user_name}</div>
                    <div style="font-size:0.65rem; color:#94a3b8;">{user_role}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with sub_c3:
            if st.button(f"🚪 {t('logout', lang_current)}", key="logout_btn", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    st.markdown("""<div style="height: 1px; background: rgba(56, 189, 248, 0.15); margin: 12px 0 16px 0;"></div>""", unsafe_allow_html=True)

    # Navigation Menu Buttons in single top row
    nav_items = [
        ("🏠", t("nav_home", lang_current),         "Home"),
        ("👤", t("nav_registration", lang_current), "Patient Registration"),
        ("📷", t("nav_screening", lang_current),    "New Screening"),
        ("🧠", t("nav_ai_analysis", lang_current),   "AI Analysis"),
        ("📋", t("nav_history", lang_current),      "Patient History"),
        ("📊", t("nav_dashboard", lang_current),    "Dashboard"),
        ("ℹ️", t("nav_about", lang_current),        "About"),
    ]

    nav_cols = st.columns(len(nav_items))
    for idx, (icon, label, page_key) in enumerate(nav_items):
        is_active = current == page_key
        btn_type = "primary" if is_active else "secondary"
        with nav_cols[idx]:
            if st.button(
                f"{icon} {label}",
                use_container_width=True,
                type=btn_type,
                key=f"top_nav_{page_key}"
            ):
                st.session_state["page"] = page_key
                st.rerun()

    # Sub-status bar for Demo mode & Offline status
    sub_col1, sub_col2 = st.columns([3, 1], vertical_alignment="center")
    with sub_col1:
        demo = st.toggle(
            f"🎭 {t('demo_mode', lang_current)} — Demo Mode ON (Predictions illustrative only)",
            value=demo_mode,
            key="demo_toggle",
        )
        st.session_state["demo_mode"] = demo

    with sub_col2:
        st.markdown(f"""
        <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); color:#34d399; font-size:0.75rem; border-radius:6px; padding:4px 10px; text-align:center; font-weight:500;">
            📶 {t('offline_ready', lang_current)}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""<div style="height: 1px; background: rgba(255, 255, 255, 0.08); margin: 8px 0 24px 0;"></div>""", unsafe_allow_html=True)


# ── Main Router ────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.get("logged_in"):
        show_login()
        return

    show_navbar()

    page = st.session_state.get("page", "Home")

    try:
        if page == "Home":
            from views import home
            home.render()

        elif page == "Patient Registration":
            from views import patient_registration
            patient_registration.render()

        elif page == "New Screening":
            from views import new_screening
            new_screening.render()

        elif page == "AI Analysis":
            from views import ai_analysis
            ai_analysis.render()

        elif page == "Patient History":
            from views import patient_history
            patient_history.render()

        elif page == "Dashboard":
            from views import dashboard
            dashboard.render()

        elif page == "About":
            from views import about
            about.render()

        else:
            st.warning(f"Unknown page: {page}")

    except Exception as e:
        st.error(f"""
        ❌ **Page Error**

        An unexpected error occurred: `{e}`

        Please try navigating to another page using the sidebar.
        """)
        import traceback
        with st.expander("🔍 Technical Details (for developers)"):
            st.code(traceback.format_exc())


main()
