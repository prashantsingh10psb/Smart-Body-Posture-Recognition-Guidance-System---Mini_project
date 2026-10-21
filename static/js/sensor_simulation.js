/**
 * Health Kiosk Sensor Hardware Simulation & Animation
 * Smart Body Posture Recognition & Guidance System
 */

class SensorSimulationService {
  constructor(containerId, ecgCanvasId) {
    this.container = document.getElementById(containerId);
    this.ecgCanvas = document.getElementById(ecgCanvasId);
    this.ecgCtx = this.ecgCanvas ? this.ecgCanvas.getContext("2d") : null;
    this.ecgAnimFrame = null;
    this.ecgOffset = 0;
  }

  showIdle(measurementType) {
    this.stopEcgAnimation();
    if (this.ecgCanvas) this.ecgCanvas.style.display = "none";

    let label = "Blood Pressure Cuff";
    let icon = "🩺";
    if (measurementType === "Weight") {
      label = "Digital Platform Scale";
      icon = "⚖️";
    } else if (measurementType === "ECG") {
      label = "ECG Contact Electrode Pads";
      icon = "❤️";
    }

    this.container.innerHTML = `
      <div style="font-size: 2rem; margin-bottom: 8px;">${icon}</div>
      <div style="font-weight: 700; color: #fff; margin-bottom: 4px;">${label}</div>
      <div class="sensor-idle-text">Sensor standby. Awaiting verified posture hold...</div>
    `;
  }

  simulateMeasurement(measurementType, resultData, onComplete) {
    if (measurementType === "ECG") {
      this.simulateEcg(resultData, onComplete);
    } else if (measurementType === "Weight") {
      this.simulateWeight(resultData, onComplete);
    } else {
      this.simulateBP(resultData, onComplete);
    }
  }

  simulateBP(resultData, onComplete) {
    this.stopEcgAnimation();
    if (this.ecgCanvas) this.ecgCanvas.style.display = "none";

    this.container.innerHTML = `
      <div class="sensor-measuring">
        <div class="sensor-spinner"></div>
        <div style="font-weight: 700; color: #38bdf8;">Inflating Blood Pressure Cuff...</div>
        <div id="bp-cuff-pressure" style="font-size: 1.6rem; font-weight: 800; color: #fff;">0 <small style="font-size: 0.8rem; color: #94a3b8;">mmHg</small></div>
        <div style="font-size: 0.78rem; color: #cbd5e1;">Please remain completely still</div>
      </div>
    `;

    const pressureEl = document.getElementById("bp-cuff-pressure");
    let p = 0;
    const interval = setInterval(() => {
      p += 14;
      if (pressureEl) pressureEl.innerHTML = `${Math.min(160, p)} <small style="font-size: 0.8rem; color: #94a3b8;">mmHg</small>`;
      if (p >= 160) {
        clearInterval(interval);
        setTimeout(() => {
          this.renderBPResult(resultData);
          if (onComplete) onComplete();
        }, 1200);
      }
    }, 120);
  }

  renderBPResult(data) {
    const meas = data || { systolic: 120, diastolic: 78, pulseBpm: 72 };
    this.container.innerHTML = `
      <div style="width: 100%;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-weight: 700; color: #10b981; font-size: 0.85rem;">✓ BP Measurement Complete</span>
          <span class="brand-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">Posture Validated</span>
        </div>
        <div class="vital-result-grid">
          <div class="vital-metric-box">
            <div class="vital-metric-label">Blood Pressure</div>
            <div class="vital-metric-value">${meas.systolic}/${meas.diastolic}</div>
            <div class="vital-metric-unit">mmHg (Normal)</div>
          </div>
          <div class="vital-metric-box">
            <div class="vital-metric-label">Pulse Rate</div>
            <div class="vital-metric-value">${meas.pulseBpm}</div>
            <div class="vital-metric-unit">BPM</div>
          </div>
        </div>
        <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 8px; text-align: left;">
          Zero posture elevation detected. True clinical reading captured.
        </div>
      </div>
    `;
  }

  simulateWeight(resultData, onComplete) {
    this.stopEcgAnimation();
    if (this.ecgCanvas) this.ecgCanvas.style.display = "none";

    this.container.innerHTML = `
      <div class="sensor-measuring">
        <div class="sensor-spinner"></div>
        <div style="font-weight: 700; color: #38bdf8;">Stabilizing Digital Load Cells...</div>
        <div id="weight-live-display" style="font-size: 1.6rem; font-weight: 800; color: #fff;">--.- <small style="font-size: 0.8rem; color: #94a3b8;">kg</small></div>
      </div>
    `;

    const weightEl = document.getElementById("weight-live-display");
    let count = 0;
    const interval = setInterval(() => {
      count++;
      const randomW = (60.0 + Math.random() * 15.0).toFixed(1);
      if (weightEl) weightEl.innerHTML = `${randomW} <small style="font-size: 0.8rem; color: #94a3b8;">kg</small>`;
      if (count > 8) {
        clearInterval(interval);
        setTimeout(() => {
          this.renderWeightResult(resultData);
          if (onComplete) onComplete();
        }, 800);
      }
    }, 120);
  }

  renderWeightResult(data) {
    const meas = data || { weightKg: 68.4, bmi: 22.8, bodyFatPercentage: 18.2 };
    this.container.innerHTML = `
      <div style="width: 100%;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-weight: 700; color: #10b981; font-size: 0.85rem;">✓ Weight Acquired</span>
          <span class="brand-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">Balanced Weight</span>
        </div>
        <div class="vital-result-grid">
          <div class="vital-metric-box">
            <div class="vital-metric-label">Body Weight</div>
            <div class="vital-metric-value">${meas.weightKg}</div>
            <div class="vital-metric-unit">kg</div>
          </div>
          <div class="vital-metric-box">
            <div class="vital-metric-label">BMI & Body Fat</div>
            <div class="vital-metric-value">${meas.bmi}</div>
            <div class="vital-metric-unit">kg/m² (Normal)</div>
          </div>
        </div>
      </div>
    `;
  }

  simulateEcg(resultData, onComplete) {
    if (this.ecgCanvas) {
      this.ecgCanvas.style.display = "block";
    }

    this.container.innerHTML = `
      <div style="width: 100%;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
          <span style="font-weight: 700; color: #38bdf8; font-size: 0.85rem;">Capturing Lead-I ECG Strip...</span>
          <span class="brand-badge" style="background: rgba(6, 182, 212, 0.2); color: #38bdf8;">Artifact-Free</span>
        </div>
        <div style="font-size: 0.72rem; color: #94a3b8; text-align: left; margin-bottom: 6px;">Sampling rate: 500 Hz | Low muscle tremor</div>
      </div>
    `;

    this.startEcgAnimation();
    setTimeout(() => {
      this.renderEcgResult(resultData);
      if (onComplete) onComplete();
    }, 3500);
  }

  startEcgAnimation() {
    this.stopEcgAnimation();
    if (!this.ecgCtx || !this.ecgCanvas) return;

    const canvas = this.ecgCanvas;
    const ctx = this.ecgCtx;
    canvas.width = canvas.clientWidth || 300;
    canvas.height = 70;

    let x = 0;
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const drawTrace = () => {
      ctx.fillStyle = "rgba(0, 0, 0, 0.08)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = "#10b981";
      ctx.lineWidth = 2;
      ctx.beginPath();

      const centerY = canvas.height / 2;
      const t = (x % 120);

      let y = centerY;
      if (t > 40 && t < 48) {
        y -= 6; // P wave
      } else if (t >= 48 && t < 52) {
        y += 4; // Q wave
      } else if (t >= 52 && t < 58) {
        y -= 26; // R spike
      } else if (t >= 58 && t < 62) {
        y += 10; // S wave
      } else if (t >= 75 && t < 90) {
        y -= 8; // T wave
      }

      ctx.moveTo(x % canvas.width, y);
      x += 3;
      ctx.lineTo(x % canvas.width, y);
      ctx.stroke();

      this.ecgAnimFrame = requestAnimationFrame(drawTrace);
    };

    drawTrace();
  }

  stopEcgAnimation() {
    if (this.ecgAnimFrame) {
      cancelAnimationFrame(this.ecgAnimFrame);
      this.ecgAnimFrame = null;
    }
  }

  renderEcgResult(data) {
    const meas = data || { heartRateBpm: 72, rhythm: "Normal Sinus Rhythm", qtIntervalMs: 395 };
    this.container.innerHTML = `
      <div style="width: 100%;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <span style="font-weight: 700; color: #10b981; font-size: 0.85rem;">✓ ECG Rhythm Analyzed</span>
          <span class="brand-badge" style="background: rgba(16, 185, 129, 0.2); color: #34d399;">Clear Trace</span>
        </div>
        <div class="vital-result-grid">
          <div class="vital-metric-box">
            <div class="vital-metric-label">Heart Rate</div>
            <div class="vital-metric-value">${meas.heartRateBpm}</div>
            <div class="vital-metric-unit">BPM (Resting)</div>
          </div>
          <div class="vital-metric-box">
            <div class="vital-metric-label">Cardiac Rhythm</div>
            <div class="vital-metric-value" style="font-size: 1rem; color: #34d399;">${meas.rhythm}</div>
            <div class="vital-metric-unit">QT: ${meas.qtIntervalMs}ms</div>
          </div>
        </div>
      </div>
    `;
  }
}

window.SensorSimulationService = SensorSimulationService;
