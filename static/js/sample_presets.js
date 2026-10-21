/**
 * Sample Posture Presets for Demonstration & Headless Testing
 * Smart Body Posture Recognition & Guidance System
 */

const SAMPLE_POSTURE_PRESETS = {
  BP_PERFECT: {
    name: "BP: Perfect Posture",
    measurementType: "BP",
    description: "Upright spine, uncrossed knees, arm resting flat at heart level.",
    expectedStatus: "CORRECT",
    landmarks: (() => {
      const lms = Array.from({ length: 33 }, () => ({ x: 0.5, y: 0.5, z: 0.0, visibility: 0.95 }));
      lms[0] = { x: 0.50, y: 0.18, z: 0.0, visibility: 0.99 }; // Nose
      lms[7] = { x: 0.46, y: 0.18, z: 0.0, visibility: 0.95 }; // L ear
      lms[8] = { x: 0.54, y: 0.18, z: 0.0, visibility: 0.95 }; // R ear
      lms[11] = { x: 0.40, y: 0.30, z: 0.0, visibility: 0.99 }; // L shoulder
      lms[12] = { x: 0.60, y: 0.30, z: 0.0, visibility: 0.99 }; // R shoulder
      lms[13] = { x: 0.32, y: 0.38, z: 0.0, visibility: 0.95 }; // L elbow
      lms[14] = { x: 0.68, y: 0.38, z: 0.0, visibility: 0.95 }; // R elbow
      lms[15] = { x: 0.42, y: 0.38, z: 0.0, visibility: 0.95 }; // L wrist (heart level)
      lms[16] = { x: 0.58, y: 0.38, z: 0.0, visibility: 0.95 }; // R wrist
      lms[23] = { x: 0.42, y: 0.60, z: 0.0, visibility: 0.99 }; // L hip
      lms[24] = { x: 0.58, y: 0.60, z: 0.0, visibility: 0.99 }; // R hip
      lms[25] = { x: 0.38, y: 0.80, z: 0.0, visibility: 0.95 }; // L knee
      lms[26] = { x: 0.62, y: 0.80, z: 0.0, visibility: 0.95 }; // R knee
      lms[27] = { x: 0.38, y: 0.95, z: 0.0, visibility: 0.90 }; // L ankle
      lms[28] = { x: 0.62, y: 0.95, z: 0.0, visibility: 0.90 }; // R ankle
      return lms;
    })()
  },

  BP_SLOUCH: {
    name: "BP: Slouching Error",
    measurementType: "BP",
    description: "Torso slouched forward, falsifying BP reading by 10-15 mmHg.",
    expectedStatus: "INCORRECT",
    landmarks: (() => {
      const lms = JSON.parse(JSON.stringify(SAMPLE_POSTURE_PRESETS?.BP_PERFECT?.landmarks || []));
      if (lms.length === 0) return [];
      // Tilt spine forward significantly
      lms[11].x = 0.62; lms[11].y = 0.36;
      lms[12].x = 0.82; lms[12].y = 0.36;
      lms[0].x = 0.72;  lms[0].y = 0.28;
      return lms;
    })()
  },

  BP_CROSSED_LEGS: {
    name: "BP: Crossed Legs Error",
    measurementType: "BP",
    description: "Knees and ankles crossed over each other.",
    expectedStatus: "INCORRECT",
    landmarks: (() => {
      const lms = JSON.parse(JSON.stringify(SAMPLE_POSTURE_PRESETS?.BP_PERFECT?.landmarks || []));
      if (lms.length === 0) return [];
      // Squeeze knees together and overlap ankles
      lms[25].x = 0.51; lms[26].x = 0.49;
      lms[27].x = 0.56; lms[28].x = 0.44;
      return lms;
    })()
  },

  BP_ARM_LOW: {
    name: "BP: Arm Below Heart",
    measurementType: "BP",
    description: "Active arm drooping below heart level near thigh.",
    expectedStatus: "INCORRECT",
    landmarks: (() => {
      const lms = JSON.parse(JSON.stringify(SAMPLE_POSTURE_PRESETS?.BP_PERFECT?.landmarks || []));
      if (lms.length === 0) return [];
      lms[13].y = 0.58; lms[15].y = 0.65; // Dropped left arm
      lms[14].y = 0.58; lms[16].y = 0.65;
      return lms;
    })()
  },

  WEIGHT_PERFECT: {
    name: "Weight: Perfect Standing",
    measurementType: "Weight",
    description: "Upright standing posture, feet aligned, arms at sides.",
    expectedStatus: "CORRECT",
    landmarks: (() => {
      const lms = Array.from({ length: 33 }, () => ({ x: 0.5, y: 0.5, z: 0.0, visibility: 0.95 }));
      lms[0] = { x: 0.50, y: 0.12, z: 0.0, visibility: 0.99 };
      lms[11] = { x: 0.42, y: 0.25, z: 0.0, visibility: 0.99 };
      lms[12] = { x: 0.58, y: 0.25, z: 0.0, visibility: 0.99 };
      lms[13] = { x: 0.38, y: 0.40, z: 0.0, visibility: 0.95 };
      lms[14] = { x: 0.62, y: 0.40, z: 0.0, visibility: 0.95 };
      lms[15] = { x: 0.38, y: 0.55, z: 0.0, visibility: 0.95 };
      lms[16] = { x: 0.62, y: 0.55, z: 0.0, visibility: 0.95 };
      lms[23] = { x: 0.44, y: 0.50, z: 0.0, visibility: 0.99 };
      lms[24] = { x: 0.56, y: 0.50, z: 0.0, visibility: 0.99 };
      lms[25] = { x: 0.44, y: 0.70, z: 0.0, visibility: 0.95 };
      lms[26] = { x: 0.56, y: 0.70, z: 0.0, visibility: 0.95 };
      lms[27] = { x: 0.44, y: 0.92, z: 0.0, visibility: 0.95 };
      lms[28] = { x: 0.56, y: 0.92, z: 0.0, visibility: 0.95 };
      return lms;
    })()
  },

  WEIGHT_LEANING: {
    name: "Weight: Leaning on Rails",
    measurementType: "Weight",
    description: "Body leaning to one side with hands gripping kiosk rails.",
    expectedStatus: "INCORRECT",
    landmarks: (() => {
      const lms = JSON.parse(JSON.stringify(SAMPLE_POSTURE_PRESETS?.WEIGHT_PERFECT?.landmarks || []));
      if (lms.length === 0) return [];
      lms[11].x = 0.35; lms[11].y = 0.23;
      lms[12].x = 0.51; lms[12].y = 0.28; // shoulder tilt
      lms[23].y = 0.48; lms[24].y = 0.53; // hip tilt
      lms[15].x = 0.20; lms[15].y = 0.38; // Arm flaring out on rail
      return lms;
    })()
  },

  ECG_PERFECT: {
    name: "ECG: Seated & Resting",
    measurementType: "ECG",
    description: "Seated still with back supported and hands rested flat on contact plates.",
    expectedStatus: "CORRECT",
    landmarks: (() => {
      return JSON.parse(JSON.stringify(SAMPLE_POSTURE_PRESETS?.BP_PERFECT?.landmarks || []));
    })()
  }
};

// Populate dependent presets once BP_PERFECT is ready
(() => {
  const baseBP = SAMPLE_POSTURE_PRESETS.BP_PERFECT.landmarks;
  const slouch = JSON.parse(JSON.stringify(baseBP));
  slouch[11].x = 0.60; slouch[11].y = 0.36;
  slouch[12].x = 0.80; slouch[12].y = 0.36;
  slouch[0].x = 0.70;  slouch[0].y = 0.28;
  SAMPLE_POSTURE_PRESETS.BP_SLOUCH.landmarks = slouch;

  const crossed = JSON.parse(JSON.stringify(baseBP));
  crossed[25].x = 0.51; crossed[26].x = 0.49;
  crossed[27].x = 0.56; crossed[28].x = 0.44;
  SAMPLE_POSTURE_PRESETS.BP_CROSSED_LEGS.landmarks = crossed;

  const lowArm = JSON.parse(JSON.stringify(baseBP));
  lowArm[13].y = 0.58; lowArm[15].y = 0.65;
  lowArm[14].y = 0.58; lowArm[16].y = 0.65;
  SAMPLE_POSTURE_PRESETS.BP_ARM_LOW.landmarks = lowArm;

  const baseWeight = SAMPLE_POSTURE_PRESETS.WEIGHT_PERFECT.landmarks;
  const leaning = JSON.parse(JSON.stringify(baseWeight));
  leaning[11].x = 0.35; leaning[11].y = 0.23;
  leaning[12].x = 0.51; leaning[12].y = 0.28;
  leaning[23].y = 0.48; leaning[24].y = 0.53;
  leaning[15].x = 0.20; leaning[15].y = 0.38;
  SAMPLE_POSTURE_PRESETS.WEIGHT_LEANING.landmarks = leaning;

  SAMPLE_POSTURE_PRESETS.ECG_PERFECT.landmarks = JSON.parse(JSON.stringify(baseBP));
})();

window.SAMPLE_POSTURE_PRESETS = SAMPLE_POSTURE_PRESETS;
