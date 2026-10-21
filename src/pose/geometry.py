"""
Geometric Calculation Utilities for Posture Analysis
Smart Body Posture Recognition & Guidance System
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
from src.pose.landmarks import Point3D, PoseLandmark


def get_point(landmarks: Union[List[Point3D], Dict[str, Point3D], List[Dict[str, float]]], index_or_name: Union[int, str, PoseLandmark]) -> Optional[Point3D]:
    """Safely retrieves a Point3D from various landmark container formats."""
    if not landmarks:
        return None

    idx: int
    if isinstance(index_or_name, PoseLandmark):
        idx = int(index_or_name)
    elif isinstance(index_or_name, int):
        idx = index_or_name
    elif isinstance(index_or_name, str):
        try:
            idx = int(PoseLandmark[index_or_name])
        except KeyError:
            # If passed as numeric string
            try:
                idx = int(index_or_name)
            except ValueError:
                return None
    else:
        return None

    if isinstance(landmarks, list):
        if 0 <= idx < len(landmarks):
            item = landmarks[idx]
            if isinstance(item, Point3D):
                return item
            elif isinstance(item, dict):
                return Point3D.from_dict(item)
    elif isinstance(landmarks, dict):
        # Could be keyed by integer, string name, or string index
        key_candidates = [idx, str(idx), PoseLandmark(idx).name if 0 <= idx <= 32 else None]
        for key in key_candidates:
            if key is not None and key in landmarks:
                val = landmarks[key]
                if isinstance(val, Point3D):
                    return val
                elif isinstance(val, dict):
                    return Point3D.from_dict(val)

    return None


def calculate_distance(p1: Point3D, p2: Point3D) -> float:
    """Calculates Euclidean distance between two points in 2D/3D."""
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2 + (p1.z - p2.z) ** 2)


def calculate_midpoint(p1: Point3D, p2: Point3D) -> Point3D:
    """Calculates the midpoint between two landmarks."""
    return Point3D(
        x=(p1.x + p2.x) / 2.0,
        y=(p1.y + p2.y) / 2.0,
        z=(p1.z + p2.z) / 2.0,
        visibility=min(p1.visibility, p2.visibility),
    )


def calculate_angle_3points(a: Point3D, b: Point3D, c: Point3D) -> float:
    """
    Calculates the 2D planar angle at vertex point b formed by line ba and line bc.
    Returns angle in degrees [0, 180].
    """
    # Vector ba
    v1_x = a.x - b.x
    v1_y = a.y - b.y
    # Vector bc
    v2_x = c.x - b.x
    v2_y = c.y - b.y

    dot_product = v1_x * v2_x + v1_y * v2_y
    mag1 = math.sqrt(v1_x ** 2 + v1_y ** 2)
    mag2 = math.sqrt(v2_x ** 2 + v2_y ** 2)

    if mag1 * mag2 == 0:
        return 0.0

    cosine = dot_product / (mag1 * mag2)
    cosine = max(-1.0, min(1.0, cosine))
    return math.degrees(math.acos(cosine))


def calculate_inclination_to_vertical(top: Point3D, bottom: Point3D) -> float:
    """
    Calculates the angle (in degrees) of the line between bottom and top relative to vertical.
    In image coordinates, top has smaller y than bottom.
    Returns angle in range [0, 90] degrees. A perfectly upright posture returns ~0 degrees.
    """
    dx = top.x - bottom.x
    dy = bottom.y - top.y  # Inverted since image y goes down

    # Angle relative to vertical axis (0 is vertical, 90 is horizontal)
    angle_rad = math.atan2(abs(dx), abs(dy) if abs(dy) > 1e-6 else 1e-6)
    return math.degrees(angle_rad)


def calculate_tilt_angle(p1: Point3D, p2: Point3D) -> float:
    """
    Calculates the angle between a horizontal line and the line segment connecting p1 and p2.
    Useful for shoulder tilt or hip tilt. Perfectly level points return 0 degrees.
    """
    dx = abs(p2.x - p1.x)
    dy = abs(p2.y - p1.y)
    if dx < 1e-6:
        return 90.0
    return math.degrees(math.atan(dy / dx))


def calculate_torso_dimensions(landmarks: Any) -> Tuple[float, Optional[Point3D], Optional[Point3D]]:
    """
    Computes torso height and midpoints for shoulders and hips.
    Returns (torso_height, mid_shoulder, mid_hip).
    """
    l_sh = get_point(landmarks, PoseLandmark.LEFT_SHOULDER)
    r_sh = get_point(landmarks, PoseLandmark.RIGHT_SHOULDER)
    l_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
    r_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)

    if not (l_sh and r_sh and l_hip and r_hip):
        return 0.0, None, None

    mid_sh = calculate_midpoint(l_sh, r_sh)
    mid_hip = calculate_midpoint(l_hip, r_hip)
    torso_height = calculate_distance(mid_sh, mid_hip)
    return torso_height, mid_sh, mid_hip


def check_legs_crossed(landmarks: Any) -> Tuple[bool, float]:
    """
    Determines if legs are crossed based on knee distance, ankle alignment,
    and leg crossing geometry.
    Returns (is_crossed, separation_metric).
    """
    l_knee = get_point(landmarks, PoseLandmark.LEFT_KNEE)
    r_knee = get_point(landmarks, PoseLandmark.RIGHT_KNEE)
    l_ankle = get_point(landmarks, PoseLandmark.LEFT_ANKLE)
    r_ankle = get_point(landmarks, PoseLandmark.RIGHT_ANKLE)
    l_hip = get_point(landmarks, PoseLandmark.LEFT_HIP)
    r_hip = get_point(landmarks, PoseLandmark.RIGHT_HIP)

    if not (l_knee and r_knee):
        return False, 1.0

    # Hip width as reference scale
    hip_width = calculate_distance(l_hip, r_hip) if (l_hip and r_hip) else 0.2
    if hip_width < 0.05:
        hip_width = 0.2

    # Horizontal distance between knees normalized by hip width
    knee_dist_x = abs(l_knee.x - r_knee.x)
    normalized_knee_dist = knee_dist_x / hip_width

    # Check ankle crossing if ankles visible
    ankle_crossed = False
    if l_ankle and r_ankle:
        # If left and right ankles have swapped sides relative to hips
        # Or ankle-knee lines cross
        if (l_knee.x < r_knee.x and l_ankle.x > r_ankle.x) or (l_knee.x > r_knee.x and l_ankle.x < r_ankle.x):
            ankle_crossed = True

    # If knees are tightly squeezed together or overlapping (< 30% hip width) or ankles crossed
    is_crossed = (normalized_knee_dist < 0.28) or ankle_crossed
    return is_crossed, normalized_knee_dist


def check_arm_heart_level(landmarks: Any) -> Tuple[bool, float, str]:
    """
    Evaluates whether at least one active arm (wrist/elbow) is rested at heart level.
    For blood pressure measurement, BP cuff arm should be resting supported at chest/heart level.
    Returns (is_aligned, offset_ratio, active_arm).
    """
    torso_height, mid_sh, mid_hip = calculate_torso_dimensions(landmarks)
    if torso_height < 0.05 or not mid_sh or not mid_hip:
        return True, 0.0, "UNKNOWN"

    # Estimated heart level: ~25% down from mid-shoulder to mid-hip
    heart_y = mid_sh.y + 0.25 * (mid_hip.y - mid_sh.y)

    l_wrist = get_point(landmarks, PoseLandmark.LEFT_WRIST)
    r_wrist = get_point(landmarks, PoseLandmark.RIGHT_WRIST)
    l_elbow = get_point(landmarks, PoseLandmark.LEFT_ELBOW)
    r_elbow = get_point(landmarks, PoseLandmark.RIGHT_ELBOW)

    offsets = []
    # Left arm
    if l_wrist and l_elbow:
        l_arm_y = (l_wrist.y + l_elbow.y) / 2.0
        l_offset = abs(l_arm_y - heart_y) / torso_height
        offsets.append(("LEFT", l_offset))

    # Right arm
    if r_wrist and r_elbow:
        r_arm_y = (r_wrist.y + r_elbow.y) / 2.0
        r_offset = abs(r_arm_y - heart_y) / torso_height
        offsets.append(("RIGHT", r_offset))

    if not offsets:
        return True, 0.0, "NONE"

    # Pick the arm closest to heart level as the candidate measuring arm
    offsets.sort(key=lambda item: item[1])
    active_arm, min_offset = offsets[0]

    # Offset threshold: within 22% of torso height
    is_aligned = min_offset <= 0.22
    return is_aligned, min_offset, active_arm
