"""
Standalone Native Desktop Posture Application (OpenCV + MediaPipe)
Smart Body Posture Recognition & Guidance System
GLA University - B.Tech CSE Mini-Project (OG-Coders T-89)
"""

import sys
import time
from pathlib import Path
import cv2
import numpy as np

# Ensure project root is in path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.pose.detector import PoseDetector
from src.pose.landmarks import POSE_CONNECTIONS, PoseLandmark
from src.rules.engine import PostureRuleEngine
from src.controller.state_machine import PostureStateMachine, PostureState
from src.controller.feedback_controller import FeedbackController


def draw_hud(frame, state_info, eval_result, feedback, current_mode, fps):
    """Draws rich diagnostic HUD and guidance on OpenCV frame."""
    h, w = frame.shape[:2]

    # Top banner background
    state = state_info.get("state", "WAITING")
    is_correct = (state == PostureState.CORRECT.value or state == PostureState.TRIGGERED.value)

    if state == PostureState.TRIGGERED.value:
        banner_color = (199, 132, 2)  # Blue/Cyan
        status_text = "SENSOR ACTIVATION TRIGGERED! Measurement in progress..."
    elif state == PostureState.CORRECT.value:
        banner_color = (40, 167, 69)  # Green
        status_text = f"CORRECT POSTURE - Hold steady ({state_info.get('holdElapsed', 0.0):.1f}s / 2.5s)"
    elif state == PostureState.NOT_DETECTED.value:
        banner_color = (70, 70, 70)  # Dark Gray
        status_text = "Awaiting user in front of kiosk camera..."
    else:
        banner_color = (40, 40, 220)  # Red
        err_msg = eval_result["errors"][0]["visualMessage"] if eval_result.get("errors") else "Adjust Posture"
        status_text = f"CORRECTION REQUIRED: {err_msg}"

    cv2.rectangle(frame, (0, 0), (w, 55), banner_color, -1)
    cv2.putText(frame, status_text, (20, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    # Mode and FPS pill
    mode_text = f"Mode: {current_mode} | FPS: {fps:.1f}"
    cv2.putText(frame, mode_text, (w - 280, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 240, 255), 2)

    # Score indicator
    score = eval_result.get("score", 0.0)
    score_text = f"Posture Score: {score:.0f}%"
    cv2.putText(frame, score_text, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Bottom Hold Progress Bar
    hold_progress = state_info.get("holdProgress", 0.0)
    bar_y = h - 25
    bar_w = w - 40
    cv2.rectangle(frame, (20, bar_y), (20 + bar_w, bar_y + 14), (40, 40, 40), -1)
    fill_w = int(bar_w * hold_progress)
    if fill_w > 0:
        cv2.rectangle(frame, (20, bar_y), (20 + fill_w, bar_y + 14), (0, 220, 100), -1)
    cv2.rectangle(frame, (20, bar_y), (20 + bar_w, bar_y + 14), (200, 200, 200), 1)

    # Footer navigation instructions
    nav_text = "Keys: [1] BP Mode  [2] Weight Mode  [3] ECG Mode  [Q] Quit"
    cv2.putText(frame, nav_text, (20, h - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)


def draw_skeleton(frame, landmarks, highlight_joints):
    """Renders keypoint joints and bones with red highlights for errors."""
    if not landmarks:
        return

    h, w = frame.shape[:2]
    hl_set = set(highlight_joints or [])

    # Draw connection lines
    for p1_idx, p2_idx in POSE_CONNECTIONS:
        if p1_idx >= len(landmarks) or p2_idx >= len(landmarks):
            continue
        p1 = landmarks[p1_idx]
        p2 = landmarks[p2_idx]
        if p1.visibility < 0.3 or p2.visibility < 0.3:
            continue

        x1, y1 = int(p1.x * w), int(p1.y * h)
        x2, y2 = int(p2.x * w), int(p2.y * h)

        name1 = PoseLandmark(p1_idx).name
        name2 = PoseLandmark(p2_idx).name
        in_error = (name1 in hl_set) or (name2 in hl_set)

        color = (0, 0, 255) if in_error else (0, 210, 255)
        thickness = 3 if in_error else 2
        cv2.line(frame, (x1, y1), (x2, y2), color, thickness)

    # Draw keypoint circles
    for idx, pt in enumerate(landmarks):
        if pt.visibility < 0.3:
            continue
        name = PoseLandmark(idx).name
        x, y = int(pt.x * w), int(pt.y * h)
        is_error = name in hl_set

        if is_error:
            cv2.circle(frame, (x, y), 8, (0, 0, 255), -1)
            cv2.circle(frame, (x, y), 12, (0, 0, 255), 2)
        else:
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.circle(frame, (x, y), 6, (255, 255, 255), 1)


def main():
    print("=" * 65)
    print(" Smart Body Posture Recognition & Guidance System (Desktop Mode)")
    print(" Initializing MediaPipe Pose Detector & Rule Engine...")
    print("=" * 65)

    detector = PoseDetector()
    rule_engine = PostureRuleEngine()
    state_machine = PostureStateMachine(hold_duration=2.5)
    feedback_controller = FeedbackController()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[DesktopApp] Warning: Camera index 0 could not be opened.")
        print("[DesktopApp] To experience the complete system with simulator presets, run: python run_kiosk.py")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    current_mode = "BP"
    prev_time = time.time()

    print("\n[DesktopApp] Camera active. Showing window...")
    print("Controls: [1] BP  [2] Weight  [3] ECG  [Q] Quit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Mirror frame for natural self-view
            frame = cv2.flip(frame, 1)

            # Detect keypoints
            landmarks = detector.detect_landmarks(frame)
            person_detected = landmarks is not None and len(landmarks) > 0

            # Evaluate posture
            eval_result = rule_engine.evaluate_posture(landmarks, measurement_type=current_mode)

            # Update State Machine
            state_info = state_machine.update(
                person_detected=person_detected,
                errors=eval_result["errors"],
            )

            # Process Feedback & Audio Debouncing
            feedback = feedback_controller.process_errors(
                errors=eval_result["errors"],
                person_present=person_detected,
            )

            # Calculate FPS
            now = time.time()
            fps = 1.0 / (now - prev_time) if (now - prev_time) > 0 else 20.0
            prev_time = now

            # Render visual overlays
            draw_skeleton(frame, landmarks, eval_result.get("highlightJoints", []))
            draw_hud(frame, state_info, eval_result, feedback, current_mode, fps)

            cv2.imshow("Smart Posture Guidance System (GLA University T-89)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('1'):
                current_mode = "BP"
                state_machine.reset_session()
                feedback_controller.reset()
            elif key == ord('2'):
                current_mode = "Weight"
                state_machine.reset_session()
                feedback_controller.reset()
            elif key == ord('3'):
                current_mode = "ECG"
                state_machine.reset_session()
                feedback_controller.reset()

    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()
        print("\n[DesktopApp] Exited cleanly.")


if __name__ == "__main__":
    main()
