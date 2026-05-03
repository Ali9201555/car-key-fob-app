// Simple progress meeting deck — 4 slides.
// Run: node build_pptx.js

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Project 2 Progress Meeting";
pres.author = "Ali Alfatin";

const BG = "0F1218";
const PANEL = "1A1F2B";
const INK = "DFE3EA";
const MUTED = "9AA0A6";
const AMBER = "FFB84D";
const BLUE = "2D6CDF";
const GREEN = "29CC74";
const PURPLE = "5E4BD5";
const ORANGE = "C98A2E";
const RED = "C0392B";

function newSlide() {
  const s = pres.addSlide();
  s.background = { color: BG };
  return s;
}

function heading(slide, text, subtitle) {
  slide.addText(text, {
    x: 0.6, y: 0.5, w: 12, h: 0.8,
    fontSize: 36, bold: true, color: INK, fontFace: "Calibri", margin: 0
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.6, y: 1.2, w: 12, h: 0.4,
      fontSize: 16, color: MUTED, italic: true, fontFace: "Calibri", margin: 0
    });
  }
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 1.75, w: 1.5, h: 0,
    line: { color: AMBER, width: 3 }
  });
}

// ============================================================
// Slide 1 — Title
// ============================================================
{
  const s = newSlide();
  s.addText("Project 2", {
    x: 0.6, y: 2.2, w: 12, h: 0.6,
    fontSize: 20, color: AMBER, bold: true, fontFace: "Calibri", charSpacing: 6, margin: 0
  });
  s.addText("Car Key Fob App", {
    x: 0.6, y: 2.8, w: 12, h: 1.4,
    fontSize: 72, bold: true, color: INK, fontFace: "Calibri", margin: 0
  });
  s.addShape(pres.shapes.LINE, {
    x: 0.6, y: 4.4, w: 2, h: 0,
    line: { color: AMBER, width: 3 }
  });
  s.addText("Progress Meeting", {
    x: 0.6, y: 4.5, w: 12, h: 0.5,
    fontSize: 20, color: MUTED, fontFace: "Calibri", italic: true, margin: 0
  });
  s.addText("Ali Alfatin  ·  CSCI 2680", {
    x: 0.6, y: 6.7, w: 12, h: 0.4,
    fontSize: 14, color: MUTED, fontFace: "Calibri", margin: 0
  });
}

// ============================================================
// Slide 2 — The idea + sketch
// ============================================================
{
  const s = newSlide();
  heading(s, "The idea", "A virtual car key fob on your desktop");

  // Left: short description
  s.addText(
    "I want to build a GUI app that works like a real car key fob. " +
    "On the left side is a drawing of the car. On the right side is the " +
    "fob with buttons. Pressing a button changes the car — locks the " +
    "doors, pops the trunk, starts the engine, etc.",
    {
      x: 0.6, y: 2.1, w: 6, h: 3.5,
      fontSize: 16, color: INK, fontFace: "Calibri", paraSpaceAfter: 10, margin: 0
    }
  );

  // Right: sketch of the main window
  drawSketch(s, 7.2, 2.0, 5.5, 4.7);
  s.addText("Rough sketch of the main window", {
    x: 7.2, y: 6.75, w: 5.5, h: 0.35,
    fontSize: 11, color: MUTED, italic: true, align: "center", fontFace: "Calibri", margin: 0
  });
}

// ============================================================
// Slide 3 — What it will do (features)
// ============================================================
{
  const s = newSlide();
  heading(s, "What it will do", "Planned features");

  const features = [
    "5 fob buttons — Lock, Unlock, Trunk, Remote Start, Panic",
    "Multiple cars — add, remove, and switch between vehicles",
    "PIN required for Remote Start and Panic",
    "Fob battery drains with use; warning when low",
    "Every action saved to a CSV event log with a timestamp",
    "Data stored in CSV + JSON so it survives closing the app",
    "Input validation on all text fields",
    "Written in Python + PyQt6 with MVC file structure",
  ];

  features.forEach((f, i) => {
    const y = 2.2 + i * 0.55;
    s.addShape(pres.shapes.OVAL, {
      x: 0.7, y: y + 0.05, w: 0.32, h: 0.32,
      fill: { color: AMBER }, line: { color: AMBER }
    });
    s.addText(`${i + 1}`, {
      x: 0.7, y: y + 0.05, w: 0.32, h: 0.32,
      fontSize: 13, bold: true, color: BG, align: "center", valign: "middle", fontFace: "Calibri", margin: 0
    });
    s.addText(f, {
      x: 1.2, y, w: 11.5, h: 0.45,
      fontSize: 15, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
    });
  });
}

// ============================================================
// Slide 4 — Questions / feedback wanted
// ============================================================
{
  const s = newSlide();
  heading(s, "Questions for the meeting", "What I'd like feedback on");

  const questions = [
    "Is the feature list enough for Project 2, or do I need more?",
    "Should I add sound effects (chirps / horn)?",
    "Would a maintenance-reminder feature be worth adding?",
    "Any edge cases I should make sure to handle?",
  ];

  questions.forEach((q, i) => {
    const y = 2.3 + i * 0.9;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y, w: 12, h: 0.7,
      fill: { color: PANEL }, line: { color: "2A2F3A", width: 1 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.7, y, w: 0.1, h: 0.7,
      fill: { color: AMBER }, line: { color: AMBER }
    });
    s.addText(q, {
      x: 1.0, y, w: 11.5, h: 0.7,
      fontSize: 16, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
    });
  });

  s.addText("AI was used to help generate some boilerplate code — disclosed as required.", {
    x: 0.7, y: 6.7, w: 12, h: 0.4,
    fontSize: 11, color: MUTED, italic: true, fontFace: "Calibri", margin: 0
  });
}

// ============================================================
// SKETCH — simple wireframe of the main window
// ============================================================
function drawSketch(slide, x, y, w, h) {
  // Window frame
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: PANEL }, line: { color: "2A2F3A", width: 2 }
  });
  // Title bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.35,
    fill: { color: "1E2430" }, line: { color: "1E2430" }
  });
  slide.addText("Car Key Fob", {
    x: x + 0.15, y: y + 0.02, w: 4, h: 0.3,
    fontSize: 10, bold: true, color: INK, fontFace: "Calibri", valign: "middle", margin: 0
  });

  // Split the body
  const bodyY = y + 0.5;
  const bodyH = h - 0.7;
  const leftW = w * 0.6;
  const rightW = w * 0.35;
  const rightX = x + leftW + 0.1;

  // Left box — car illustration placeholder
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x + 0.15, y: bodyY, w: leftW - 0.15, h: bodyH,
    fill: { color: BG }, line: { color: "2A2F3A", width: 1 }
  });

  // Simple cartoon car inside
  const carY = bodyY + bodyH * 0.3;
  const carH = bodyH * 0.5;
  const carX = x + 0.35;
  const carW = leftW - 0.55;

  // Roof
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: carX + carW * 0.22, y: carY, w: carW * 0.55, h: carH * 0.45,
    fill: { color: "C0C0C0" }, line: { color: "111111", width: 1 }, rectRadius: 0.08
  });
  // Body
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: carX + carW * 0.08, y: carY + carH * 0.38, w: carW * 0.84, h: carH * 0.4,
    fill: { color: "C0C0C0" }, line: { color: "111111", width: 1 }, rectRadius: 0.08
  });
  // Windows
  slide.addShape(pres.shapes.RECTANGLE, {
    x: carX + carW * 0.26, y: carY + 0.05, w: carW * 0.22, h: carH * 0.32,
    fill: { color: "8FC9FF" }, line: { color: "111111", width: 0.5 }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: carX + carW * 0.52, y: carY + 0.05, w: carW * 0.22, h: carH * 0.32,
    fill: { color: "8FC9FF" }, line: { color: "111111", width: 0.5 }
  });
  // Wheels
  const wr = carH * 0.22;
  slide.addShape(pres.shapes.OVAL, {
    x: carX + carW * 0.14, y: carY + carH * 0.73, w: wr, h: wr,
    fill: { color: "111111" }, line: { color: "111111" }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: carX + carW * 0.72, y: carY + carH * 0.73, w: wr, h: wr,
    fill: { color: "111111" }, line: { color: "111111" }
  });

  // "LOCKED" badge
  slide.addText("LOCKED", {
    x: x + 0.25, y: bodyY + 0.1, w: 1, h: 0.25,
    fontSize: 9, bold: true, color: GREEN, fontFace: "Calibri", margin: 0
  });

  // Right: fob buttons
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: rightX, y: bodyY, w: rightW, h: bodyH,
    fill: { color: BG }, line: { color: "2A2F3A", width: 1 }, rectRadius: 0.1
  });
  slide.addText("KEY FOB", {
    x: rightX, y: bodyY + 0.1, w: rightW, h: 0.25,
    fontSize: 9, bold: true, color: INK, align: "center", charSpacing: 2, fontFace: "Calibri", margin: 0
  });

  const colors = [BLUE, GREEN, PURPLE, ORANGE, RED];
  const labels = ["LOCK", "UNLOCK", "TRUNK", "REMOTE START", "PANIC"];
  const btnH = (bodyH - 1.0) / 5;
  for (let i = 0; i < 5; i++) {
    const by = bodyY + 0.45 + i * btnH;
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: rightX + 0.15, y: by + 0.04, w: rightW - 0.3, h: btnH - 0.1,
      fill: { color: colors[i] }, line: { color: colors[i] }, rectRadius: 0.08
    });
    slide.addText(labels[i], {
      x: rightX + 0.15, y: by + 0.04, w: rightW - 0.3, h: btnH - 0.1,
      fontSize: 9, bold: true, color: "FFFFFF", align: "center", valign: "middle", fontFace: "Calibri", margin: 0
    });
  }

  // Battery bar at bottom of fob
  slide.addText("Battery", {
    x: rightX + 0.15, y: bodyY + bodyH - 0.45, w: rightW - 0.3, h: 0.2,
    fontSize: 7, color: MUTED, fontFace: "Calibri", margin: 0
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rightX + 0.15, y: bodyY + bodyH - 0.25, w: rightW - 0.3, h: 0.12,
    fill: { color: "111111" }, line: { color: "333333" }
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: rightX + 0.17, y: bodyY + bodyH - 0.23, w: (rightW - 0.34) * 0.8, h: 0.08,
    fill: { color: GREEN }, line: { color: GREEN }
  });
}

pres.writeFile({ fileName: "Project2_Progress_Meeting.pptx" })
  .then(file => console.log("Wrote:", file))
  .catch(err => { console.error("FAILED:", err); process.exit(1); });
