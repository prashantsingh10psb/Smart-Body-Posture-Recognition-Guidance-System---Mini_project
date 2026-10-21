"""Visual feedback controller for posture guidance."""

from typing import Dict, List, Any


class FeedbackController:
    """Creates immediate on-screen feedback for posture errors."""

    def __init__(self):
        self.error_start_times: Dict[str, float] = {}
        self.last_visual_message = None

    def process_errors(
        self,
        errors: List[Dict[str, Any]],
        person_present: bool = True,
    ) -> Dict[str, Any]:
        if not person_present:
            self.error_start_times.clear()
            message = "Welcome! Please sit or stand in front of the kiosk to begin."
            joints = []
            active_errors = []
        elif not errors:
            self.error_start_times.clear()
            message = "Great posture! Hold steady to start measurement."
            joints = []
            active_errors = []
        else:
            current_ids = set()
            joints = []
            for err in errors:
                rule_id = err.get("ruleId", "UNKNOWN")
                current_ids.add(rule_id)
                for joint in err.get("highlightJoints", []):
                    if joint not in joints:
                        joints.append(joint)
            self.error_start_times = {
                key: value for key, value in self.error_start_times.items()
                if key in current_ids
            }
            message = errors[0].get("visualMessage", "Please adjust your posture")
            active_errors = errors

        self.last_visual_message = message
        return {
            "visualMessage": message,
            "highlightJoints": joints,
            "activeErrors": active_errors,
        }

    def reset(self) -> None:
        """Resets visual feedback state."""
        self.error_start_times.clear()
        self.last_visual_message = None
