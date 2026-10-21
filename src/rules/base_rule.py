"""
Base Posture Rule and Validation Data Structures
Smart Body Posture Recognition & Guidance System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from src.pose.landmarks import Point3D


class ErrorSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class PostureError:
    rule_id: str
    name: str
    severity: ErrorSeverity
    visual_message: str
    metric_name: str
    metric_value: float
    threshold_value: float
    highlight_joints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ruleId": self.rule_id,
            "name": self.name,
            "severity": self.severity.value if isinstance(self.severity, ErrorSeverity) else str(self.severity),
            "visualMessage": self.visual_message,
            "metricName": self.metric_name,
            "metricValue": round(self.metric_value, 2),
            "thresholdValue": round(self.threshold_value, 2),
            "highlightJoints": self.highlight_joints,
        }


@dataclass
class RuleEvaluationResult:
    passed: bool
    error: Optional[PostureError] = None
    metric_name: str = ""
    metric_value: float = 0.0


class BasePostureRule(ABC):
    """Abstract base class for all individual posture validation rules."""

    def __init__(self, rule_id: str, name: str, config: Optional[Dict[str, Any]] = None):
        self.rule_id = rule_id
        self.name = name
        self.config = config or {}

    @abstractmethod
    def evaluate(self, landmarks: List[Point3D]) -> RuleEvaluationResult:
        """Evaluates landmarks and returns a RuleEvaluationResult."""
        pass
