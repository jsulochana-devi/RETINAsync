# 👁️ RETINAsync — Explainable AI for Diabetic Retinopathy Screening in Rural India

> **Smart India Hackathon 2026 | Problem Statement SIH26038**

---

## 🎯 Project Overview

**RETINAsync** is an end-to-end AI-powered diabetic retinopathy (DR) screening prototype designed for
community health workers in rural India. It enables non-specialist healthcare workers to perform fundus
image screening at primary health centres, with automatic image quality validation, 5-class DR severity
classification, Grad-CAM visual explainability, and risk-based referral support.

> ⚠️ **This is a research and hackathon prototype. It is NOT a certified medical device and must NOT
> be used for clinical diagnosis. All results require review by a qualified ophthalmologist.**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔍 Image Quality Gate | Automatic blur, illumination & field-of-view check |
| 🧠 5-Class DR Classification | CNN grades No DR → Proliferative DR with confidence |
| 🗺️ Grad-CAM Explainability | Heatmap highlights regions driving the prediction |
| 📋 Risk Stratification | Grade → risk level → referral recommendation |
| 📄 PDF Reports | Downloadable screening report per patient |
| 📶 Offline-Ready | Local SQLite DB, no cloud required |
| 🎭 Demo Mode | Works without a trained model for SIH demonstrations |

---

## 🏗️ Architecture

```
RETINAsync/
├── app.py                     # Streamlit entry point, login, navigation
├── backend/
│   ├── database.py            # SQLite CRUD operations
│   ├── quality_gate.py        # Blur, illumination, FOV detection
│   ├── preprocessing.py       # CLAHE, resize, denoise pipeline
│   ├── model.py               # CNN interface + demo mode
│   ├── gradcam.py             # Grad-CAM / demo heatmap
│   ├── risk.py                # Grade → risk → referral mapping
│   └── report.py              # PDF report generation (ReportLab)
├── pages/
│   ├── home.py
│   ├── patient_registration.py
│   ├── new_screening.py
│   ├── ai_analysis.py
│   ├── patient_history.py
│   ├── dashboard.py
│   └── about.py
├── models/                    # Place dr_model.keras here
├── database/                  # Auto-created SQLite database
├── uploads/                   # Saved patient images
├── reports/                   # Generated PDF reports
├── requirements.txt
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10 or 3.11
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The app will open at: `http://localhost:8501`

---

## 🔑 Demo Credentials

| Username | Password |
|---|---|
| `healthworker` | `demo123` |

> ⚠️ These are demonstration credentials for the prototype only.

---

## 🎭 Demo Mode

By default, **Demo Mode** is enabled. This allows the complete screening workflow to be
demonstrated without a trained CNN model:

- Predictions are deterministic sample results clearly labelled **DEMONSTRATION**
- Grad-CAM shows a synthetic demonstration heatmap
- All 3 demo cases are available (No DR, Moderate DR, Severe DR)

To disable Demo Mode, toggle it off in the sidebar or place a trained model at:

```
models/dr_model.keras
```

---

## 🧠 Adding a Real Trained Model

1. Train a 5-class CNN on a fundus image dataset (e.g., EyePACS, APTOS 2019)
2. Save the model in Keras format:

```python
model.save("models/dr_model.keras")
```

3. Ensure the model:
   - Accepts input shape `(224, 224, 3)` float32 in range [0, 1]
   - Outputs a softmax vector of shape `(5,)` for [No DR, Mild, Moderate, Severe, Proliferative]
   - Has a named last convolutional layer (e.g., `last_conv`) for Grad-CAM targeting

4. Restart the app — it will auto-detect the model and disable Demo Mode.

---

## 🗄️ Database Structure

### `patients` table
| Column | Type | Description |
|---|---|---|
| patient_id | TEXT PK | Auto-generated (e.g., P1001) |
| name | TEXT | Full name |
| age | INTEGER | Age |
| gender | TEXT | Male / Female / Other |
| phone | TEXT | Optional |
| village | TEXT | Optional location |
| registration_date | TEXT | ISO datetime |

### `screenings` table
| Column | Type | Description |
|---|---|---|
| screening_id | TEXT PK | Auto-generated |
| patient_id | TEXT FK | Links to patients |
| blur_score | REAL | Laplacian variance |
| illumination_score | REAL | Mean brightness |
| fov_score | REAL | Fundus coverage % |
| quality_status | TEXT | PASS / BORDERLINE / FAIL |
| predicted_grade | INTEGER | 0–4 |
| predicted_class | TEXT | Full class name |
| confidence | REAL | % confidence |
| risk_level | TEXT | Low to Very High |
| referral_status | TEXT | Referral recommendation |
| is_demo | INTEGER | 1 if demo prediction |

---

## 🔍 How Grad-CAM Works

Gradient-weighted Class Activation Mapping (Grad-CAM) computes the gradient of the predicted class
score with respect to the feature maps of the last convolutional layer. These gradients are
globally average-pooled to produce importance weights, which are used to create a weighted
combination of activation maps — a heatmap highlighting the image regions most relevant to
the prediction.

In Demo Mode, a synthetic Gaussian heatmap is placed at anatomically plausible positions
(optic disc, macula, peripheral lesion areas) purely for workflow demonstration.

---

## 📋 Screening Workflow

```
Login → Home → Register Patient → Upload Image
     → Quality Gate
          ↓ FAIL → Show reason → Retake image
          ↓ PASS
     → Preprocessing (CLAHE, resize, denoise)
     → CNN Classification (5-class)
     → Grad-CAM Visualization
     → Risk Stratification
     → Referral Recommendation
     → Save Screening to DB
     → Generate PDF Report
     → Patient History / Dashboard
```

---

## 🌐 Language Support

| Language | Status |
|---|---|
| English | ✅ Fully implemented |
| తెలుగు (Telugu) | 🔜 Coming soon |
| हिन्दी (Hindi) | 🔜 Coming soon |

---

## 🔮 Future Improvements

- [ ] Real trained CNN model integration (EfficientNetB3 / ResNet50)
- [ ] Mobile camera capture support
- [ ] Full Telugu and Hindi translations
- [ ] Telemedicine integration for referral handoff
- [ ] Batch screening mode
- [ ] Cloud sync for multi-centre deployments
- [ ] Integration with ABDM (Ayushman Bharat Digital Mission)

---

## ⚠️ Medical Disclaimer

RETINAsync is a **research prototype** developed for the Smart India Hackathon 2026.
It is **NOT** a certified medical device, and its predictions have **NOT** been clinically validated.

- Do NOT use for actual patient diagnosis or treatment decisions
- All AI predictions require review by a qualified ophthalmologist
- The risk stratification is illustrative prototype logic, NOT an official clinical protocol
- Grad-CAM visualizations are interpretive aids, not diagnostic evidence

---

## 📜 License

This project is developed as a hackathon prototype for educational and research purposes.

---

*RETINAsync v1.0 — Smart India Hackathon 2026 | SIH26038*
# RETINAsync
