"""
MediaPipe Pose Keypoint Detector
Smart Body Posture Recognition & Guidance System
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import cv2

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

from src.pose.landmarks import Point3D, PoseLandmark


class PoseDetector:
    """Wrapper around MediaPipe PoseLandmarker for kiosk camera streams and frame analysis."""

    def __init__(self, model_path: Optional[str] = None):
        self.detector = None
        self.model_path = model_path
        if not self.model_path:
            base_dir = Path(__file__).resolve().parent.parent.parent
            default_path = base_dir / "models" / "pose_landmarker_lite.task"
            if default_path.exists():
                self.model_path = str(default_path)

        self._init_detector()

    def _init_detector(self) -> None:
        """Initializes the MediaPipe PoseLandmarker if model and library are available."""
        if not MEDIAPIPE_AVAILABLE or not self.model_path or not os.path.exists(self.model_path):
            self.detector = None
            return

        try:
            base_options = mp_python.BaseOptions(model_asset_path=self.model_path)
            options = mp_vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=mp_vision.RunningMode.IMAGE,
                num_poses=1,
                min_pose_detection_confidence=0.5,
                min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5,
                output_segmentation_masks=False,
            )
            self.detector = mp_vision.PoseLandmarker.create_from_options(options)
        except Exception as e:
            print(f"[PoseDetector] Warning: Could not initialize MediaPipe detector: {e}")
            self.detector = None

    def detect_landmarks(self, frame_bgr: np.ndarray) -> Optional[List[Point3D]]:
        """
        Detects 33 human pose landmarks from an OpenCV BGR image.
        Returns a list of 33 Point3D instances or None if no pose is detected.
        """
        if self.detector is None or frame_bgr is None:
            return None

        # Convert OpenCV BGR to RGB
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        try:
            detection_result = self.detector.detect(mp_image)
            if not detection_result.pose_landmarks or len(detection_result.pose_landmarks) == 0:
                return None

            raw_landmarks = detection_result.pose_landmarks[0]
            landmarks = [
                Point3D(
                    x=lm.x,
                    y=lm.y,
                    z=lm.z if hasattr(lm, "z") else 0.0,
                    visibility=lm.visibility if hasattr(lm, "visibility") and lm.visibility is not None else 1.0,
                )
                for lm in raw_landmarks
            ]
            return landmarks
        except Exception as e:
            print(f"[PoseDetector] Detection error: {e}")
            return None

    def close(self) -> None:
        """Releases detector resources."""
        if self.detector:
            try:
                self.detector.close()
            except Exception:
                pass
            self.detector = None
