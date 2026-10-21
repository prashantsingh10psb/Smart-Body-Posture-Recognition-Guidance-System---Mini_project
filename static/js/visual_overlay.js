/**
 * Visual Overlay Renderer for Posture Skeleton and Error Highlights
 * Smart Body Posture Recognition & Guidance System
 */

class VisualOverlayRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");

    // Standard MediaPipe skeleton connections
    this.connections = [
      [11, 12], // shoulders
      [11, 13], [13, 15], // left arm
      [12, 14], [14, 16], // right arm
      [11, 23], [12, 24], // torso sides
      [23, 24], // hips
      [23, 25], [25, 27], // left leg
      [24, 26], [26, 28], // right leg
    ];

    this.landmarkNames = {
      0: "NOSE",
      11: "LEFT_SHOULDER", 12: "RIGHT_SHOULDER",
      13: "LEFT_ELBOW", 14: "RIGHT_ELBOW",
      15: "LEFT_WRIST", 16: "RIGHT_WRIST",
      23: "LEFT_HIP", 24: "RIGHT_HIP",
      25: "LEFT_KNEE", 26: "RIGHT_KNEE",
      27: "LEFT_ANKLE", 28: "RIGHT_ANKLE"
    };

    // Inverted mapping for quick lookup
    this.nameToIdx = {};
    for (const [idx, name] of Object.entries(this.landmarkNames)) {
      this.nameToIdx[name] = parseInt(idx);
    }
  }

  resize(width, height) {
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  render(landmarks, options = {}) {
    this.clear();
    if (!landmarks || landmarks.length === 0) return;

    const width = this.canvas.width;
    const height = this.canvas.height;
    const ctx = this.ctx;

    const highlightJoints = new Set(options.highlightJoints || []);
    const isCorrect = options.status === "CORRECT";
    const status = options.status || "WAITING";

    // 1. Draw Skeleton Connection Lines
    ctx.lineWidth = 4;
    ctx.lineCap = "round";

    for (const [i, j] of this.connections) {
      const p1 = landmarks[i];
      const p2 = landmarks[j];
      if (!p1 || !p2 || (p1.visibility && p1.visibility < 0.3) || (p2.visibility && p2.visibility < 0.3)) {
        continue;
      }

      // Check if either end of connection is in error
      const name1 = this.landmarkNames[i];
      const name2 = this.landmarkNames[j];
      const inError = highlightJoints.has(name1) || highlightJoints.has(name2);

      ctx.beginPath();
      // Mirror x for natural kiosk feed
      const x1 = (1.0 - p1.x) * width;
      const y1 = p1.y * height;
      const x2 = (1.0 - p2.x) * width;
      const y2 = p2.y * height;

      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);

      if (inError) {
        ctx.strokeStyle = "rgba(239, 68, 68, 0.85)"; // Red warning
        ctx.shadowColor = "rgba(239, 68, 68, 0.8)";
        ctx.shadowBlur = 8;
      } else {
        ctx.strokeStyle = isCorrect ? "rgba(16, 185, 129, 0.85)" : "rgba(14, 165, 233, 0.75)"; // Green or Cyan
        ctx.shadowColor = isCorrect ? "rgba(16, 185, 129, 0.5)" : "rgba(14, 165, 233, 0.4)";
        ctx.shadowBlur = 4;
      }
      ctx.stroke();
    }
    ctx.shadowBlur = 0;

    // 2. Draw Spine Alignment Vector (Mid-shoulder to Mid-hip)
    const lSh = landmarks[11];
    const rSh = landmarks[12];
    const lHip = landmarks[23];
    const rHip = landmarks[24];

    if (lSh && rSh && lHip && rHip) {
      const midShX = (1.0 - (lSh.x + rSh.x) / 2.0) * width;
      const midShY = ((lSh.y + rSh.y) / 2.0) * height;
      const midHipX = (1.0 - (lHip.x + rHip.x) / 2.0) * width;
      const midHipY = ((lHip.y + rHip.y) / 2.0) * height;

      ctx.setLineDash([6, 6]);
      ctx.lineWidth = 3;
      ctx.strokeStyle = isCorrect ? "rgba(52, 211, 153, 0.9)" : "rgba(245, 158, 11, 0.9)";
      ctx.beginPath();
      ctx.moveTo(midHipX, midHipY);
      ctx.lineTo(midShX, midShY);
      ctx.stroke();
      ctx.setLineDash([]); // Reset line dash
    }

    // 3. Draw Landmark Joints
    for (let idx = 0; idx < landmarks.length; idx++) {
      const pt = landmarks[idx];
      if (!pt || (pt.visibility && pt.visibility < 0.3)) continue;

      const jointName = this.landmarkNames[idx];
      if (!jointName && idx !== 0) continue; // Only key joints

      const x = (1.0 - pt.x) * width;
      const y = pt.y * height;
      const isHighlighted = highlightJoints.has(jointName);

      ctx.beginPath();
      if (isHighlighted) {
        // Pulsating error joint
        ctx.arc(x, y, 9, 0, 2 * Math.PI);
        ctx.fillStyle = "#ef4444";
        ctx.shadowColor = "#ef4444";
        ctx.shadowBlur = 12;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(x, y, 14, 0, 2 * Math.PI);
        ctx.strokeStyle = "rgba(239, 68, 68, 0.5)";
        ctx.lineWidth = 2;
        ctx.stroke();
      } else {
        ctx.arc(x, y, 6, 0, 2 * Math.PI);
        ctx.fillStyle = isCorrect ? "#10b981" : "#38bdf8";
        ctx.shadowColor = isCorrect ? "#10b981" : "#38bdf8";
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();
      }
      ctx.shadowBlur = 0;
    }

    // 4. Draw Directional Guidance Arrow if Slouched
    if (highlightJoints.has("LEFT_SHOULDER") && highlightJoints.has("LEFT_HIP")) {
      const arrowX = width * 0.15;
      const arrowY = height * 0.45;
      this.drawUpwardGuidanceArrow(ctx, arrowX, arrowY, "Sit Upright");
    }
  }

  drawUpwardGuidanceArrow(ctx, x, y, text) {
    ctx.save();
    ctx.fillStyle = "rgba(245, 158, 11, 0.9)";
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;

    // Upward arrow
    ctx.beginPath();
    ctx.moveTo(x, y - 30);
    ctx.lineTo(x - 14, y - 6);
    ctx.lineTo(x - 6, y - 6);
    ctx.lineTo(x - 6, y + 25);
    ctx.lineTo(x + 6, y + 25);
    ctx.lineTo(x + 6, y - 6);
    ctx.lineTo(x + 14, y - 6);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Text badge
    ctx.font = "bold 12px sans-serif";
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.fillText(text, x, y + 42);
    ctx.restore();
  }
}

window.VisualOverlayRenderer = VisualOverlayRenderer;
