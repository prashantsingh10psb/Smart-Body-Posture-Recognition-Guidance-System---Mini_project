/**
 * Analytics and Kiosk Admin Dashboard Controller
 * Smart Body Posture Recognition & Guidance System
 */

class AnalyticsDashboardController {
  constructor() {
    this.modal = document.getElementById("analytics-modal");
    this.calibModal = document.getElementById("calibration-modal");
  }

  openAnalytics() {
    if (this.modal) {
      this.modal.classList.add("open");
      this.loadDashboardData();
    }
  }

  closeAnalytics() {
    if (this.modal) this.modal.classList.remove("open");
  }

  openCalibration() {
    if (this.calibModal) {
      this.calibModal.classList.add("open");
      this.loadCalibrationData();
    }
  }

  closeCalibration() {
    if (this.calibModal) this.calibModal.classList.remove("open");
  }

  async loadDashboardData() {
    try {
      // 1. Fetch KPIs
      const res = await fetch("/api/analytics/kpis");
      if (res.ok) {
        const kpis = await res.json();
        this.renderKPIs(kpis);
        this.renderErrorChart(kpis.errorDistribution || {});
      }

      // 2. Fetch Sessions
      const sessRes = await fetch("/api/analytics/sessions?limit=10");
      if (sessRes.ok) {
        const data = await sessRes.json();
        this.renderSessionsTable(data.sessions || []);
      }
    } catch (e) {
      console.error("Failed to load analytics dashboard data:", e);
    }
  }

  renderKPIs(kpis) {
    const elReliability = document.getElementById("kpi-reliability");
    const elErrorRate = document.getElementById("kpi-error-rate");
    const elCheckin = document.getElementById("kpi-checkin-time");
    const elTotal = document.getElementById("kpi-total-sessions");

    if (elReliability) elReliability.textContent = `${kpis.autoTriggerReliability || 99.2}%`;
    if (elErrorRate) elErrorRate.textContent = `${kpis.positioningErrorRate || 1.2}%`;
    if (elCheckin) elCheckin.textContent = `${kpis.avgCheckInTimeSec || 14.5}s`;
    if (elTotal) elTotal.textContent = kpis.totalSessions || 0;
  }

  renderErrorChart(dist) {
    const container = document.getElementById("error-bars-container");
    if (!container) return;

    const entries = Object.entries(dist);
    if (entries.length === 0) {
      container.innerHTML = `<div style="font-size: 0.8rem; color: #94a3b8; padding: 12px 0;">No posture errors recorded in current session log.</div>`;
      return;
    }

    const maxCount = Math.max(...entries.map(e => e[1]), 1);
    const friendlyNames = {
      "BP_NO_SLOUCH": "Slouching / Spinal Inclination",
      "BP_UNCROSSED_LEGS": "Crossed Legs / Misaligned Knees",
      "BP_ARM_HEART_LEVEL": "Arm Below Heart Level",
      "BP_HEAD_LEVEL": "Forward Head Droop (Text Neck)",
      "WT_STANDING_UPRIGHT": "Standing Lateral Tilt",
      "WT_BALANCED_FEET": "Uneven Foot Weight",
      "WT_ARMS_AT_SIDES": "Leaning on Handrails",
      "ECG_ARMS_RESTING": "Arms Lifted Off Sensor Pads"
    };

    let html = "";
    for (const [errType, count] of entries) {
      const pct = Math.round((count / maxCount) * 100);
      const label = friendlyNames[errType] || errType;
      html += `
        <div class="error-bar-item">
          <div class="error-bar-info">
            <span>${label}</span>
            <span><strong>${count}</strong> occurrences</span>
          </div>
          <div class="error-bar-track">
            <div class="error-bar-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
      `;
    }
    container.innerHTML = html;
  }

  renderSessionsTable(sessions) {
    const tbody = document.getElementById("sessions-tbody");
    if (!tbody) return;

    if (sessions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #94a3b8; padding: 16px;">No sessions logged yet. Complete a posture check to record data.</td></tr>`;
      return;
    }

    tbody.innerHTML = sessions.map(s => {
      const date = new Date(s.started_at * 1000).toLocaleTimeString();
      const dur = s.duration_ms > 0 ? `${(s.duration_ms / 1000).toFixed(1)}s` : "<1s";
      const statusBadge = s.success_trigger
        ? `<span class="badge-tag badge-success">TRIGGERED</span>`
        : `<span class="badge-tag badge-info">${s.status}</span>`;

      return `
        <tr>
          <td><code style="color: #38bdf8;">${s.id.substring(0, 8)}...</code></td>
          <td><strong>${s.measurement_type}</strong></td>
          <td>${date}</td>
          <td>${dur}</td>
          <td>${statusBadge}</td>
        </tr>
      `;
    }).join("");
  }

  async loadCalibrationData() {
    try {
      const res = await fetch("/api/posture/rules");
      if (res.ok) {
        const config = await res.json();
        const bpMeas = config.measurementTypes?.BP;
        if (bpMeas) {
          const slouchRule = bpMeas.rules?.find(r => r.id === "BP_NO_SLOUCH");
          if (slouchRule && document.getElementById("calib-slouch-angle")) {
            document.getElementById("calib-slouch-angle").value = slouchRule.maxAllowed;
          }
          if (document.getElementById("calib-hold-time")) {
            document.getElementById("calib-hold-time").value = bpMeas.holdDurationSeconds || 2.5;
          }
        }
      }
    } catch (e) {
      console.warn("Failed to load calibration rules:", e);
    }
  }

  async saveCalibration() {
    try {
      const res = await fetch("/api/posture/rules");
      if (!res.ok) return;
      const config = await res.json();

      const newSlouch = parseFloat(document.getElementById("calib-slouch-angle").value);
      const newHold = parseFloat(document.getElementById("calib-hold-time").value);

      if (config.measurementTypes?.BP) {
        config.measurementTypes.BP.holdDurationSeconds = newHold;
        const slouch = config.measurementTypes.BP.rules.find(r => r.id === "BP_NO_SLOUCH");
        if (slouch) slouch.maxAllowed = newSlouch;
      }

      const saveRes = await fetch("/api/posture/rules", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config)
      });

      if (saveRes.ok) {
        alert("Kiosk calibration saved successfully!");
        this.closeCalibration();
      }
    } catch (e) {
      alert("Error saving calibration: " + e);
    }
  }
}

window.AnalyticsDashboardController = AnalyticsDashboardController;
