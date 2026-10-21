"""Pose package initialization."""
from src.pose.landmarks import PoseLandmark, Point3D, POSE_CONNECTIONS
from src.pose.geometry import (
    calculate_angle_3points,
    calculate_inclination_to_vertical,
    calculate_tilt_angle,
    calculate_distance,
    calculate_midpoint,
    check_legs_crossed,
    check_arm_heart_level,
    calculate_torso_dimensions,
    get_point,
)
from src.pose.detector import PoseDetector

__all__ = [
    "PoseLandmark",
    "Point3D",
    "POSE_CONNECTIONS",
    "calculate_angle_3points",
    "calculate_inclination_to_vertical",
    "calculate_tilt_angle",
    "calculate_distance",
    "calculate_midpoint",
    "check_legs_crossed",
    "check_arm_heart_level",
    "calculate_torso_dimensions",
    "get_point",
    "PoseDetector",
]
