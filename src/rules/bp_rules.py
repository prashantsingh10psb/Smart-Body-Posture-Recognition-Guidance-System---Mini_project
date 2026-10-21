"""
Blood Pressure (BP) Measurement Posture Validation Rules
Smart Body Posture Recognition & Guidance System
"""

from typing import List, Dict, Any, Optional
from src.pose.landmarks import Point3D, PoseLandmark
from src.pose.geometry import (
    get_point,
    calculate_midpoint,
    calculate_inclination_to_vertical,
    calculate_torso_dimensions,
    check_legs_crossed,
    check_arm_heart_level,
)
from src.rules.base_rule import BasePostureRule, RuleEvaluationResult, PostureError, ErrorSeverity


class BPSlouchRule(BasePostureRule):
    """Rule verifying that the user sits upright without slouching."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("BP_NO_SLOUCH", "Upright Spine (No Slouching)", config)
        self.max_spine_tilt = float(self.config.get("maxAllowed", 18.0))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
        r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
        l_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
        r_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)

        if not (l_sh and r_sh and l_hip and r_hip):
            return RuleEvaluationResult(passed=True, metric_name="spine_tilt_angle_deg", metric_value=0.0)

        mid_sh = calculate_midpoint(l_sh, r_sh)
        mid_hip = calculate_midpoint(l_hip, r_hip)
        tilt_angle = calculate_inclination_to_vertical(mid_sh, mid_hip)

        passed = tilt_angle <= self.max_spine_tilt
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.CRITICAL,
                visual_message=self.config.get("visualMessage", "Sit up straight against the backrest"),
                metric_name="spine_tilt_angle_deg",
                metric_value=tilt_angle,
                threshold_value=self.max_spine_tilt,
                highlight_joints=["LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="spine_tilt_angle_deg", metric_value=tilt_angle)


class BPCrossedLegsRule(BasePostureRule):
    """Rule verifying uncrossed legs and feet flat on floor."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("BP_UNCROSSED_LEGS", "Uncrossed Legs & Level Knees", config)

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        is_crossed, separation_metric = check_legs_crossed(landmarks)

        passed = not is_crossed
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.CRITICAL,
                visual_message=self.config.get("visualMessage", "Uncross your legs and keep feet flat on the floor"),
                metric_name="knee_separation_ratio",
                metric_value=separation_metric,
                threshold_value=0.28,
                highlight_joints=["LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="knee_separation_ratio", metric_value=separation_metric)


class BPArmAlignmentRule(BasePostureRule):
    """Rule verifying arm is rested at heart level for cuff measurement."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("BP_ARM_HEART_LEVEL", "Arm at Heart Level", config)
        self.max_offset_ratio = float(self.config.get("maxAllowed", 0.22))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        is_aligned, offset_ratio, active_arm = check_arm_heart_level(landmarks)

        passed = is_aligned
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.WARNING,
                visual_message=self.config.get("visualMessage", "Rest your arm on the table at heart level"),
                metric_name="arm_heart_offset_ratio",
                metric_value=offset_ratio,
                threshold_value=self.max_offset_ratio,
                highlight_joints=[
                    f"{active_arm}_SHOULDER" if active_arm in ("LEFT", "RIGHT") else "LEFT_SHOULDER",
                    f"{active_arm}_ELBOW" if active_arm in ("LEFT", "RIGHT") else "LEFT_ELBOW",
                    f"{active_arm}_WRIST" if active_arm in ("LEFT", "RIGHT") else "LEFT_WRIST",
                ],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="arm_heart_offset_ratio", metric_value=offset_ratio)


class BPHeadLevelRule(BasePostureRule):
    """Rule verifying head and neck are neutral."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("BP_HEAD_LEVEL", "Head & Neck Neutral", config)
        self.max_flexion = float(self.config.get("maxAllowed", 25.0))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        nose = get_point(landmarks, PoseLandmark.NOSE)
        l_ear = get_point(landmarks, PoseLandmark.LEFT_EAR)
        r_ear = get_point(landmarks, PoseLandmark.RIGHT_EAR)
        l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
        r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)

        if not (nose and (l_ear or r_ear) and (l_sh and r_sh)):
            return RuleEvaluationResult(passed=True, metric_name="neck_flexion_deg", metric_value=0.0)

        ear = l_ear if (l_ear and l_ear.visibility > 0.5) else r_ear
        mid_sh = calculate_midpoint(l_sh, r_sh)
        flexion_angle = calculate_inclination_to_vertical(nose, mid_sh)

        passed = flexion_angle <= self.max_flexion
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.INFO,
                visual_message=self.config.get("visualMessage", "Keep your head up and look forward"),
                metric_name="neck_flexion_deg",
                metric_value=flexion_angle,
                threshold_value=self.max_flexion,
                highlight_joints=["NOSE", "LEFT_EAR", "RIGHT_EAR", "LEFT_SHOULDER", "RIGHT_SHOULDER"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="neck_flexion_deg", metric_value=flexion_angle)
