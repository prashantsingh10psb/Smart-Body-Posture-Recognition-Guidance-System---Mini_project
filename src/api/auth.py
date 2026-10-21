"""
Authentication Middleware for Kiosk Sensor Trigger API
Smart Body Posture Recognition & Guidance System
"""

from functools import wraps
from flask import request, jsonify
from config.settings import DEVICE_KEY


def require_device_key(f):
    """
    Decorator enforcing Device-key authentication on sensitive hardware trigger endpoints
    as specified in Section 10.2 and 14.1 (STRIDE threat mitigation).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check X-Device-Key header, query param, or Bearer auth
        auth_header = request.headers.get("X-Device-Key")
        if not auth_header:
            auth_bearer = request.headers.get("Authorization", "")
            if auth_bearer.startswith("Bearer "):
                auth_header = auth_bearer[7:].strip()
            elif auth_bearer.startswith("DeviceKey "):
                auth_header = auth_bearer[10:].strip()

        if not auth_header:
            auth_header = request.args.get("device_key")

        if not auth_header or auth_header != DEVICE_KEY:
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid X-Device-Key header required to trigger kiosk sensor hardware.",
                "strideMitigation": "Prevents spoofed sensor activation signals.",
            }), 401

        return f(*args, **kwargs)

    return decorated_function
