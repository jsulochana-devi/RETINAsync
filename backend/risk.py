"""
backend/risk.py
Maps predicted DR grade to risk level and referral recommendation.
This is prototype referral-support logic — NOT an official clinical protocol.
"""

RISK_MAP = {
    0: {
        "risk_level": "Low",
        "risk_color": "#22c55e",       # green
        "risk_badge": "🟢 LOW",
        "referral_text": "Routine screening / annual follow-up",
        "urgency": "ROUTINE",
        "urgency_color": "#22c55e",
        "advice": "No signs of diabetic retinopathy detected. Continue routine annual screening.",
    },
    1: {
        "risk_level": "Low–Moderate",
        "risk_color": "#84cc16",       # lime
        "risk_badge": "🟡 LOW–MODERATE",
        "referral_text": "Follow-up screening in 6–12 months",
        "urgency": "FOLLOW-UP",
        "urgency_color": "#84cc16",
        "advice": "Mild signs detected. Follow-up screening recommended within 6–12 months.",
    },
    2: {
        "risk_level": "Moderate",
        "risk_color": "#f59e0b",       # amber
        "risk_badge": "🟠 MODERATE",
        "referral_text": "Specialist review recommended",
        "urgency": "SPECIALIST REVIEW",
        "urgency_color": "#f59e0b",
        "advice": "Moderate diabetic retinopathy detected. Specialist ophthalmology review is recommended.",
    },
    3: {
        "risk_level": "High",
        "risk_color": "#ef4444",       # red
        "risk_badge": "🔴 HIGH",
        "referral_text": "Priority specialist review",
        "urgency": "PRIORITY",
        "urgency_color": "#ef4444",
        "advice": "Severe diabetic retinopathy detected. Priority ophthalmology review is strongly recommended.",
    },
    4: {
        "risk_level": "Very High",
        "risk_color": "#7c3aed",       # purple
        "risk_badge": "🔴 VERY HIGH",
        "referral_text": "Urgent specialist review required",
        "urgency": "URGENT",
        "urgency_color": "#7c3aed",
        "advice": "Proliferative diabetic retinopathy detected. Urgent ophthalmology assessment is required.",
    },
}

DR_CLASSES = {
    0: "No Diabetic Retinopathy",
    1: "Mild Diabetic Retinopathy",
    2: "Moderate Diabetic Retinopathy",
    3: "Severe Diabetic Retinopathy",
    4: "Proliferative Diabetic Retinopathy",
}

DR_GRADES = {
    0: "Grade 0",
    1: "Grade 1",
    2: "Grade 2",
    3: "Grade 3",
    4: "Grade 4",
}


def calculate_risk(grade: int) -> dict:
    """
    Map a DR grade (0–4) to risk level and referral recommendation.

    Returns a dict with:
        risk_level, risk_color, risk_badge,
        referral_text, urgency, urgency_color,
        advice, dr_class, dr_grade
    """
    grade = int(grade)
    if grade not in RISK_MAP:
        grade = 0

    result = dict(RISK_MAP[grade])
    result["grade"] = grade
    result["dr_class"] = DR_CLASSES[grade]
    result["dr_grade"] = DR_GRADES[grade]
    return result
