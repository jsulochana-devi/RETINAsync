"""
backend/quality_gate.py
Image quality assessment for retinal fundus images.
Implements three metrics: blur, illumination, and field-of-view.
"""

import cv2
import numpy as np


# ── Thresholds ─────────────────────────────────────────────────────────────────
BLUR_THRESHOLD        = 80.0    # Laplacian variance — below this = blurry
ILLUMINATION_MIN      = 40.0    # Mean brightness — below = too dark
ILLUMINATION_MAX      = 220.0   # Mean brightness — above = overexposed
FOV_THRESHOLD         = 55.0    # Percent of image that is the fundus circle

BLUR_WARNING          = 120.0   # Between this and BLUR_THRESHOLD = borderline
ILLUMINATION_MIN_WARN = 55.0
ILLUMINATION_MAX_WARN = 200.0
FOV_WARNING           = 65.0


def _to_gray(image: np.ndarray) -> np.ndarray:
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return image


def calculate_blur_score(image: np.ndarray) -> float:
    """
    Compute Laplacian variance as a blur metric.
    Higher value = sharper image.
    """
    gray = _to_gray(image)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    variance = laplacian.var()
    return round(float(variance), 2)


def calculate_illumination(image: np.ndarray) -> float:
    """
    Calculate mean brightness of the image.
    Returns value in [0, 255].
    """
    gray = _to_gray(image)
    mean_val = float(np.mean(gray))
    return round(mean_val, 2)


def calculate_fov_score(image: np.ndarray) -> float:
    """
    Estimate what percentage of the image contains the retinal disc.
    Uses circular Hough transform or simple thresholding of the bright circular region.
    Returns percentage in [0, 100].
    """
    gray = _to_gray(image)
    h, w = gray.shape

    # Threshold to find bright (fundus) region
    _, thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)

    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

    bright_pixels = np.sum(cleaned > 0)
    total_pixels = h * w
    pct = (bright_pixels / total_pixels) * 100.0

    # Clamp to reasonable range
    pct = min(max(pct, 0.0), 100.0)
    return round(pct, 1)


def _score_status(value: float, fail_thresh: float, warn_thresh: float,
                  high_is_good: bool = True) -> str:
    """Return PASS / BORDERLINE / FAIL based on thresholds."""
    if high_is_good:
        if value >= warn_thresh:
            return "PASS"
        elif value >= fail_thresh:
            return "BORDERLINE"
        else:
            return "FAIL"
    else:  # low is good
        if value <= warn_thresh:
            return "PASS"
        elif value <= fail_thresh:
            return "BORDERLINE"
        else:
            return "FAIL"


def run_quality_gate(image: np.ndarray) -> dict:
    """
    Run all three quality checks.
    Returns a comprehensive result dict.
    """
    blur_score = calculate_blur_score(image)
    illumination = calculate_illumination(image)
    fov_score = calculate_fov_score(image)

    # Blur status
    blur_status = _score_status(blur_score, BLUR_THRESHOLD, BLUR_WARNING, high_is_good=True)

    # Illumination — dual bound
    if ILLUMINATION_MIN_WARN <= illumination <= ILLUMINATION_MAX_WARN:
        illum_status = "PASS"
    elif ILLUMINATION_MIN <= illumination <= ILLUMINATION_MAX:
        illum_status = "BORDERLINE"
    else:
        illum_status = "FAIL"

    # FOV status
    fov_status = _score_status(fov_score, FOV_THRESHOLD, FOV_WARNING, high_is_good=True)

    # Overall status
    statuses = [blur_status, illum_status, fov_status]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "BORDERLINE" in statuses:
        overall = "BORDERLINE"
    else:
        overall = "PASS"

    # Collect failure reasons
    reasons = []
    if blur_status == "FAIL":
        reasons.append("Excessive blur — image is too blurry for reliable screening")
    if blur_status == "BORDERLINE":
        reasons.append("Borderline sharpness — image may be slightly blurry")
    if illum_status == "FAIL":
        if illumination < ILLUMINATION_MIN:
            reasons.append("Insufficient illumination — image is too dark")
        else:
            reasons.append("Over-illumination — image is too bright / overexposed")
    if illum_status == "BORDERLINE":
        reasons.append("Borderline illumination")
    if fov_status == "FAIL":
        reasons.append("Insufficient field of view — fundus not properly centered or framed")
    if fov_status == "BORDERLINE":
        reasons.append("Borderline field of view — consider re-framing")

    return {
        "blur_score": blur_score,
        "blur_status": blur_status,
        "illumination_score": illumination,
        "illumination_status": illum_status,
        "fov_score": fov_score,
        "fov_status": fov_status,
        "overall_status": overall,
        "fail_reasons": reasons,
        "can_proceed": overall != "FAIL",
    }
