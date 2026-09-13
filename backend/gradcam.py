"""
backend/gradcam.py
Grad-CAM explainability visualization for the DR classification model.
Falls back to a clearly-labelled synthetic demonstration heatmap in Demo Mode.
"""

import numpy as np
import cv2
from PIL import Image
import io


def _apply_colormap(heatmap: np.ndarray) -> np.ndarray:
    """Apply JET colormap to a grayscale heatmap [0,1]."""
    heatmap_uint8 = np.uint8(255 * heatmap)
    colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    return colored_rgb


def _overlay_heatmap(original: np.ndarray, heatmap_colored: np.ndarray,
                     alpha: float = 0.45) -> np.ndarray:
    """Blend heatmap over original image."""
    orig_resized = cv2.resize(original, (heatmap_colored.shape[1], heatmap_colored.shape[0]))
    overlay = cv2.addWeighted(orig_resized.astype(np.uint8), 1 - alpha,
                               heatmap_colored.astype(np.uint8), alpha, 0)
    return overlay


# ── Demo heatmap generator ────────────────────────────────────────────────────

def _generate_demo_heatmap(image_array: np.ndarray, grade: int) -> np.ndarray:
    """
    Generate a synthetic demonstration heatmap.
    The heatmap simulates attention on the optic disc/macula region.
    Clearly for demonstration only.
    """
    h, w = image_array.shape[:2]
    heatmap = np.zeros((h, w), dtype=np.float32)

    # Place Gaussian blobs at clinically relevant positions (normalized)
    def add_blob(cy_frac, cx_frac, sigma_frac, strength):
        cy = int(cy_frac * h)
        cx = int(cx_frac * w)
        sigma = int(sigma_frac * min(h, w))
        y_idx, x_idx = np.ogrid[:h, :w]
        blob = np.exp(-((y_idx - cy) ** 2 + (x_idx - cx) ** 2) / (2 * sigma ** 2))
        return blob * strength

    # Optic disc area (right-center of fundus)
    heatmap += add_blob(0.5, 0.62, 0.08, 0.9)

    # Macula area (center)
    if grade >= 2:
        heatmap += add_blob(0.5, 0.45, 0.10, 0.7)

    # Peripheral lesions for higher grades
    if grade >= 3:
        heatmap += add_blob(0.3, 0.35, 0.06, 0.5)
        heatmap += add_blob(0.7, 0.65, 0.05, 0.4)
    if grade >= 4:
        heatmap += add_blob(0.25, 0.55, 0.07, 0.6)
        heatmap += add_blob(0.75, 0.4,  0.06, 0.5)

    # Normalize
    if heatmap.max() > 0:
        heatmap = heatmap / heatmap.max()

    return heatmap


# ── Real Grad-CAM ─────────────────────────────────────────────────────────────

def _real_gradcam(model, image_array: np.ndarray, target_layer_name: str = "last_conv") -> np.ndarray:
    """
    Compute real Grad-CAM for the predicted class.
    Requires TensorFlow.
    """
    import tensorflow as tf

    batch = np.expand_dims(image_array, axis=0)

    # Build gradient model
    try:
        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(target_layer_name).output, model.output]
        )
    except Exception:
        # Try to find the last conv layer automatically
        last_conv = None
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                last_conv = layer.name
                break
        if last_conv is None:
            return None
        grad_model = tf.keras.models.Model(
            inputs=model.inputs,
            outputs=[model.get_layer(last_conv).output, model.output]
        )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(batch, training=False)
        predicted_class = tf.argmax(predictions[0])
        class_score = predictions[:, predicted_class]

    grads = tape.gradient(class_score, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_out = conv_outputs[0]
    heatmap = conv_out @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


# ── Public interface ──────────────────────────────────────────────────────────

def generate_gradcam(model, image_array: np.ndarray, grade: int, is_demo: bool) -> dict:
    """
    Generate Grad-CAM visualization.

    Args:
        model:       Keras model or None
        image_array: float32 (H, W, 3) in [0, 1]
        grade:       predicted DR grade (0–4)
        is_demo:     whether running in demo mode

    Returns dict:
        heatmap_pil, overlay_pil, original_pil, is_demo
    """
    # Convert image array to displayable uint8
    img_uint8 = np.clip(image_array * 255, 0, 255).astype(np.uint8)

    if is_demo or model is None:
        heatmap = _generate_demo_heatmap(img_uint8, grade)
        is_real = False
    else:
        try:
            heatmap = _real_gradcam(model, image_array)
            if heatmap is None:
                heatmap = _generate_demo_heatmap(img_uint8, grade)
                is_real = False
            else:
                # Resize heatmap to match image
                heatmap = cv2.resize(heatmap, (img_uint8.shape[1], img_uint8.shape[0]))
                is_real = True
        except Exception:
            heatmap = _generate_demo_heatmap(img_uint8, grade)
            is_real = False

    heatmap_colored = _apply_colormap(heatmap)
    overlay = _overlay_heatmap(img_uint8, heatmap_colored, alpha=0.45)

    return {
        "original_pil": Image.fromarray(img_uint8),
        "heatmap_pil":  Image.fromarray(heatmap_colored),
        "overlay_pil":  Image.fromarray(overlay),
        "is_demo":      not is_real,
    }
