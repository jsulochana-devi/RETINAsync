"""
backend/model.py
CNN model interface for 5-class DR classification.
Automatically activates Demo Mode if no trained model file is found.
TensorFlow is optional — if not installed, Demo Mode is always used.
"""

import os
import hashlib
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "dr_model.keras")

# Check TF availability once at import
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    TF_AVAILABLE = False

DR_CLASSES = [
    "No DR",
    "Mild DR",
    "Moderate DR",
    "Severe DR",
    "Proliferative DR",
]

DR_CLASS_FULL = [
    "No Diabetic Retinopathy",
    "Mild Diabetic Retinopathy",
    "Moderate Diabetic Retinopathy",
    "Severe Diabetic Retinopathy",
    "Proliferative Diabetic Retinopathy",
]

_model = None
DEMO_MODE = True  # will be set to False if real model loads


# ── Demo predictions ──────────────────────────────────────────────────────────

# Three demo cases that cycle based on image content hash
_DEMO_CASES = [
    # Grade 0 — No DR
    {"grade": 0, "confidence": 97.8,
     "probs": [0.978, 0.012, 0.006, 0.003, 0.001]},
    # Grade 2 — Moderate DR
    {"grade": 2, "confidence": 87.4,
     "probs": [0.032, 0.085, 0.874, 0.007, 0.002]},
    # Grade 3 — Severe DR
    {"grade": 3, "confidence": 91.2,
     "probs": [0.010, 0.025, 0.041, 0.912, 0.012]},
    # Grade 1 — Mild DR
    {"grade": 1, "confidence": 83.1,
     "probs": [0.095, 0.831, 0.052, 0.018, 0.004]},
    # Grade 4 — Proliferative DR
    {"grade": 4, "confidence": 88.5,
     "probs": [0.005, 0.012, 0.031, 0.067, 0.885]},
]


def _image_hash_index(image_array: np.ndarray) -> int:
    """Produce a deterministic index from image content."""
    flat = image_array.flatten()
    sample = flat[::max(1, len(flat) // 1000)]
    digest = hashlib.md5(sample.tobytes()).hexdigest()
    return int(digest[:4], 16) % len(_DEMO_CASES)


# ── Model loading ─────────────────────────────────────────────────────────────

def load_model():
    """
    Load the trained DR model if available.
    Falls back to Demo Mode automatically.
    Returns (model_or_None, is_demo_mode).
    """
    global _model, DEMO_MODE

    if not TF_AVAILABLE:
        DEMO_MODE = True
        _model = None
        return None, True

    if not os.path.exists(MODEL_PATH):
        DEMO_MODE = True
        _model = None
        return None, True

    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(MODEL_PATH)
        DEMO_MODE = False
        return _model, False
    except Exception as e:
        DEMO_MODE = True
        _model = None
        print(f"[model.py] Could not load model: {e}. Running in Demo Mode.")
        return None, True


def is_demo_mode() -> bool:
    return DEMO_MODE


def get_model():
    return _model


# ── Inference ─────────────────────────────────────────────────────────────────

def predict_dr_grade(model_input: np.ndarray) -> dict:
    """
    Run classification on a preprocessed image array.

    Args:
        model_input: float32 array of shape (224, 224, 3), values in [0, 1]

    Returns dict:
        grade, class_name, class_name_full, confidence, probabilities, is_demo
    """
    if DEMO_MODE or _model is None:
        idx = _image_hash_index(model_input)
        case = _DEMO_CASES[idx]
        grade = case["grade"]
        probs = case["probs"]
        confidence = case["confidence"]
    else:
        import tensorflow as tf
        batch = np.expand_dims(model_input, axis=0)
        raw = _model.predict(batch, verbose=0)[0]
        probs = [float(p) for p in raw]
        grade = int(np.argmax(probs))
        confidence = round(float(np.max(probs)) * 100, 1)

    return {
        "grade": grade,
        "class_name": DR_CLASSES[grade],
        "class_name_full": DR_CLASS_FULL[grade],
        "confidence": confidence if DEMO_MODE else confidence,
        "probabilities": probs,
        "is_demo": DEMO_MODE,
    }


def get_class_probabilities(model_input: np.ndarray) -> list:
    """Return list of probabilities for all 5 classes."""
    result = predict_dr_grade(model_input)
    return result["probabilities"]


def build_demo_model_architecture():
    """
    Build and return a lightweight demo CNN architecture.
    This is NOT used for real predictions — only for Grad-CAM structure reference.
    Requires TensorFlow.
    """
    if not TF_AVAILABLE:
        return None
    try:
        import tensorflow as tf
        inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
        x = tf.keras.layers.Conv2D(32, (3, 3), activation="relu", padding="same", name="conv1")(inputs)
        x = tf.keras.layers.MaxPooling2D(2, 2)(x)
        x = tf.keras.layers.Conv2D(64, (3, 3), activation="relu", padding="same", name="conv2")(x)
        x = tf.keras.layers.MaxPooling2D(2, 2)(x)
        x = tf.keras.layers.Conv2D(128, (3, 3), activation="relu", padding="same", name="last_conv")(x)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dense(256, activation="relu")(x)
        x = tf.keras.layers.Dropout(0.5)(x)
        outputs = tf.keras.layers.Dense(5, activation="softmax")(x)
        model = tf.keras.Model(inputs, outputs)
        return model
    except Exception:
        return None
