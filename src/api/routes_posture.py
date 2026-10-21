"""
Posture Analysis and Sensor Trigger API Routes
Smart Body Posture Recognition & Guidance System
"""

import time
import base64
import random
import cv2
import numpy as np
from flask import Blueprint, request, jsonify

from src.rules.engine import PostureRuleEngine
from src.controller.state_machine import PostureStateMachine, PostureState
from src.controller.feedback_controller import FeedbackController
from src.pose.detector import PoseDetector
from src.pose.landmarks import Point3D
from src.api.auth import require_device_key
from config.settings import load_posture_rules, save_posture_rules

posture_bp = Blueprint("posture", __name__, url_prefix="/api/posture")

# Singleton engine, state machine, feedback controller, and detector
rule_engine = PostureRuleEngine()
state_machine = PostureStateMachine(hold_duration=rule_engine.get_hold_duration("BP"))
feedback_controller = FeedbackController()
pose_detector = PoseDetector()


@posture_bp.route("/analyze", methods=["POST"])
def analyze_posture():
    """
    Endpoint: POST /api/posture/analyze (Section 10.2)
    Accepts:
      {
        "measurementType": "BP" | "Weight" | "ECG",
        "keypoints": [ {x, y, z, visibility}, ... ],
        "sessionId": Optional[str]
      }
    Returns:
      200 { status, score, errors: [], metrics: {}, holdProgress, isTriggered, state, feedback: {} }
    """
    start_time = time.time()
    data = request.get_json(force=True, silent=True) or {}
    measurement_type = data.get("measurementType", "BP")
    raw_keypoints = data.get("keypoints", [])

    # Update hold duration for the measurement type if needed
    hold_duration = rule_engine.get_hold_duration(measurement_type)
    state_machine.set_hold_duration(hold_duration)

    landmarks = None
    if raw_keypoints and len(raw_keypoints) > 0:
        landmarks = [Point3D.from_dict(kp) for kp in raw_keypoints]

    # Evaluate rules
    eval_result = rule_engine.evaluate_posture(landmarks, measurement_type=measurement_type)
    person_detected = (eval_result["status"] != "NO_PERSON_DETECTED")

    # Update state machine & hold timer
    sm_result = state_machine.update(
        person_detected=person_detected,
        errors=eval_result["errors"],
    )

    # Process visual feedback
    feedback_result = feedback_controller.process_errors(
        errors=eval_result["errors"],
        person_present=person_detected,
    )

    processing_latency_ms = round((time.time() - start_time) * 1000.0, 2)

    return jsonify({
        "status": eval_result["status"],
        "score": eval_result["score"],
        "errors": eval_result["errors"],
        "metrics": eval_result["metrics"],
        "highlightJoints": eval_result["highlightJoints"],
        "measurementType": eval_result["measurementType"],
        "state": sm_result["state"],
        "holdElapsed": sm_result["holdElapsed"],
        "holdProgress": sm_result["holdProgress"],
        "isTriggered": sm_result["isTriggered"],
        "statusMessage": sm_result["statusMessage"],
        "feedback": {
            "visualMessage": feedback_result["visualMessage"],
        },
        "latencyMs": processing_latency_ms,
    }), 200


@posture_bp.route("/analyze-frame", methods=["POST"])
def analyze_frame():
    """
    Endpoint: POST /api/posture/analyze-frame
    Accepts base64 encoded frame or multipart image file for server-side MediaPipe inference.
    """
    start_time = time.time()
    measurement_type = request.form.get("measurementType", "BP")
    frame = None

    if "frame" in request.files:
        file_bytes = np.frombuffer(request.files["frame"].read(), np.uint8)
        frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    else:
        json_data = request.get_json(silent=True) or {}
        measurement_type = json_data.get("measurementType", measurement_type)
        b64_img = json_data.get("image")
        if b64_img:
            if "," in b64_img:
                b64_img = b64_img.split(",", 1)[1]
            try:
                img_data = base64.b64decode(b64_img)
                nparr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception as e:
                return jsonify({"error": f"Invalid base64 image: {e}"}), 400

    landmarks = None
    if frame is not None:
        landmarks = pose_detector.detect_landmarks(frame)

    keypoints_json = [lm.to_dict() for lm in landmarks] if landmarks else []

    # Evaluate rules
    eval_result = rule_engine.evaluate_posture(landmarks, measurement_type=measurement_type)
    person_detected = (landmarks is not None and len(landmarks) > 0)

    sm_result = state_machine.update(
        person_detected=person_detected,
        errors=eval_result["errors"],
    )

    feedback_result = feedback_controller.process_errors(
        errors=eval_result["errors"],
        person_present=person_detected,
    )

    latency_ms = round((time.time() - start_time) * 1000.0, 2)

    return jsonify({
        "status": eval_result["status"],
        "score": eval_result["score"],
        "errors": eval_result["errors"],
        "metrics": eval_result["metrics"],
        "highlightJoints": eval_result["highlightJoints"],
        "keypoints": keypoints_json,
        "state": sm_result["state"],
        "holdProgress": sm_result["holdProgress"],
        "isTriggered": sm_result["isTriggered"],
        "statusMessage": sm_result["statusMessage"],
        "feedback": {
            "visualMessage": feedback_result["visualMessage"],
        },
        "latencyMs": latency_ms,
    }), 200


@posture_bp.route("/trigger", methods=["POST"])
@require_device_key
def trigger_sensor():
    """
    Endpoint: POST /api/posture/trigger (Section 10.2)
    Requires Device-key authentication.
    Triggers simulated vital sensor reading upon successful posture hold.
    """
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get("sessionId", "session-simulated")
    measurement_type = data.get("measurementType", "BP").upper()

    timestamp = time.time()

    # Generate realistic simulated vital measurement based on type
    if measurement_type == "BP":
        systolic = random.randint(114, 126)
        diastolic = random.randint(74, 82)
        pulse = random.randint(68, 78)
        measurement_data = {
            "type": "Blood Pressure",
            "systolic": systolic,
            "diastolic": diastolic,
            "pulseBpm": pulse,
            "unit": "mmHg",
            "clinicalClassification": "Optimal / Normal BP (Accurate Posture Ensured)",
            "postureQualityOffset": "0 mmHg distortion (Slouch avoided)",
        }
    elif measurement_type == "WEIGHT":
        weight_kg = round(random.uniform(64.5, 75.2), 1)
        bmi = round(weight_kg / ((1.72) ** 2), 1)
        measurement_data = {
            "type": "Weight & Body Composition",
            "weightKg": weight_kg,
            "bmi": bmi,
            "bodyFatPercentage": round(random.uniform(16.5, 21.0), 1),
            "muscleMassKg": round(weight_kg * 0.42, 1),
            "balanceSymmetry": "50% Left / 50% Right",
        }
    elif measurement_type == "ECG":
        bpm = random.randint(66, 76)
        measurement_data = {
            "type": "ECG Diagnostic Scan",
            "heartRateBpm": bpm,
            "rhythm": "Normal Sinus Rhythm",
            "noiseArtifacts": "Minimal (<0.5 mV) - Proper arm placement confirmed",
            "qtIntervalMs": 395,
            "prIntervalMs": 155,
        }
    else:
        measurement_data = {"type": measurement_type, "status": "Reading Acquired"}

    return jsonify({
        "triggered": True,
        "sessionId": session_id,
        "measurementType": measurement_type,
        "timestamp": timestamp,
        "measurement": measurement_data,
        "message": f"Kiosk sensor hardware activated successfully for {measurement_type}.",
    }), 200


@posture_bp.route("/reset", methods=["POST"])
def reset_posture_session():
    """Resets the state machine and feedback controller."""
    state_machine.reset_session()
    feedback_controller.reset()
    return jsonify({"status": "reset", "message": "Posture state machine and hold timer reset."}), 200


@posture_bp.route("/rules", methods=["GET"])
def get_rules():
    """Returns currently active posture rule definitions."""
    return jsonify(rule_engine.config_data), 200


@posture_bp.route("/rules", methods=["PUT"])
def update_rules():
    """Allows kiosk technician to update rule thresholds and parameters."""
    new_config = request.get_json(force=True, silent=True)
    if not new_config:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        save_posture_rules(new_config)
        rule_engine.reload_config(new_config)
        return jsonify({"status": "updated", "message": "Posture rules configuration saved and reloaded."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save configuration: {e}"}), 500
