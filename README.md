# Smart Body Posture Recognition & Guidance System
### GLA University • Department of Computer Science Engineering & Applications
### B.Tech CSE (III YEAR – VI SEM) (2025–26) • Mini-Project v1.0

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-5.0%2B-green.svg)](https://opencv.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%20Tasks-orange.svg)](https://developers.google.com/mediapipe)
[![Flask](https://img.shields.io/badge/Flask-3.1%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Tests](https://img.shields.io/badge/Pytest-22%20Passed-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/License-Academic%20Use-blue.svg)](#)

---

## 👥 Team & Project Credits
- **Team Name & ID:** OG-Coders (T-89)
- **Team Leader:** Prasant Kumar (UR: 2415500346)
- **Team Member 1:** Pawan Kumar (UR: 2415500334)
- **Team Member 2:** Dhananjay Chaudhary (UR: 2415500155)
- **Project Mentor:** Rohit Kumar Gupta Sir
- **Academic Year:** 2025–2026

---

## 📖 Executive Summary
In self-service health kiosks and automated diagnostic booths, accurate measurement of vital signs (blood pressure, body weight, ECG) depends directly on proper patient positioning. Unattended users frequently sit slouched (falsely elevating BP by **10–15 mmHg**), cross their legs (elevating systolic BP by **5–8 mmHg**), or place their arms below heart level.

This project delivers an **AI-powered computer vision guidance layer** that connects to standard kiosk cameras, extracts 33 human anatomical landmarks in real-time, validates biomechanical posture rules across 3 clinical measurement modes, provides on-screen visual guidance, and **automatically activates kiosk diagnostic sensors** once correct posture is maintained steadily for **2.5 seconds**.

---

## 🚀 Key Features

1. **Real-Time 33-Keypoint Pose Detection:** Powered by MediaPipe Pose running on edge CPU with p95 latency $\le 45\text{ ms}$ (SLA $\le 300\text{ ms}$).
2. **Clinical Posture Validation Engine:**
   - **Blood Pressure (BP):** Upright spine ($\le 18^\circ$ tilt), uncrossed legs, arm supported at heart level, neutral head position.
   - **Weight & BMI:** Upright vertical stance, balanced foot weight distribution, arms hanging relaxed (not leaning on rails).
   - **ECG Diagnostic Scan:** Back supported, grounded legs, forearms resting flat on sensor contact plates, motion stability.
3. **Continuous Hold-Timer & Auto Sensor Trigger:** Verifies steady posture for 2.5 seconds before emitting an authenticated hardware activation signal.
4. **Interactive Hardware Simulation:**
   - Animated Blood Pressure cuff inflation counter (0 to 160 mmHg, settling at 120/78 mmHg).
   - Digital platform weight scale stabilization with BMI and body fat index.
   - Real-time scrolling Lead-I ECG strip tracing canvas with P-Q-R-S-T wave rendering.
5. **Dual-Channel User Feedback:**
   - **Visual HUD Canvas:** Glowing color-coded joints (green = correct, red = error), dashed spine line, and upward directional guidance arrows.
   - **Voice guidance is not included in this version; posture corrections are shown on screen.
6. **Built-in Posture Presets Simulator:** Instantly test "Perfect Posture", "Slouching", "Crossed Legs", and "Arm Low" scenarios without needing a physical webcam.
7. **Analytics & Admin Dashboard:** Tracks positioning error reduction ($< 2\%$ vs $30\%$), auto-trigger reliability ($\ge 98\%$), average check-in duration, and error distribution.
8. **Privacy by Design (Zero PII):** Raw frames are discarded immediately after keypoint inference; only anonymized posture events are stored.

---

## 📁 Project Structure

```text
Dhananjay/
├── mini_pro_synopsis.pdf               # Original approved B.Tech project synopsis
├── README.md                           # Main documentation & quickstart guide
├── requirements.txt                    # Project dependencies
├── run_kiosk.py                        # Single-command launcher for Kiosk Web Server
├── run_desktop_app.py                  # Standalone OpenCV + MediaPipe native GUI
├── .env.example                        # Configuration template
├── models/
│   └── pose_landmarker_lite.task       # Local MediaPipe PoseLandmarker model (5.7 MB)
├── config/
│   ├── settings.py                     # Environment variables & paths
│   └── posture_rules.json              # Versioned posture rules configuration
├── src/
│   ├── pose/
│   │   ├── landmarks.py                # 33 Landmark Enums, connections & Point3D
│   │   ├── geometry.py                 # Vector math, spine tilt & knee separation
│   │   └── detector.py                 # MediaPipe PoseLandmarker inference wrapper
│   ├── rules/
│   │   ├── base_rule.py                # Abstract base rule class & PostureError model
│   │   ├── bp_rules.py                 # BP slouch, crossed legs, arm height rules
│   │   ├── weight_rules.py             # Weight stance & rail-leaning rules
│   │   ├── ecg_rules.py                # ECG resting & electrode contact rules
│   │   └── engine.py                   # PostureRuleEngine orchestrator
│   ├── controller/
│   │   ├── hold_timer.py               # 2.5s steady hold counter & trigger emitter
│   │   ├── state_machine.py            # 5-state lifecycle model
│   │   └── feedback_controller.py      # Audio prompt debouncing (>=2s rule)
│   ├── api/
│   │   ├── app.py                      # Flask app factory, CORS, static file serving
│   │   ├── routes_posture.py           # /api/posture/analyze, /trigger, /rules
│   │   ├── routes_analytics.py         # /api/analytics/log, /kpis, /sessions
│   │   └── auth.py                     # Device-key authentication middleware
│   ├── database/
│   │   └── db.py                       # SQLite manager (Sessions, Events, Analytics)
│   └── tts/
│       └── tts_engine.py               # (removed; voice guidance is not included)
├── static/
│   ├── css/
│   │   ├── kiosk.css                   # High-contrast medical touchscreen styling
│   │   └── dashboard.css               # Analytics KPIs and charts styling
│   ├── js/
│   │   ├── kiosk.js                    # Main client controller (webcam & UI loop)
│   │   ├── visual_overlay.js           # Canvas skeleton, glowing joints & arrows
│   │   ├── (removed; voice guidance is not included)
│   │   ├── sensor_simulation.js        # BP cuff, scale, ECG animations
│   │   ├── analytics_dashboard.js      # KPI cards & recent sessions table
│   │   └── sample_presets.js           # Instant demo scenario presets
│   └── index.html                      # Single-page kiosk touchscreen application
├── tests/
│   ├── test_geometry.py                # Vector geometry unit tests
│   ├── test_rules.py                   # BP, Weight, ECG rule tests
│   ├── test_state_machine.py           # Hold timer and state transitions tests
│   └── test_api.py                     # Flask API endpoints & auth tests
└── docs/
    ├── ARCHITECTURE.md                 # Complete system architecture with 6 Mermaid diagrams
    ├── PROJECT_REPORT.md               # Academic project report (GLA Univ format)
    └── PRESENTATION_DECK.md            # Slide deck outline for viva/presentation
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites & Installation
Ensure Python 3.10+ is installed. Install all dependencies:
```bash
python -m pip install -r requirements.txt
```

### 2. Launch the Kiosk Web System
Run the kiosk launcher:
```bash
python run_kiosk.py
```
- The server will start at `http://127.0.0.1:5000`.
- Your default web browser will **automatically open** to the kiosk touchscreen interface.
- You can immediately click **"Posture Preset Demo"** dropdown to test all posture scenarios, or click **"Start Camera"** to use your real webcam!

### 3. Run Standalone Desktop Application (Optional)
To run a pure native OpenCV desktop window with MediaPipe and live HUD overlays:
```bash
python run_desktop_app.py
```
*Keyboard shortcuts:*
- Press `1` for Blood Pressure check
- Press `2` for Weight / Stance check
- Press `3` for ECG diagnostic check
- Press `Q` to quit

### 4. Run Automated Test Suite
To verify all 22 automated tests:
```bash
python -m pytest tests -v
```

---

## 📡 REST API Reference

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/health` | None | System uptime, latency SLA, and NFR monitoring |
| `POST` | `/api/posture/analyze` | None | Validates 33 keypoints against clinical posture rules |
| `POST` | `/api/posture/analyze-frame` | None | Accepts image frame and runs server-side MediaPipe |
| `POST` | `/api/posture/trigger` | `X-Device-Key` | Triggers simulated kiosk sensor reading |
| `GET` | `/api/posture/rules` | None | Returns active posture rule parameters |
| `PUT` | `/api/posture/rules` | None | Updates posture tolerance thresholds (Calibration) |
| `POST` | `/api/analytics/log` | None | Stores anonymized session logs and errors |
| `GET` | `/api/analytics/kpis` | None | Returns operational KPIs (Reliability, Error rate) |
| `GET` | `/api/analytics/sessions` | None | Returns recent session history |

---

## 📊 Technical Workflow & Diagrams
For in-depth architectural details, data flow diagrams, ERD, and sequence flows, refer to:
👉 **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

For the full academic report and viva presentation deck, refer to:
👉 **[docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md)**  
👉 **[docs/PRESENTATION_DECK.md](docs/PRESENTATION_DECK.md)**
