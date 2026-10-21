"""
Unit Tests for Posture Rule Engine and Clinical Rule Sets
Smart Body Posture Recognition & Guidance System
"""

import pytest
from src.pose.landmarks import Point3D, PoseLandmark
from src.rules.engine import PostureRuleEngine
from src.rules.bp_rules import BPSlouchRule, BPCrossedLegsRule, BPArmAlignmentRule
from src.rules.weight_rules import WeightStandingUprightRule, WeightBalancedFeetRule, WeightArmsAtSidesRule
from src.rules.ecg_rules import ECGSeatedUprightRule, ECGUncrossedLegsRule, ECGArmsRestingRule


def create_mock_landmarks(overrides=None):
    """Generates standard 33 pose landmark list with optional position overrides."""
    landmarks = [Point3D(0.5, 0.5, 0.0, 1.0) for _ in range(33)]

    # Standard upright seated default
    defaults = {
        PoseLandmark.NOSE: Point3D(0.5, 0.18),
        PoseLandmark.LEFT_EAR: Point3D(0.46, 0.18),
        PoseLandmark.RIGHT_EAR: Point3D(0.54, 0.18),
        PoseLandmark.LEFT_SHOULDER: Point3D(0.40, 0.30),
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.60, 0.30),
        PoseLandmark.LEFT_ELBOW: Point3D(0.35, 0.38),
        PoseLandmark.RIGHT_ELBOW: Point3D(0.65, 0.38),
        PoseLandmark.LEFT_WRIST: Point3D(0.42, 0.38),
        PoseLandmark.RIGHT_WRIST: Point3D(0.58, 0.38),
        PoseLandmark.LEFT_HIP: Point3D(0.42, 0.60),
        PoseLandmark.RIGHT_HIP: Point3D(0.58, 0.60),
        PoseLandmark.LEFT_KNEE: Point3D(0.38, 0.80),
        PoseLandmark.RIGHT_KNEE: Point3D(0.62, 0.80),
        PoseLandmark.LEFT_ANKLE: Point3D(0.38, 0.95),
        PoseLandmark.RIGHT_ANKLE: Point3D(0.62, 0.95),
    }

    for idx, pt in defaults.items():
        landmarks[int(idx)] = pt

    if overrides:
        for idx, pt in overrides.items():
            landmarks[int(idx)] = pt

    return landmarks


def test_bp_slouch_rule():
    rule = BPSlouchRule()

    # Upright posture: should pass
    upright = create_mock_landmarks()
    res_upright = rule.evaluate(upright)
    assert res_upright.passed is True
    assert res_upright.error is None
    assert res_upright.metric_value < 10.0

    # Slouched posture: shoulders tilted forward significantly
    slouched = create_mock_landmarks({
        PoseLandmark.LEFT_SHOULDER: Point3D(0.65, 0.30),
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.85, 0.30),
    })
    res_slouched = rule.evaluate(slouched)
    assert res_slouched.passed is False
    assert res_slouched.error is not None
    assert res_slouched.error.rule_id == "BP_NO_SLOUCH"
    assert "straight" in res_slouched.error.visual_message.lower()


def test_bp_crossed_legs_rule():
    rule = BPCrossedLegsRule()

    # Uncrossed: knees apart
    uncrossed = create_mock_landmarks()
    assert rule.evaluate(uncrossed).passed is True

    # Crossed: knees squeezed/overlapping
    crossed = create_mock_landmarks({
        PoseLandmark.LEFT_KNEE: Point3D(0.51, 0.80),
        PoseLandmark.RIGHT_KNEE: Point3D(0.49, 0.80),
    })
    res = rule.evaluate(crossed)
    assert res.passed is False
    assert res.error.rule_id == "BP_UNCROSSED_LEGS"


def test_weight_rules():
    engine = PostureRuleEngine()

    standing_good = create_mock_landmarks({
        PoseLandmark.LEFT_SHOULDER: Point3D(0.42, 0.25),
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.58, 0.25),
        PoseLandmark.LEFT_HIP: Point3D(0.44, 0.50),
        PoseLandmark.RIGHT_HIP: Point3D(0.56, 0.50),
        PoseLandmark.LEFT_ANKLE: Point3D(0.44, 0.90),
        PoseLandmark.RIGHT_ANKLE: Point3D(0.56, 0.90),
        PoseLandmark.LEFT_WRIST: Point3D(0.40, 0.55),
        PoseLandmark.RIGHT_WRIST: Point3D(0.60, 0.55),
    })

    eval_good = engine.evaluate_posture(standing_good, measurement_type="Weight")
    assert eval_good["status"] == "CORRECT"
    assert eval_good["score"] == 100.0
    assert len(eval_good["errors"]) == 0

    # Arms flared out / resting on rails
    leaning = create_mock_landmarks({
        PoseLandmark.LEFT_SHOULDER: Point3D(0.42, 0.25),
        PoseLandmark.RIGHT_SHOULDER: Point3D(0.58, 0.25),
        PoseLandmark.LEFT_WRIST: Point3D(0.15, 0.35),  # High wide arm
    })
    eval_leaning = engine.evaluate_posture(leaning, measurement_type="Weight")
    assert eval_leaning["status"] == "INCORRECT"
    assert any(e["ruleId"] == "WT_ARMS_AT_SIDES" for e in eval_leaning["errors"])


def test_ecg_rules():
    engine = PostureRuleEngine()
    seated_ecg = create_mock_landmarks()
    res = engine.evaluate_posture(seated_ecg, measurement_type="ECG")
    assert res["status"] == "CORRECT"
    assert res["score"] == 100.0


def test_rule_engine_empty_landmarks():
    engine = PostureRuleEngine()
    res = engine.evaluate_posture(None, measurement_type="BP")
    assert res["status"] == "NO_PERSON_DETECTED"
    assert res["score"] == 0.0
