"""
Unit Tests for State Machine, Hold Timer, and Feedback Controller
Smart Body Posture Recognition & Guidance System
"""

import time
import pytest
from src.controller.hold_timer import HoldTimer
from src.controller.state_machine import PostureStateMachine, PostureState
from src.controller.feedback_controller import FeedbackController


def test_hold_timer_success():
    timer = HoldTimer(required_duration=0.2)  # fast 200ms for unit testing

    # Frame 1: correct posture starts
    elapsed, progress, triggered = timer.update(is_correct=True)
    assert not triggered
    assert progress < 1.0

    # Wait 250ms
    time.sleep(0.25)

    # Frame 2: correct posture maintained
    elapsed, progress, triggered = timer.update(is_correct=True)
    assert triggered is True
    assert progress == 1.0


def test_hold_timer_interruption():
    timer = HoldTimer(required_duration=0.5)

    # Start hold
    timer.update(is_correct=True)
    time.sleep(0.1)

    # Interrupted by slouch
    elapsed, progress, triggered = timer.update(is_correct=False)
    assert triggered is False
    assert elapsed == 0.0
    assert progress == 0.0
    assert timer.hold_start_time is None


def test_posture_state_machine_flow():
    sm = PostureStateMachine(hold_duration=0.2)
    assert sm.state == PostureState.NOT_DETECTED

    # 1. No person detected
    res = sm.update(person_detected=False, errors=[])
    assert res["state"] == PostureState.NOT_DETECTED.value

    # 2. Person enters with errors
    errors = [{"ruleId": "BP_NO_SLOUCH", "visualMessage": "Sit straight"}]
    res = sm.update(person_detected=True, errors=errors)
    assert res["state"] == PostureState.INCORRECT.value
    assert not res["isTriggered"]

    # 3. Person corrects posture
    res = sm.update(person_detected=True, errors=[])
    assert res["state"] == PostureState.CORRECT.value
    assert not res["isTriggered"]

    # 4. Hold completes
    time.sleep(0.25)
    res = sm.update(person_detected=True, errors=[])
    assert res["state"] == PostureState.TRIGGERED.value
    assert res["isTriggered"] is True


def test_feedback_controller_visual_feedback():
    fc = FeedbackController()
    errors = [{"ruleId": "BP_NO_SLOUCH", "visualMessage": "Sit straight", "highlightJoints": ["LEFT_SHOULDER"]}]

    fb = fc.process_errors(errors, person_present=True)
    assert fb["visualMessage"] == "Sit straight"
    assert fb["highlightJoints"] == ["LEFT_SHOULDER"]
    assert fb["activeErrors"] == errors
    assert "audioPrompt" not in fb
    assert "shouldSpeak" not in fb
