"""
Analytics and Anonymized Session Logging API Routes
Smart Body Posture Recognition & Guidance System
"""

from flask import Blueprint, request, jsonify
from src.database.db import DatabaseManager

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")
db = DatabaseManager()


@analytics_bp.route("/log", methods=["POST"])
def log_analytics():
    """
    Endpoint: POST /api/analytics/log (Section 10.2)
    Accepts:
      {
        "sessionId": str,
        "errorTypes": [ str, ... ],
        "measurementType": Optional[str],
        "sessionDurationMs": Optional[int],
        "triggered": Optional[bool]
      }
    Returns:
      201 { "logId": int, "status": "logged" }
    """
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get("sessionId")
    if not session_id:
        # Create a session if not provided
        session_id = db.create_session(data.get("measurementType", "BP"))

    measurement_type = data.get("measurementType", "BP")
    duration_ms = int(data.get("sessionDurationMs", 0))
    error_types = data.get("errorTypes", [])
    triggered = bool(data.get("triggered", True))

    log_id = db.log_analytics_summary(
        session_id=session_id,
        measurement_type=measurement_type,
        duration_ms=duration_ms,
        error_types=error_types,
        triggered=triggered,
    )

    # Log individual errors to posture_events
    for err in error_types:
        db.log_posture_event(session_id, str(err))

    return jsonify({"logId": log_id, "status": "logged"}), 201


@analytics_bp.route("/session/start", methods=["POST"])
def start_session():
    """Starts a new anonymized kiosk user session."""
    data = request.get_json(force=True, silent=True) or {}
    measurement_type = data.get("measurementType", "BP")
    session_id = db.create_session(measurement_type)
    return jsonify({"sessionId": session_id, "measurementType": measurement_type}), 201


@analytics_bp.route("/session/end", methods=["POST"])
def end_session():
    """Concludes session and returns duration statistics."""
    data = request.get_json(force=True, silent=True) or {}
    session_id = data.get("sessionId")
    success = bool(data.get("success", True))
    if not session_id:
        return jsonify({"error": "sessionId required"}), 400

    result = db.complete_session(session_id, success=success)
    if not result:
        return jsonify({"error": "Session not found"}), 404

    return jsonify(result), 200


@analytics_bp.route("/kpis", methods=["GET"])
def get_kpis():
    """Returns aggregated KPI summary matching Section 8 & 13."""
    kpis = db.get_analytics_kpis()
    return jsonify(kpis), 200


@analytics_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """Returns recent session logs for the admin dashboard."""
    limit = int(request.args.get("limit", 20))
    sessions = db.get_recent_sessions(limit=limit)
    return jsonify({"sessions": sessions}), 200
