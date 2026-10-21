"""
Posture State Machine
Smart Body Posture Recognition & Guidance System

States:
  NOT_DETECTED -> INCORRECT -> CORRECTING -> CORRECT -> TRIGGERED
"""

from enum import Enum
import time
from typing import Dict, Any, Optional, List
from src.controller.hold_timer import HoldTimer
from src.rules.base_rule import PostureError


class PostureState(str, Enum):
    NOT_DETECTED = "NOT_DETECTED"
    INCORRECT = "INCORRECT"
    CORRECTING = "CORRECTING"
    CORRECT = "CORRECT"
    TRIGGERED = "TRIGGERED"


class PostureStateMachine:
    """Manages posture lifecycle states, hold countdown, and transitions."""

    def __init__(self, hold_duration: float = 2.5):
        self.state: PostureState = PostureState.NOT_DETECTED
        self.hold_timer = HoldTimer(required_duration=hold_duration)
        self.previous_error_count: int = 0
        self.state_enter_time: float = time.time()
        self.transition_history: List[Dict[str, Any]] = []

    def set_hold_duration(self, duration: float) -> None:
        self.hold_timer.set_duration(duration)

    def transition_to(self, new_state: PostureState, reason: str = "") -> None:
        """Transitions state if different, recording transition history."""
        if new_state != self.state:
            now = time.time()
            self.transition_history.append({
                "from": self.state.value,
                "to": new_state.value,
                "timestamp": now,
                "reason": reason,
            })
            # Keep history bounded
            if len(self.transition_history) > 50:
                self.transition_history = self.transition_history[-50:]
            self.state = new_state
            self.state_enter_time = now

    def update(
        self,
        person_detected: bool,
        errors: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Updates the state machine based on detection and active errors.
        Returns a dict describing the current state and trigger condition.
        """
        if not person_detected:
            self.hold_timer.reset()
            self.previous_error_count = 0
            self.transition_to(PostureState.NOT_DETECTED, "No person detected in frame")
            return {
                "state": self.state.value,
                "holdElapsed": 0.0,
                "holdProgress": 0.0,
                "isTriggered": False,
                "statusMessage": "Awaiting user in front of kiosk camera...",
            }

        error_count = len(errors)
        is_correct = (error_count == 0)

        # Update hold timer
        hold_elapsed, hold_progress, just_triggered = self.hold_timer.update(is_correct)

        if just_triggered:
            self.transition_to(PostureState.TRIGGERED, f"Posture held for {self.hold_timer.required_duration}s")
            return {
                "state": self.state.value,
                "holdElapsed": hold_elapsed,
                "holdProgress": 1.0,
                "isTriggered": True,
                "statusMessage": "Posture verified! Starting vital signs measurement...",
            }

        if self.state == PostureState.TRIGGERED:
            # Remain in triggered until explicitly reset or user leaves
            return {
                "state": self.state.value,
                "holdElapsed": self.hold_timer.required_duration,
                "holdProgress": 1.0,
                "isTriggered": False,
                "statusMessage": "Measurement in progress...",
            }

        if is_correct:
            self.transition_to(PostureState.CORRECT, "All posture rules met")
            remaining = max(0.0, self.hold_timer.required_duration - hold_elapsed)
            return {
                "state": self.state.value,
                "holdElapsed": round(hold_elapsed, 2),
                "holdProgress": round(hold_progress, 3),
                "isTriggered": False,
                "statusMessage": f"Hold still for {remaining:.1f}s to start measurement...",
            }
        else:
            # Person present with errors
            if error_count < self.previous_error_count:
                self.transition_to(PostureState.CORRECTING, "Errors decreasing")
            else:
                self.transition_to(PostureState.INCORRECT, "Posture errors present")

            self.previous_error_count = error_count
            return {
                "state": self.state.value,
                "holdElapsed": 0.0,
                "holdProgress": 0.0,
                "isTriggered": False,
                "statusMessage": f"Please correct posture: {errors[0].get('visualMessage', 'Adjust position')}",
            }

    def reset_session(self) -> None:
        """Resets the state machine for a new measurement session."""
        self.hold_timer.reset()
        self.state = PostureState.NOT_DETECTED
        self.previous_error_count = 0
        self.state_enter_time = time.time()
