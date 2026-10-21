"""
Hold Timer for Continuous Posture Stability Verification
Smart Body Posture Recognition & Guidance System
"""

import time
from typing import Optional, Tuple


class HoldTimer:
    """Tracks continuous correct posture duration and fires trigger when duration requirement is met."""

    def __init__(self, required_duration: float = 2.5):
        self.required_duration = required_duration
        self.hold_start_time: Optional[float] = None
        self.is_completed: bool = False
        self.last_update_time: float = time.time()

    def set_duration(self, duration: float) -> None:
        self.required_duration = max(0.5, duration)

    def update(self, is_correct: bool) -> Tuple[float, float, bool]:
        """
        Updates the timer state.
        Args:
            is_correct: True if all posture rules currently pass.
        Returns:
            (elapsed_seconds, progress_ratio_0_to_1, is_triggered_now)
        """
        now = time.time()
        self.last_update_time = now

        if not is_correct:
            # Reset timer if posture breaks
            self.hold_start_time = None
            self.is_completed = False
            return 0.0, 0.0, False

        # If already triggered for this stable posture session, stay triggered
        if self.is_completed:
            return self.required_duration, 1.0, False

        # First frame of correct posture
        if self.hold_start_time is None:
            self.hold_start_time = now
            return 0.0, 0.0, False

        elapsed = now - self.hold_start_time
        progress = min(1.0, elapsed / self.required_duration)

        if elapsed >= self.required_duration and not self.is_completed:
            self.is_completed = True
            return elapsed, 1.0, True

        return elapsed, progress, False

    def reset(self) -> None:
        """Resets the hold timer."""
        self.hold_start_time = None
        self.is_completed = False
