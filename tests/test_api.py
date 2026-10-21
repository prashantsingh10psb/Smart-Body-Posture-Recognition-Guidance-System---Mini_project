"""
API Integration Tests
Smart Body Posture Recognition & Guidance System
"""

import pytest
import json
from src.api.app import create_app
from config.settings import DEVICE_KEY


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "HEALTHY"
    assert "nfrCompliance" in data


def test_posture_analyze_no_person(client):
    response = client.post(
        "/api/posture/analyze",
        data=json.dumps({"measurementType": "BP", "keypoints": []}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "NO_PERSON_DETECTED"
    assert data["state"] == "NOT_DETECTED"


def test_posture_analyze_with_keypoints(client):
    # Send basic mock keypoints
    kps = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 1.0} for _ in range(33)]
    # Shoulder positions
    kps[11] = {"x": 0.40, "y": 0.30, "z": 0.0, "visibility": 1.0}
    kps[12] = {"x": 0.60, "y": 0.30, "z": 0.0, "visibility": 1.0}
    kps[23] = {"x": 0.42, "y": 0.60, "z": 0.0, "visibility": 1.0}
    kps[24] = {"x": 0.58, "y": 0.60, "z": 0.0, "visibility": 1.0}

    response = client.post(
        "/api/posture/analyze",
        data=json.dumps({"measurementType": "BP", "keypoints": kps}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert "score" in data
    assert "holdProgress" in data
    assert "feedback" in data


def test_posture_trigger_unauthorized(client):
    # Calling trigger without device key header should return 401
    response = client.post(
        "/api/posture/trigger",
        data=json.dumps({"sessionId": "test-session", "measurementType": "BP"}),
        content_type="application/json",
    )
    assert response.status_code == 401
    assert "Unauthorized" in response.get_json()["error"]


def test_posture_trigger_authorized(client):
    # Calling trigger WITH device key header should return 200
    response = client.post(
        "/api/posture/trigger",
        headers={"X-Device-Key": DEVICE_KEY},
        data=json.dumps({"sessionId": "test-session-123", "measurementType": "BP"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["triggered"] is True
    assert "measurement" in data
    assert data["measurement"]["type"] == "Blood Pressure"


def test_posture_rules_endpoint(client):
    response = client.get("/api/posture/rules")
    assert response.status_code == 200
    data = response.get_json()
    assert "measurementTypes" in data
    assert "BP" in data["measurementTypes"]
    assert "Weight" in data["measurementTypes"]
    assert "ECG" in data["measurementTypes"]


def test_analytics_log_and_kpis(client):
    # 1. Log an event
    log_payload = {
        "sessionId": "test-sess-analytics",
        "measurementType": "BP",
        "sessionDurationMs": 14200,
        "errorTypes": ["BP_NO_SLOUCH"],
        "triggered": True,
    }
    log_res = client.post(
        "/api/analytics/log",
        data=json.dumps(log_payload),
        content_type="application/json",
    )
    assert log_res.status_code == 201
    assert "logId" in log_res.get_json()

    # 2. Get KPIs
    kpi_res = client.get("/api/analytics/kpis")
    assert kpi_res.status_code == 200
    kpis = kpi_res.get_json()
    assert "autoTriggerReliability" in kpis
    assert "positioningErrorRate" in kpis
