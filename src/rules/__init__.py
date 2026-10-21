"""Posture rules package initialization."""
from src.rules.base_rule import BasePostureRule, PostureError, RuleEvaluationResult, ErrorSeverity
from src.rules.bp_rules import BPSlouchRule, BPCrossedLegsRule, BPArmAlignmentRule, BPHeadLevelRule
from src.rules.weight_rules import WeightStandingUprightRule, WeightBalancedFeetRule, WeightArmsAtSidesRule
from src.rules.ecg_rules import ECGSeatedUprightRule, ECGUncrossedLegsRule, ECGArmsRestingRule
from src.rules.engine import PostureRuleEngine

__all__ = [
    "BasePostureRule",
    "PostureError",
    "RuleEvaluationResult",
    "ErrorSeverity",
    "BPSlouchRule",
    "BPCrossedLegsRule",
    "BPArmAlignmentRule",
    "BPHeadLevelRule",
    "WeightStandingUprightRule",
    "WeightBalancedFeetRule",
    "WeightArmsAtSidesRule",
    "ECGSeatedUprightRule",
    "ECGUncrossedLegsRule",
    "ECGArmsRestingRule",
    "PostureRuleEngine",
]
