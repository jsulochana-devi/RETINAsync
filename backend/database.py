"""
backend/database.py
SQLite database operations for RETINAsync.
"""

import sqlite3
import os
from datetime import datetime
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "retinasync.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed demo data."""
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            full_name TEXT,
            role      TEXT DEFAULT 'health_worker'
        )
    """)

    # Patients table
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id        TEXT PRIMARY KEY,
            name              TEXT NOT NULL,
            age               INTEGER,
            gender            TEXT,
            phone             TEXT,
            village           TEXT,
            state             TEXT DEFAULT 'Andhra Pradesh',
            registration_date TEXT
        )
    """)

    # Screenings table
    c.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            screening_id       TEXT PRIMARY KEY,
            patient_id         TEXT,
            image_path         TEXT,
            blur_score         REAL,
            illumination_score REAL,
            fov_score          REAL,
            quality_status     TEXT,
            quality_fail_reason TEXT,
            predicted_grade    INTEGER,
            predicted_class    TEXT,
            confidence         REAL,
            risk_level         TEXT,
            referral_status    TEXT,
            report_path        TEXT,
            is_demo            INTEGER DEFAULT 0,
            screening_date     TEXT,
            eye_side           TEXT DEFAULT 'Unknown',
            state              TEXT DEFAULT 'Andhra Pradesh',
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
        )
    """)

    # Migrate: add eye_side and state columns if missing
    try:
        c.execute("ALTER TABLE screenings ADD COLUMN eye_side TEXT DEFAULT 'Unknown'")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE patients ADD COLUMN state TEXT DEFAULT 'Andhra Pradesh'")
    except Exception:
        pass
    try:
        c.execute("ALTER TABLE screenings ADD COLUMN state TEXT DEFAULT 'Andhra Pradesh'")
    except Exception:
        pass

    conn.commit()

    # Seed demo user
    c.execute("SELECT COUNT(*) FROM users WHERE username='healthworker'")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)",
            ("healthworker", "demo123", "Demo Health Worker", "health_worker")
        )

    # Seed demo patients with Indian states
    demo_patients = [
        ("P1001", "Demo Patient A", 45, "Male",   "9876543210", "Nalgonda",   "Telangana",      "2026-08-10"),
        ("P1002", "Demo Patient B", 62, "Female",  "9876543211", "Warangal",   "Telangana",      "2026-08-15"),
        ("P1003", "Demo Patient C", 54, "Male",   "9876543212", "Vijayawada", "Andhra Pradesh", "2026-08-20"),
        ("P1004", "Demo Patient D", 58, "Female",  "9876543213", "Chennai",    "Tamil Nadu",     "2026-08-22"),
        ("P1005", "Demo Patient E", 49, "Male",   "9876543214", "Pune",       "Maharashtra",    "2026-08-25"),
    ]
    for p in demo_patients:
        c.execute("SELECT COUNT(*) FROM patients WHERE patient_id=?", (p[0],))
        if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO patients VALUES (?,?,?,?,?,?,?,?)", p
            )

    # Seed demo screenings with states
    demo_screenings = [
        ("SCR-1001", "P1001", "", 210.5, 128.3, 82.1, "PASS", None, 0, "No DR",               98.2, "Low",           "Routine Screening",          None, 1, "2026-08-10 10:30:00", "Right", "Telangana"),
        ("SCR-1002", "P1002", "", 185.2, 115.7, 76.4, "PASS", None, 2, "Moderate DR",         87.4, "Moderate",      "Specialist Review",          None, 1, "2026-08-15 14:45:00", "Left",  "Telangana"),
        ("SCR-1003", "P1003", "", 170.8, 108.1, 71.2, "PASS", None, 3, "Severe DR",           91.2, "High",          "Priority Specialist Review", None, 1, "2026-08-20 09:15:00", "Right", "Andhra Pradesh"),
        ("SCR-1004", "P1004", "", 195.0, 120.0, 78.5, "PASS", None, 1, "Mild DR",             92.0, "Low–Moderate",  "6-Month Follow-up",          None, 1, "2026-08-22 11:10:00", "Left",  "Tamil Nadu"),
        ("SCR-1005", "P1005", "", 160.2, 105.4, 70.0, "PASS", None, 4, "Proliferative DR",    94.5, "Very High",     "Immediate Specialist Referral", None, 1, "2026-08-25 16:30:00", "Right", "Maharashtra"),
    ]
    for s in demo_screenings:
        c.execute("SELECT COUNT(*) FROM screenings WHERE screening_id=?", (s[0],))
        if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO screenings (screening_id, patient_id, image_path, blur_score, "
                "illumination_score, fov_score, quality_status, quality_fail_reason, "
                "predicted_grade, predicted_class, confidence, risk_level, referral_status, "
                "report_path, is_demo, screening_date, eye_side, state) VALUES "
                "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", s
            )

    conn.commit()
    conn.close()


# ── Patient CRUD ──────────────────────────────────────────────────────────────

def generate_patient_id():
    """Generate next patient ID using MAX to avoid collision on deletions."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT MAX(CAST(SUBSTR(patient_id, 2) AS INTEGER)) FROM patients WHERE patient_id LIKE 'P%'")
    row = c.fetchone()
    conn.close()
    last = row[0] if row[0] is not None else 1000
    return f"P{last + 1:04d}"


def save_patient(patient_id, name, age, gender, phone, village, state="Andhra Pradesh"):
    conn = get_connection()
    c = conn.cursor()
    reg_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT OR IGNORE INTO patients VALUES (?,?,?,?,?,?,?,?)",
        (patient_id, name, age, gender, phone, village, state, reg_date)
    )
    conn.commit()
    conn.close()


def get_patient(patient_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def search_patients(query):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM patients WHERE patient_id LIKE ? OR name LIKE ? ORDER BY registration_date DESC",
        (f"%{query}%", f"%{query}%")
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_patients():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM patients ORDER BY registration_date DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Screening CRUD ────────────────────────────────────────────────────────────

def generate_screening_id():
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"SCR-{ts}"


def save_screening(screening_id, patient_id, image_path, blur_score, illumination_score,
                   fov_score, quality_status, quality_fail_reason,
                   predicted_grade, predicted_class, confidence,
                   risk_level, referral_status, report_path, is_demo,
                   eye_side="Unknown"):
    conn = get_connection()
    c = conn.cursor()
    screening_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT OR REPLACE INTO screenings
        (screening_id, patient_id, image_path, blur_score, illumination_score,
         fov_score, quality_status, quality_fail_reason, predicted_grade, predicted_class,
         confidence, risk_level, referral_status, report_path, is_demo, screening_date, eye_side)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        screening_id, patient_id, image_path,
        blur_score, illumination_score, fov_score,
        quality_status, quality_fail_reason,
        predicted_grade, predicted_class, confidence,
        risk_level, referral_status, report_path, int(is_demo),
        screening_date, eye_side
    ))
    conn.commit()
    conn.close()


def get_screenings_for_patient(patient_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM screenings WHERE patient_id=? ORDER BY screening_date DESC",
        (patient_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_screening_by_id(screening_id: str) -> dict:
    """Retrieve a single screening record by its ID.

    Returns a dictionary with column names as keys, or None if not found.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM screenings WHERE screening_id = ?", (screening_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_recent_screenings(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.*, p.name as patient_name
        FROM screenings s
        LEFT JOIN patients p ON s.patient_id = p.patient_id
        ORDER BY s.screening_date DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_priority_referrals(limit=5):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.*, p.name as patient_name
        FROM screenings s
        LEFT JOIN patients p ON s.patient_id = p.patient_id
        WHERE s.risk_level IN ('High', 'Very High')
          AND s.quality_status = 'PASS'
        ORDER BY s.screening_date DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Dashboard Stats ───────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(DISTINCT patient_id) FROM screenings WHERE quality_status='PASS'")
    total_patients = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM screenings WHERE quality_status='PASS'")
    total_screenings = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM screenings")
    total_attempts = c.fetchone()[0]

    quality_pass_rate = round((total_screenings / total_attempts * 100) if total_attempts > 0 else 0, 1)

    c.execute("SELECT COUNT(*) FROM screenings WHERE risk_level IN ('High','Very High') AND quality_status='PASS'")
    referrals_needed = c.fetchone()[0]

    # Grade distribution
    c.execute("""
        SELECT predicted_grade, COUNT(*) as cnt
        FROM screenings
        WHERE quality_status='PASS' AND predicted_grade IS NOT NULL
        GROUP BY predicted_grade
        ORDER BY predicted_grade
    """)
    grade_dist_raw = c.fetchall()
    grade_dist = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    for row in grade_dist_raw:
        if row[0] is not None:
            grade_dist[int(row[0])] = row[1]

    conn.close()
    return {
        "total_patients": total_patients,
        "total_screenings": total_screenings,
        "quality_pass_rate": quality_pass_rate,
        "referrals_needed": referrals_needed,
        "grade_distribution": grade_dist,
    }


def get_screenings_date_series():
    """Return screening counts grouped by date for trend chart."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT SUBSTR(screening_date, 1, 10) as day, COUNT(*) as count
        FROM screenings
        WHERE quality_status = 'PASS'
        GROUP BY day
        ORDER BY day
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_screenings_csv():
    """Return all screenings joined with patient name for CSV export."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.screening_id, p.name as patient_name, s.patient_id,
               s.screening_date, s.eye_side, s.predicted_grade, s.predicted_class,
               s.confidence, s.risk_level, s.referral_status,
               s.quality_status, s.blur_score, s.illumination_score, s.fov_score, s.is_demo
        FROM screenings s
        LEFT JOIN patients p ON s.patient_id = p.patient_id
        ORDER BY s.screening_date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_state_wise_stats():
    """Return screening breakdown grouped by Indian State."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(state, 'Andhra Pradesh') as state_name,
               COUNT(*) as total_screenings,
               SUM(CASE WHEN risk_level IN ('High', 'Very High') THEN 1 ELSE 0 END) as high_risk_count
        FROM screenings
        WHERE quality_status = 'PASS'
        GROUP BY state_name
        ORDER BY total_screenings DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def authenticate_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

