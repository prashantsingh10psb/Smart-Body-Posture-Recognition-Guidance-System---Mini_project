/**
 * Main Kiosk Application Controller
 * Smart Body Posture Recognition & Guidance System
 */

document.addEventListener("DOMContentLoaded", () => {
  const videoEl = document.getElementById("webcam-video");
  const canvasEl = document.getElementById("overlay-canvas");
  const scoreValEl = document.getElementById("score-value");
  const statusPillEl = document.getElementById("status-pill");
  const statusBannerEl = document.getElementById("hud-status-banner");
  const statusTextEl = document.getElementById("hud-status-text");
  const holdBarEl = document.getElementById("hold-progress-fill");
  const holdTextEl = document.getElementById("hold-progress-text");
  const errorsContainerEl = document.getElementById("active-errors-container");
  const primaryGuidanceEl = document.getElementById("primary-guidance-text");

  // Services
  const overlayRenderer = new VisualOverlayRenderer(canvasEl);
  const sensorService = new SensorSimulationService("sensor-stage-container", "ecg-canvas");
  const dashboard = new AnalyticsDashboardController();

  // App State
  let currentMeasurement = "BP";
  let activeSessionId = null;
  let isWebcamActive = false;
  let currentStream = null;
  let processingInterval = null;
  let isSimulatingPreset = false;
  let activePresetKey = null;
  let measurementInProgress = false;
  const encounteredErrors = new Set();
  const sessionStartTime = Date.now();

  // Resize canvas when video loads
  videoEl.addEventListener("loadedmetadata", () => {
    overlayRenderer.resize(videoEl.videoWidth || 640, videoEl.videoHeight || 480);
  });

  // 1. Session Management
  async function initSession() {
    try {
      const res = await fetch("/api/analytics/session/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ measurementType: currentMeasurement })
      });
      if (res.ok) {
        const data = await res.json();
        activeSessionId = data.sessionId;
      }
    } catch (e) {
      console.warn("Could not start session:", e);
      activeSessionId = "local-" + Date.now();
    }
    encounteredErrors.clear();
    measurementInProgress = false;
    sensorService.showIdle(currentMeasurement);
  }

  // 2. Mode Switching (BP, Weight, ECG)
  document.querySelectorAll(".mode-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".mode-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentMeasurement = tab.dataset.mode;
      document.getElementById("current-mode-title").textContent =
        currentMeasurement === "BP" ? "Blood Pressure Posture Check" :
        currentMeasurement === "Weight" ? "Weight & BMI Stance Check" :
        "ECG Resting Posture Check";

      initSession();
      resetPostureState();

      // If in preset mode, auto-switch to a fitting preset
      if (isSimulatingPreset) {
        const presetKey = currentMeasurement === "BP" ? "BP_PERFECT" :
                          currentMeasurement === "Weight" ? "WEIGHT_PERFECT" : "ECG_PERFECT";
        applyPreset(presetKey);
      }
    });
  });

  // 3. Camera Controls
  const toggleCamBtn = document.getElementById("btn-toggle-cam");
  async function startWebcam() {
    try {
      isSimulatingPreset = false;
      document.getElementById("preset-select").value = "";
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
        audio: false
      });
      currentStream = stream;
      videoEl.srcObject = stream;
      await videoEl.play();
      isWebcamActive = true;
      toggleCamBtn.textContent = "📷 Stop Camera";
      toggleCamBtn.classList.add("btn-primary");
      document.getElementById("live-indicator-badge").style.display = "flex";
      startProcessingLoop();
    } catch (err) {
      console.warn("Webcam access failed:", err);
      alert("Camera access denied or unavailable. You can use the 'Posture Presets' dropdown below to test all scenarios!");
    }
  }

  function stopWebcam() {
    if (currentStream) {
      currentStream.getTracks().forEach(t => t.stop());
      currentStream = null;
    }
    videoEl.srcObject = null;
    isWebcamActive = false;
    toggleCamBtn.textContent = "📷 Start Camera";
    toggleCamBtn.classList.remove("btn-primary");
    document.getElementById("live-indicator-badge").style.display = "none";
    if (processingInterval) {
      clearInterval(processingInterval);
      processingInterval = null;
    }
    overlayRenderer.clear();
  }

  toggleCamBtn.addEventListener("click", () => {
    if (isWebcamActive) {
      stopWebcam();
    } else {
      startWebcam();
    }
  });

  // 4. Client-to-Backend Frame Processing
  // For ultra-smooth kiosk response, capture video frame and send to /api/posture/analyze-frame
  const captureCanvas = document.createElement("canvas");
  const captureCtx = captureCanvas.getContext("2d");

  function startProcessingLoop() {
    if (processingInterval) clearInterval(processingInterval);
    processingInterval = setInterval(async () => {
      if (!isWebcamActive || measurementInProgress) return;

      captureCanvas.width = 320; // Fast scale down for low latency (<300ms SLA)
      captureCanvas.height = 240;
      captureCtx.drawImage(videoEl, 0, 0, 320, 240);

      const b64 = captureCanvas.toDataURL("image/jpeg", 0.65);

      try {
        const response = await fetch("/api/posture/analyze-frame", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            image: b64,
            measurementType: currentMeasurement,
            sessionId: activeSessionId
          })
        });

        if (response.ok) {
          const result = await response.json();
          handleAnalysisResult(result);
        }
      } catch (err) {
        console.warn("Frame analysis error:", err);
      }
    }, 150); // ~7-10 updates/sec server loop, well within kiosk bandwidth
  }

  // 5. Presets Selector (for instant demo / testing)
  const presetSelect = document.getElementById("preset-select");
  presetSelect.addEventListener("change", (e) => {
    const key = e.target.value;
    if (key) {
      stopWebcam();
      applyPreset(key);
    }
  });

  let presetInterval = null;
  function applyPreset(key) {
    const preset = SAMPLE_POSTURE_PRESETS[key];
    if (!preset) return;

    isSimulatingPreset = true;
    activePresetKey = key;
    if (presetInterval) clearInterval(presetInterval);

    // Set canvas dimensions
    overlayRenderer.resize(640, 480);

    // Call backend API with preset keypoints repeatedly to simulate live session
    presetInterval = setInterval(async () => {
      if (!isSimulatingPreset || measurementInProgress) return;

      try {
        const res = await fetch("/api/posture/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            measurementType: currentMeasurement,
            keypoints: preset.landmarks,
            sessionId: activeSessionId
          })
        });

        if (res.ok) {
          const result = await responseOrJson(res);
          result.keypoints = preset.landmarks;
          handleAnalysisResult(result);
        }
      } catch (e) {
        console.warn("Preset eval error:", e);
      }
    }, 200);
  }

  async function responseOrJson(res) {
    return await res.json();
  }

  // 6. Handle Analysis Result & Visual/Audio Update
  function handleAnalysisResult(result) {
    const status = result.status;
    const score = result.score || 0;
    const errors = result.errors || [];
    const holdProgress = result.holdProgress || 0;
    const isTriggered = result.isTriggered || false;
    const feedback = result.feedback || {};

    // Track encountered errors for session logging
    errors.forEach(err => encounteredErrors.add(err.ruleId));

    // Update Score & Status Badge
    scoreValEl.textContent = `${score}%`;
    if (status === "CORRECT") {
      scoreValEl.style.color = "var(--success)";
      statusPillEl.textContent = "CORRECT";
      statusPillEl.className = "status-pill badge-success";
      statusBannerEl.className = "hud-status-banner status-correct";
      statusTextEl.textContent = "✓ Posture Optimal — Keep Still";
    } else if (status === "INCORRECT") {
      scoreValEl.style.color = "var(--danger)";
      statusPillEl.textContent = "INCORRECT";
      statusPillEl.className = "status-pill badge-danger";
      statusBannerEl.className = "hud-status-banner status-incorrect";
      statusTextEl.textContent = `⚠ ${feedback.visualMessage || "Posture Error Detected"}`;
    } else {
      scoreValEl.style.color = "var(--text-muted)";
      statusPillEl.textContent = "STANDBY";
      statusPillEl.className = "status-pill badge-info";
      statusBannerEl.className = "hud-status-banner status-waiting";
      statusTextEl.textContent = "Position yourself in front of kiosk";
    }

    // Update Hold Progress Bar
    const pct = Math.round(holdProgress * 100);
    holdBarEl.style.width = `${pct}%`;
    if (holdProgress > 0 && holdProgress < 1) {
      holdTextEl.textContent = `Holding steady: ${pct}%`;
    } else if (holdProgress >= 1) {
      holdTextEl.textContent = `Posture Verified!`;
    } else {
      holdTextEl.textContent = `Hold posture for 2.5s to start scan`;
    }

    // Render Canvas Overlay
    overlayRenderer.render(result.keypoints, {
      highlightJoints: result.highlightJoints,
      status: status
    });

    // Render Errors List
    renderErrorsList(errors);

    // Sensor Activation Trigger (Auto-trigger after 2.5s hold)
    if (isTriggered && !measurementInProgress) {
      triggerKioskHardwareScan();
    }
  }

  function renderErrorsList(errors) {
    if (!errors || errors.length === 0) {
      errorsContainerEl.innerHTML = `
        <div class="no-errors-notice">
          <span>✓</span>
          <div>All clinical posture rules satisfied. Hold still for scan.</div>
        </div>
      `;
      primaryGuidanceEl.textContent = "Posture is aligned. Stay relaxed and still.";
      return;
    }

    errorsContainerEl.innerHTML = errors.map(err => `
      <div class="error-item ${err.severity === 'WARNING' ? 'warning' : ''}">
        <div class="error-icon">⚠</div>
        <div class="error-text">
          <div class="error-name">${err.name}</div>
          <div class="error-instruction">${err.visualMessage}</div>
        </div>
      </div>
    `).join("");

    primaryGuidanceEl.textContent = errors[0].visualMessage;
  }

  // 7. Trigger Kiosk Hardware Scan & Log Analytics
  async function triggerKioskHardwareScan() {
    measurementInProgress = true;

    statusBannerEl.className = "hud-status-banner status-triggered";
    statusTextEl.textContent = "⚡ Posture Held! Sensor Measurement in Progress...";

    try {
      // Call authenticated sensor trigger API with Device Key
      const triggerRes = await fetch("/api/posture/trigger", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Device-Key": "kiosk-device-secret-key-2026"
        },
        body: JSON.stringify({
          sessionId: activeSessionId,
          measurementType: currentMeasurement
        })
      });

      let triggerData = null;
      if (triggerRes.ok) {
        const json = await triggerRes.json();
        triggerData = json.measurement;
      }

      // Simulate sensor animation (cuff, scale, or ECG trace)
      sensorService.simulateMeasurement(currentMeasurement, triggerData, async () => {
        // Log to analytics API
        const sessionDur = Date.now() - sessionStartTime;
        await fetch("/api/analytics/log", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sessionId: activeSessionId,
            measurementType: currentMeasurement,
            sessionDurationMs: sessionDur,
            errorTypes: Array.from(encounteredErrors),
            triggered: true
          })
        });

        setTimeout(() => {
          measurementInProgress = false;
          resetPostureState();
        }, 4000);
      });

    } catch (e) {
      console.error("Sensor trigger failure:", e);
      measurementInProgress = false;
    }
  }

  async function resetPostureState() {
    try {
      await fetch("/api/posture/reset", { method: "POST" });
    } catch (e) {}
    holdBarEl.style.width = "0%";
    holdTextEl.textContent = "Hold posture for 2.5s to start scan";
  }


  // 8. Modals (Analytics & Calibration)
  document.getElementById("btn-open-analytics").addEventListener("click", () => dashboard.openAnalytics());
  document.getElementById("btn-close-analytics").addEventListener("click", () => dashboard.closeAnalytics());
  document.getElementById("btn-open-calibration").addEventListener("click", () => dashboard.openCalibration());
  document.getElementById("btn-close-calibration").addEventListener("click", () => dashboard.closeCalibration());
  document.getElementById("btn-save-calibration").addEventListener("click", () => dashboard.saveCalibration());

  // Initialize
  initSession();
  // By default, start with BP_PERFECT preset loaded so the screen looks lively immediately!
  presetSelect.value = "BP_PERFECT";
  applyPreset("BP_PERFECT");
});
