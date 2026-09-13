"""
backend/preprocessing.py
Retinal image preprocessing pipeline.
Resize → Crop → Denoise → CLAHE → Normalize
"""

import cv2
import numpy as np
from PIL import Image


TARGET_SIZE = (224, 224)


def _pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR numpy array."""
    img = np.array(pil_img)
    if len(img.shape) == 3 and img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return img


def _cv2_to_pil(cv2_img: np.ndarray) -> Image.Image:
    """Convert OpenCV RGB numpy array to PIL Image."""
    return Image.fromarray(cv2_img.astype(np.uint8))


def crop_to_fundus(image: np.ndarray) -> np.ndarray:
    """
    Crop image to the circular fundus region.
    Finds the largest bright region and crops a square around it.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if len(image.shape) == 3 else image.copy()
    _, thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image  # fallback: return original

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    # Add small padding
    pad = 10
    x = max(0, x - pad)
    y = max(0, y - pad)
    x2 = min(image.shape[1], x + w + pad)
    y2 = min(image.shape[0], y + h + pad)

    cropped = image[y:y2, x:x2]
    return cropped if cropped.size > 0 else image


def apply_clahe(image: np.ndarray) -> np.ndarray:
    """Apply CLAHE to the LAB lightness channel."""
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    merged = cv2.merge([l_clahe, a, b])
    result = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
    return result


def preprocess_image(pil_image: Image.Image) -> tuple:
    """
    Full preprocessing pipeline for a retinal fundus image.

    Args:
        pil_image: PIL Image (RGB)

    Returns:
        (processed_pil_image, steps_description, model_input_array)
    """
    # Convert to numpy RGB
    img = _pil_to_cv2(pil_image.convert("RGB"))

    steps = []

    # Step 1 — Resize to working size
    img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)
    steps.append("Resized to 512×512")

    # Step 2 — Crop to fundus region
    img = crop_to_fundus(img)
    steps.append("Cropped to fundus region")

    # Step 3 — Resize to target size
    img = cv2.resize(img, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    steps.append(f"Resized to {TARGET_SIZE[0]}×{TARGET_SIZE[1]}")

    # Step 4 — Gaussian denoise
    img = cv2.GaussianBlur(img, (3, 3), 0)
    steps.append("Applied Gaussian denoising")

    # Step 5 — CLAHE contrast enhancement
    img = apply_clahe(img)
    steps.append("Applied CLAHE contrast enhancement")

    # Step 6 — Normalize to [0, 1] float for model
    model_input = img.astype(np.float32) / 255.0

    processed_pil = _cv2_to_pil(img)

    description = " → ".join(steps)
    return processed_pil, description, model_input
