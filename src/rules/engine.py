"""
Posture Rule Engine Orchestrator
Smart Body Posture Recognition & Guidance System
"""

from typing import Dict, List, Optional, Any, Tuple
from src.pose.landmarks import Point3D
from src.rules.base_rule import BasePostureRule, PostureError, ErrorSeverity
from src.rules.bp_rules import BPSlouchRule, BPCrossedLegsRule, BPArmAlignmentRule, BPHeadLevelRule
from src.rules.weight_rules import WeightStandingUprightRule, WeightBalancedFeetRule, WeightArmsAtSidesRule
from src.rules.ecg_rules import ECGSeatedUprightRule, ECGUncrossedLegsRule, ECGArmsRestingRule
from config.settings import load_posture_rules


class PostureRuleEngine:
    """Evaluates human pose landmarks against clinical posture rules per vital measurement type."""

    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        self.config_data = config_data or load_posture_rules()
        self.rules_registry: Dict[str, List[BasePostureRule]] = {}
        self._init_rules()

    def _init_rules(self) -> None:
        """Instantiates rule objects based on configuration."""
        measurements = self.config_data.get("measurementTypes", {})

        # BP Rules
        bp_configs = {r["id"]: r for r in measurements.get("BP", {}).get("rules", [])}
        self.rules_registry["BP"] = [
            BPSlouchRule(bp_configs.get("BP_NO_SLOUCH")),
            BPCrossedLegsRule(bp_configs.get("BP_UNCROSSED_LEGS")),
            BPArmAlignmentRule(bp_configs.get("BP_ARM_HEART_LEVEL")),
            BPHeadLevelRule(bp_configs.get("BP_HEAD_LEVEL")),
        ]

        # Weight Rules
        wt_configs = {r["id"]: r for r in measurements.get("Weight", {}).get("rules", [])}
        self.rules_registry["Weight"] = [
            WeightStandingUprightRule(wt_configs.get("WT_STANDING_UPRIGHT")),
            WeightBalancedFeetRule(wt_configs.get("WT_BALANCED_FEET")),
            WeightArmsAtSidesRule(wt_configs.get("WT_ARMS_AT_SIDES")),
        ]

        # ECG Rules
        ecg_configs = {r["id"]: r for r in measurements.get("ECG", {}).get("rules", [])}
        self.rules_registry["ECG"] = [
            ECGSeatedUprightRule(ecg_configs.get("ECG_SEATED_UPRIGHT")),
            ECGUncrossedLegsRule(ecg_configs.get("ECG_UNCROSSED_LEGS")),
            ECGArmsRestingRule(ecg_configs.get("ECG_ARMS_RESTING")),
        ]

    def reload_config(self, new_config: Dict[str, Any]) -> None:
        """Reloads engine rules with modified parameters."""
        self.config_data = new_config
        self._init_rules()

    def get_supported_measurements(self) -> List[str]:
        return list(self.rules_registry.keys())

    def get_hold_duration(self, measurement_type: str) -> float:
        """Returns the hold duration in seconds configured for this measurement."""
        meas = self.config_data.get("measurementTypes", {}).get(measurement_type, {})
        return float(meas.get("holdDurationSeconds", 2.5))

    def evaluate_posture(
        self,
        landmarks: Optional[List[Point3D]],
        measurement_type: str = "BP",
    ) -> Dict[str, Any]:
        """
        Evaluates detected landmarks against rules for the specified measurement type.
        Returns a dictionary matching the API specification:
        {
            "status": "CORRECT" | "INCORRECT" | "NO_PERSON_DETECTED",
            "score": float (0-100),
            "errors": [ PostureError.to_dict() ],
            "metrics": { metric_name: value },
            "highlightJoints": [ joint_name, ... ]
        }
        """
        if not landmarks or len(landmarks) == 0:
            return {
                "status": "NO_PERSON_DETECTED",
                "score": 0.0,
                "errors": [],
                "metrics": {},
                "highlightJoints": [],
                "primaryGuidance": "Please position yourself in front of the kiosk camera.",
                "measurementType": measurement_type,
            }

        # Normalize measurement type key
        norm_type = measurement_type.upper()
        if norm_type == "WEIGHT":
            norm_type = "Weight"
        elif norm_type == "ECG":
            norm_type = "ECG"
        elif norm_type == "BP":
            norm_type = "BP"
        else:
            norm_type = "BP"

        rules = self.rules_registry.get(norm_type, self.rules_registry["BP"])

        errors: List[PostureError] = []
        metrics: Dict[str, float] = {}
        highlight_joints: List[str] = []
        total_rules = len(rules)
        passed_rules = 0

        for rule in rules:
            result = rule.evaluate(landmarks)
            if result.metric_name:
                metrics[result.metric_name] = round(result.metric_value, 2)

            if result.passed:
                passed_rules += 1
            else:
                if result.error:
                    errors.append(result.error)
                    for joint in result.error.highlight_joints:
                        if joint not in highlight_joints:
                            highlight_joints.append(joint)

        score = round((passed_rules / total_rules) * 100.0, 1) if total_rules > 0 else 100.0
        status = "CORRECT" if len(errors) == 0 else "INCORRECT"

        # Determine primary guidance message
        if status == "CORRECT":
            primary_guidance = "Posture is correct! Please hold steady."
        else:
            # Sort errors by severity: CRITICAL first, then WARNING, then INFO
            severity_order = {ErrorSeverity.CRITICAL: 0, ErrorSeverity.WARNING: 1, ErrorSeverity.INFO: 2}
            errors.sort(key=lambda e: severity_order.get(e.severity, 3))
            primary_guidance = errors[0].visual_message

        return {
            "status": status,
            "score": score,
            "errors": [e.to_dict() for e in errors],
            "metrics": metrics,
            "highlightJoints": highlight_joints,
            "primaryGuidance": primary_guidance,
            "measurementType": norm_type,
        }
