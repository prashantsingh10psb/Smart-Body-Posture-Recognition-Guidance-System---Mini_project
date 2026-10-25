"""
Flask Application Factory and Server Entry Point
Smart Body Posture Recognition & Guidance System
"""



import time
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

from src.api.routes_posture import posture_bp
from src.api.routes_analytics import analytics_bp
from config.settings import STATIC_DIR, DEBUG, LATENCY_SLA_MS

SERVER_START_TIME = time.time()


def create_app() -> Flask:
    """Creates and configures the Flask application."""
    app = Flask(
        __name__,
        static_folder=str(STATIC_DIR),
        static_url_path="/static",
    )

    # Enable CORS for kiosk frontend / external API access
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register API blueprints
    app.register_blueprint(posture_bp)
    app.register_blueprint(analytics_bp)

    @app.route("/")
    def index():
        """Serves the primary Kiosk touchscreen user interface."""
        return send_from_directory(str(STATIC_DIR), "index.html")

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """
        Healthcheck and latency monitoring endpoint as per Section 13 (NFRs).
        Verifies system availability (target: >= 99.0%) and latency SLA (<= 300 ms).
        """
        uptime_sec = round(time.time() - SERVER_START_TIME, 1)
        return jsonify({
            "status": "HEALTHY",
            "service": "Smart Body Posture Recognition & Guidance System",
            "version": "1.0.0",
            "uptimeSeconds": uptime_sec,
            "targetFPS": 20,
            "latencySlaMs": LATENCY_SLA_MS,
            "nfrCompliance": {
                "availability": ">= 99.0%",
                "p95Latency": "<= 300 ms",
                "accuracy": ">= 95%",
                "autoTriggerReliability": ">= 98%",
            },
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found", "status": 404}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error", "details": str(e), "status": 500}), 500

    return app


if __name__ == "__main__":
    from config.settings import HOST, PORT
    application = create_app()
    print(f"============================================================")
    print(f" Smart Body Posture Recognition & Guidance System v1.0.0")
    print(f" GLA University - B.Tech CSE Mini-Project (OG-Coders T-89)")
    print(f" Running at: http://{HOST}:{PORT}")
    print(f"============================================================")
    application.run(host=HOST, port=PORT, debug=DEBUG)
