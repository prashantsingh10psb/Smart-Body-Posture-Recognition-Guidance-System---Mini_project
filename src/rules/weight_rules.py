"""
Weight & Body Composition Posture Validation Rules
Smart Body Posture Recognition & Guidance System
"""

from typing import List, Dict, Any, Optional
from src.pose.landmarks import Point3D, PoseLandmark
from src.pose.geometry import (
    get_point,
    calculate_midpoint,
    calculate_inclination_to_vertical,
    calculate_tilt_angle,
    calculate_distance,
    calculate_angle_3points,
)
from src.rules.base_rule import BasePostureRule, RuleEvaluationResult, PostureError, ErrorSeverity


class WeightStandingUprightRule(BasePostureRule):
    """Rule verifying upright standing alignment on the scale platform."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("WT_STANDING_UPRIGHT", "Stand Straight", config)
        self.max_lateral_tilt = float(self.config.get("maxAllowed", 10.0))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
        r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
        l_ankle = get_point(landmarks, PoseLandmark.LEFT_ANKLE)
        r_ankle = get_point(landmarks, PoseLandmark.RIGHT_ANKLE)

        if not (l_sh and r_sh and l_ankle and r_ankle):
            return RuleEvaluationResult(passed=True, metric_name="standing_tilt_deg", metric_value=0.0)

        mid_sh = calculate_midpoint(l_sh, r_sh)
        mid_ank = calculate_midpoint(l_ankle, r_ankle)
        tilt = calculate_inclination_to_vertical(mid_sh, mid_ank)

        passed = tilt <= self.max_lateral_tilt
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.CRITICAL,
                visual_message=self.config.get("visualMessage", "Stand tall and centered on the scale"),
                metric_name="standing_tilt_deg",
                metric_value=tilt,
                threshold_value=self.max_lateral_tilt,
                highlight_joints=["LEFT_SHOULDER", "RIGHT_SHOULDER", "LEFT_ANKLE", "RIGHT_ANKLE"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="standing_tilt_deg", metric_value=tilt)


class WeightBalancedFeetRule(BasePostureRule):
    """Rule verifying even weight distribution between left and right feet."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("WT_BALANCED_FEET", "Even Weight Distribution", config)
        self.max_hip_tilt = float(self.config.get("maxAllowed", 8.0))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        l_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
        r_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)

        if not (l_hip and r_hip):
            return RuleEvaluationResult(passed=True, metric_name="hip_tilt_deg", metric_value=0.0)

        hip_tilt = calculate_tilt_angle(l_hip, r_hip)
        passed = hip_tilt <= self.max_hip_tilt
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.WARNING,
                visual_message=self.config.get("visualMessage", "Distribute your weight evenly on both feet"),
                metric_name="hip_tilt_deg",
                metric_value=hip_tilt,
                threshold_value=self.max_hip_tilt,
                highlight_joints=["LEFT_HIP", "RIGHT_HIP"],
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="hip_tilt_deg", metric_value=hip_tilt)


class WeightArmsAtSidesRule(BasePostureRule):
    """Rule verifying arms hang naturally at sides and user is not leaning on railings."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("WT_ARMS_AT_SIDES", "Arms Relaxed at Sides", config)
        self.max_abduction = float(self.config.get("maxAllowed", 28.0))

    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
        r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
        l_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
        r_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)
        l_wr = get_point(landmarks, PoseLandmark.LEFT_WRIST)
        r_wr = get_point(landmarks, PoseLandmark.RIGHT_WRIST)

        if not (l_sh and r_sh and l_hip and r_hip and (l_wr or r_wr)):
            return RuleEvaluationResult(passed=True, metric_name="arm_abduction_deg", metric_value=0.0)

        max_angle = 0.0
        active_joints = []
        if l_wr and l_hip and l_sh:
            angle_l = calculate_angle_3points(l_wr, l_sh, l_hip)
            if angle_l > max_angle:
                max_angle = angle_l
                active_joints = ["LEFT_SHOULDER", "LEFT_WRIST"]

        if r_wr and r_hip and r_sh:
            angle_r = calculate_angle_3points(r_wr, r_sh, r_hip)
            if angle_r > max_angle:
                max_angle = angle_r
                active_joints = ["RIGHT_SHOULDER", "RIGHT_WRIST"]

        passed = max_angle <= self.max_abduction
        error = None
        if not passed:
            error = PostureError(
                rule_id=self.rule_id,
                name=self.name,
                severity=ErrorSeverity.WARNING,
                visual_message=self.config.get("visualMessage", "Keep arms relaxed at sides without leaning on rails"),
                metric_name="arm_abduction_deg",
                metric_value=max_angle,
                threshold_value=self.max_abduction,
                highlight_joints=active_joints,
            )

        return RuleEvaluationResult(passed=passed, error=error, metric_name="arm_abduction_deg", metric_value=max_angle)
