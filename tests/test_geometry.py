"""
Unit Tests for Posture Geometry Calculations
Smart Body Posture Recognition & Guidance System
"""

import pytest
import math
from src.pose.landmarks import Point3D, PoseLandmark
from src.pose.geometry import (
    calculate_distance,
    calculate_midpoint,
    calculate_angle_3points,
    calculate_inclination_to_vertical,
    calculate_tilt_angle,
    check_legs_crossed,
    check_arm_heart_level,
    calculate_torso_dimensions,
)


def test_calculate_distance():
    p1 = Point3D(0.0, 0.0, 0.0)
    p2 = Point3D(3.0, 4.0, 0.0)
    assert math.isclose(calculate_distance(p1, p2), 5.0, abs_tol=1e-5)


def test_calculate_midpoint():
    p1 = Point3D(2.0, 4.0, 0.0)
    p2 = Point3D(6.0, 8.0, 0.0)
    mid = calculate_midpoint(p1, p2)
    assert mid.x == 4.0
    assert mid.y == 6.0


def test_calculate_angle_3points_right_angle():
    a = Point3D(0.0, 1.0)
    b = Point3D(0.0, 0.0)  # vertex
    c = Point3D(1.0, 0.0)
    angle = calculate_angle_3points(a, b, c)
    assert math.isclose(angle, 90.0, abs_tol=1e-3)


def test_calculate_angle_3points_straight_line():
    a = Point3D(0.0, -1.0)
    b = Point3D(0.0, 0.0)  # vertex
    c = Point3D(0.0, 1.0)
    angle = calculate_angle_3points(a, b, c)
    assert math.isclose(angle, 180.0, abs_tol=1e-3)


def test_calculate_inclination_to_vertical():
    # Perfectly upright (top above bottom)
    top = Point3D(0.5, 0.2)
    bottom = Point3D(0.5, 0.8)
    angle = calculate_inclination_to_vertical(top, bottom)
    assert math.isclose(angle, 0.0, abs_tol=1e-3)

    # 45 degrees slant
    top_45 = Point3D(0.8, 0.5)
    bottom_45 = Point3D(0.5, 0.8)
    angle_45 = calculate_inclination_to_vertical(top_45, bottom_45)
    assert math.isclose(angle_45, 45.0, abs_tol=1e-3)


def test_check_legs_crossed():
    # Uncrossed legs (proper separation between knees)
    uncrossed_landmarks = {
        PoseLandmark.LEFT_HIP: Point3D(0.4, 0.5),
        PoseLandmark.RIGHT_HIP: Point3D(0.6, 0.5),
        PoseLandmark.LEFT_KNEE: Point3D(0.38, 0.75),
        PoseLandmark.RIGHT_KNEE: Point3D(0.62, 0.75),
        PoseLandmark.LEFT_ANKLE: Point3D(0.38, 0.95),
        PoseLandmark.RIGHT_ANKLE: Point3D(0.62, 0.95),
    }
    is_crossed, metric = check_legs_crossed(uncrossed_landmarks)
    assert not is_crossed
    assert metric > 0.5

    # Crossed legs (knees overlapping horizontally)
    crossed_landmarks = {
        PoseLandmark.LEFT_HIP: Point3D(0.4, 0.5),
        PoseLandmark.RIGHT_HIP: Point3D(0.6, 0.5),
        PoseLandmark.LEFT_KNEE: Point3D(0.51, 0.75),
        PoseLandmark.RIGHT_KNEE: Point3D(0.49, 0.75),
        PoseLandmark.LEFT_ANKLE: Point3D(0.55, 0.95),
        PoseLandmark.RIGHT_ANKLE: Point3D(0.45, 0.95),
    }
    is_crossed, metric = check_legs_crossed(crossed_landmarks)
    assert is_crossed
