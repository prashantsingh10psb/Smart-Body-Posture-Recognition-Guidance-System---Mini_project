# Technical Architecture Specification
## Smart Body Posture Recognition & Guidance System
**GLA University — Department of Computer Science Engineering & Applications**  
**Team OG-Coders (T-89)** | **Academic Year: 2025–2026**

---

### 1. High-Level Architecture Overview
The system is engineered as an edge-ready, real-time posture correction layer positioned directly before automated diagnostic health kiosks. It enforces clinical positioning rules for Blood Pressure (BP), Body Weight/BMI, and Electrocardiogram (ECG) measurements to prevent distorted physiological readings.

```mermaid
graph TD
    subgraph KioskClient["Client / Kiosk Touch Interface"]
        CameraFeed["Live Camera Stream (USB / Integrated)"]
        CanvasHUD["Dynamic Skeleton & Error Overlay (Canvas)"]
        AudioSynthesizer["Speech Synthesis & Audio Cues"]
        SensorSim["Kiosk Sensor Hardware Simulation"]
    end

    subgraph CoreEngine["Core Processing Engine (Python)"]
        PoseEstimator["MediaPipe Pose Landmarker (33 Joints)"]
        GeometryModule["2D/3D Posture Geometry & Vectors"]
        RuleEngine["Clinical Rule Validation Engine (BP/Weight/ECG)"]
        StateMachine["Posture State Machine (5 States)"]
        HoldController["Continuous Hold Timer (2.5s Steady)"]
        FeedbackCtrl["Audio-Visual Feedback Controller (Debounced)"]
    end

    subgraph ServiceLayer["REST API & Backend Services"]
        FlaskServer["Flask Application Factory"]
        AuthMiddleware["Device-Key Authentication (STRIDE)"]
        AnalyticsService["Anonymized Analytics Logger"]
    end

    subgraph Persistence["Storage & Configuration Layer"]
        RulesJSON["posture_rules.json (Versioned Config)"]
        SQLiteDB["kiosk_posture.db (Anonymized Sessions & Events)"]
    end

    CameraFeed -->|Video Frames / Coordinates| PoseEstimator
    PoseEstimator --> GeometryModule
    GeometryModule --> RuleEngine
    RuleEngine --> StateMachine
    StateMachine --> HoldController
    RuleEngine --> FeedbackCtrl
    HoldController -->|Trigger Event| AuthMiddleware
    AuthMiddleware -->|Hardware Activation Signal| SensorSim
    FeedbackCtrl -->|Visual Guidance| CanvasHUD
    FeedbackCtrl -->|Voice Prompts| AudioSynthesizer
    RulesJSON -.->|Thresholds| RuleEngine
    AnalyticsService --> SQLiteDB
```

---

### 2. State Transition Diagram
Represents the user alignment lifecycle at the kiosk as defined in Section 12 of the project synopsis:
`Not Detected -> Incorrect -> Correcting -> Correct -> Triggered`

```mermaid
stateDiagram-v2
    [*] --> NOT_DETECTED : System Ready / Camera Initialized

    NOT_DETECTED --> INCORRECT : User approaches kiosk (Posture errors detected)
    NOT_DETECTED --> CORRECT : User approaches in ideal posture

    INCORRECT --> CORRECTING : User starts adjusting body posture (Errors decreasing)
    CORRECTING --> INCORRECT : Misalignment worsens
    CORRECTING --> CORRECT : All clinical posture rules satisfied

    CORRECT --> INCORRECT : Posture broken / Slouched (Hold timer resets to 0.0s)
    CORRECT --> CORRECT : Posture held continuously (Timer advances 0 to 2.5s)
    CORRECT --> TRIGGERED : Posture held steady for 2.5 seconds

    TRIGGERED --> NOT_DETECTED : User departs / Scan complete / Session Reset
```

---

### 3. Sequence Diagram: Frame Processing to Sensor Activation
Shows chronological interactions across components during an active vitals measurement check-in:

```mermaid
sequenceDiagram
    autonumber
    actor User as Kiosk User
    participant Cam as Kiosk Camera
    participant UI as Kiosk Touch UI (Canvas)
    participant API as Posture API (/api/posture/analyze)
    participant Engine as Rule Engine & Geometry
    participant SM as State Machine & Hold Timer
    participant Audio as Speech Guidance
    participant Sensor as Kiosk Sensor Hardware

    User->>Cam: Position in front of kiosk
    loop Continuous Frame Capture (>=15 FPS)
        Cam->>API: Send Frame / 33 Keypoint Landmark Array
        API->>Engine: Evaluate rules (BP / Weight / ECG)
        Engine->>Engine: Calculate spine tilt, knee overlap, arm height
        Engine-->>SM: Pass / Fail status & active error list
        
        alt Posture is Incorrect
            SM->>UI: Render red skeleton & error guidance banner
            Note over Audio: If error persists >= 2.0 seconds
            SM->>Audio: Play debounced spoken instruction ("Please sit up straight")
        else Posture is Correct
            SM->>UI: Render green skeleton & animate hold progress bar (0% -> 100%)
            SM->>SM: Increment continuous hold timer
            
            opt Hold Timer reaches 2.5s
                SM->>API: Emit steady posture hold verified signal
                API->>Sensor: POST /api/posture/trigger (Auth: X-Device-Key)
                Sensor-->>UI: Display inflating BP cuff / scale reading / ECG trace
                Audio->>User: "Posture verified. Starting measurement."
            end
        end
    end
```

---

### 4. Use Case Diagram
Defines the functional interactions of kiosk users and clinical technicians:

```mermaid
flowchart LR
    User((Kiosk User))
    Admin((Kiosk Technician / Admin))

    subgraph PostureGuidanceSystem["Smart Body Posture Recognition & Guidance System"]
        UC1["Select Measurement Mode (BP, Weight, ECG)"]
        UC2["Real-Time Posture Alignment Guidance"]
        UC3["Spoken Audio Feedback Guidance"]
        UC4["Automatic Sensor Scan Trigger (2.5s Hold)"]
        UC5["View Vital Signs Scan Results"]
        UC6["Review Anonymized Operational KPIs"]
        UC7["Calibrate Posture Angle Thresholds"]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5

    Admin --> UC6
    Admin --> UC7
```

---

### 5. Data Flow Diagram (DFD Level 1)
Details the flow of information from raw video capture to anonymized analytics logging:

```mermaid
flowchart TD
    P0["Raw Camera Stream (640x480)"] --> D1["1.0 Keypoint Detection"]
    D1 -->|33 Landmark Coordinates (x,y,z)| D2["2.0 Biomechanical Geometry Analysis"]
    D2 -->|Spine Angle, Knee Distance, Arm Offset| D3["3.0 Rule Engine Validation"]
    
    RConfig[("Config Store: posture_rules.json")] -.->|Rule Parameters & Thresholds| D3
    
    D3 -->|Posture Errors & Violations| D4["4.0 Visual & Audio Controller"]
    D4 -->|Canvas Overlay & Spoken Prompts| UI["Kiosk Screen & Audio Speaker"]
    
    D3 -->|Validation Status| D5["5.0 Hold Timer & State Machine"]
    D5 -->|Steady 2.5s Hold Signal| D6["6.0 Hardware Sensor Trigger"]
    D6 -->|Device-Key Authenticated Request| KioskSensor["Vital Signs Hardware / Diagnostic Unit"]
    
    D5 -->|Anonymized Event Stream| D7["7.0 Analytics & Audit Logger"]
    D7 --> LogDB[("SQLite DB: kiosk_posture.db")]
    LogDB --> AdminUI["Admin KPI Dashboard"]
```

---

### 6. Entity Relationship Diagram (ERD)
Database schema implemented in SQLite as specified in Section 11 of the synopsis:

```mermaid
erDiagram
    SESSION ||--o{ POSTURE_EVENT : "logs"
    SESSION ||--o{ ANALYTICS_LOG : "summarizes"

    SESSION {
        string id PK "UUID"
        string measurement_type "BP, Weight, ECG"
        float started_at "Unix epoch timestamp"
        float completed_at "Unix epoch timestamp"
        int duration_ms "Total session duration"
        string status "ACTIVE, COMPLETED, ABORTED"
        int success_trigger "1 if auto-triggered, 0 otherwise"
    }

    POSTURE_EVENT {
        int id PK "Autoincrement"
        string session_id FK "References SESSION.id"
        float timestamp "Unix epoch timestamp"
        string error_type "Slouch, CrossedLegs, ArmMisaligned, etc."
        int resolved_in_ms "Duration user took to correct"
        int corrected "1 if resolved, 0 if abandoned"
    }

    ANALYTICS_LOG {
        int id PK "Autoincrement"
        string session_id FK "References SESSION.id"
        float timestamp "Unix epoch timestamp"
        string measurement_type "BP, Weight, ECG"
        int session_duration_ms "Alignment duration"
        string errors_encountered "JSON array of error IDs"
        int triggered_measurement "1 if scan started"
    }
```

---

### 7. Security and Threat Model (STRIDE)
As evaluated in Section 14 of the project synopsis:

| Asset | Threat (STRIDE) | Severity | Mitigation Implemented |
|---|---|---|---|
| **Camera Video Stream** | Information Disclosure | High | Real-time in-memory inference; raw frames are immediately discarded after keypoint extraction; zero PII / facial data stored. |
| **Sensor Trigger API** | Spoofing / Tampering | Medium | Protected with `X-Device-Key` header authentication (`@require_device_key` decorator) restricting trigger access to local kiosk hardware. |
| **Audit Logs** | Repudiation | Low | Immutable SQLite session records with UUIDs, duration metrics, and ISO timestamps. |
| **System Availability** | Denial of Service | Medium | Client-side debouncing and low-resolution (320x240) image scaling keeping frame latency <50ms (p95 SLA <= 300ms). |
