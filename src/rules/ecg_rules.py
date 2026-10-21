"""
Electrocardiogram (ECG) Diagnostic Scan Posture Validation Rules
Smart Body Posture Recognition & Guidance System
"""

from typing import List, Dict, Any, Optional
from src.pose.landmarks import Point3D, PoseLandmark
from src.pose.geometry import (
    get_point,
    calculate_midpoint,
    calculate_inclination_to_vertical,
    calculate_distance,
    check_legs_crossed,
)
from src.rules.base_rule import BasePostureRule, RuleEvaluationResult, PostureError, ErrorSeverity


class ECGSeatedUprightRule(BasePostureRule):
    """Rule verifying upright seated position with back supported."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ECG_SEATED_UPRIGHT", "Upright Seated Position", config)
        self.max_spine_tilt = float(self.config.get("maxAllowed", 15.0))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
        r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
        l_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
        r_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)

        if not (l_sh and r_sh and l_hip and r_hip):
            return RuleEvaluationResult(passed=True, metric_name="spine_tilt_deg", metric_value=0.0)

        mid_sh = calculate_midpoint(l_sh, r_sh)
        mid_hip = calculate_midpoint(l_hip, r_hip)
        tilt = calculate_inclination_to_vertical(mid_sh, mid_hip)

        passed = tilt <= self.max_spine_tilt
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.CRITICAL,
                visual_message=self.config.get("visualMessage", "Sit back comfortably and keep your spine upright"),
                metric_name="spine_tilt_deg",
                metric_value=tilt,
                threshold_value=self.max_spine_tilt,
                highlight_joints=["LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_HIP", "RIGHT_HIP"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="spine_tilt_deg", metric_value=tilt)


class ECGUncrossedLegsRule(BasePostureRule):
    """Rule verifying legs are uncrossed with feet flat to prevent baseline wandering."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ECG_UNCROSSED_LEGS", "Legs Uncrossed & Grounded", config)

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        is_crossed, separation_metric = check_legs_crossed(landmarks)
        passed = not is_crossed
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.CRITICAL,
                visual_message=self.config.get("visualMessage", "Keep feet flat on the floor and uncross legs"),
                metric_name="knee_separation_ratio",
                metric_value=separation_metric,
                threshold_value=0.28,
                highlight_joints=["LEFT_KNEE", "RIGHT_KNEE", "LEFT_ANKLE", "RIGHT_ANKLE"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="knee_separation_ratio", metric_value=separation_metric)


class ECGArmsRestingRule(BasePostureRule):
    """Rule verifying forearms/hands are placed steadily on sensor contact pads."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("ECG_ARMS_RESTING", "Forearms Resting on Electrodes", config)

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
        r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
        l_wr = get_point(landmarks, PoseLandmark.LEFT_WRIST)
        r_wr = get_point(landmarks, PoseLandmark.RIGHT_WRIST)

        if not (l_sh and r_sh and (l_wr or r_wr)):
            return RuleEvaluationResult(passed=True, metric_name="arm_elevation", metric_value=0.0)

        # Arms should be lowered (wrists lower than shoulders, y_wr > y_sh in image coords)
        arms_raised = False
        active_joints = []
        if l_wr and l_wr.y < l_sh.y:
            arms_raised = True
            active_joints.extend(["LEFT_SHOULDER", "LEFT_WRIST"])
        if r_wr and r_wr.y < r_sh.y:
            arms_raised = True
            active_joints.extend(["RIGHT_SHOULDER", "RIGHT_WRIST"])

        passed = not arms_raised
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.CRITICAL,
                visual_message=self.config.get("visualMessage", "Rest forearms gently on the sensor pads"),
                metric_name="arm_elevation",
                metric_value=1.0 if arms_raised else 0.0,
                threshold_value=0.0,
                highlight_joints=active_joints,
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="arm_elevation", metric_value=1.0 if arms_raised else 0.0)
