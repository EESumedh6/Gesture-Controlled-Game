# ✈️ Gesture-Controlled Aircraft Game Controller

A real-time computer vision system that lets you control a flight simulator using **facial movements** and **hand gestures** — no keyboard or mouse required. Built with OpenCV, MediaPipe-based CVZone, and PyAutoGUI.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Gesture Map](#gesture-map)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)

---

## Overview

This project replaces traditional keyboard input for flight simulators with an intuitive gesture-based control system. A webcam tracks your **face position** for directional flight control and reads **dual-hand gestures** for combat actions like firing missiles, deploying flares, and activating boosters — all in real time.

---

## Features

- 🎯 **Face-based directional control** — head position controls pitch and roll (W/A/S/D keys)
- 🤲 **Dual-hand gesture recognition** — left and right hand gestures trigger distinct combat actions
- 🚀 **Action cooldowns** — threaded cooldown timers prevent rapid re-triggering of missiles, flares, and boosters
- ⚡ **Gesture activation sequence** — a deliberate activation gesture (thumbs + pinkies up on both hands) enables control, avoiding accidental inputs
- 📊 **Real-time FPS overlay** — averaged over 30 frames for smooth display

---

## Tech Stack

| Library | Purpose |
|---|---|
| OpenCV (`cv2`) | Camera capture, frame rendering, visual overlays |
| CVZone | FaceMesh detector, Hand detector, FPS reader |
| PyAutoGUI | Simulating keyboard key presses and releases |
| Threading | Non-blocking cooldown timers and gesture activation delay |

---

## How It Works

### 1. Face Tracking → Directional Control
The system tracks **facial landmark #168** (nose bridge) as the control point. Relative to reference landmarks on the left (#57) and right (#287) sides of the face:
- Head tilts **up** → `W` key held
- Head tilts **down** → `S` key held
- Head tilts **right** past the right landmark → `D` key held
- Head tilts **left** past the left landmark → `A` key held

### 2. Hand Gesture → Combat Actions
With both hands in frame, the system reads index fingertip (landmark 8) and thumb tip (landmark 4) positions on each hand:

| Gesture | Action | Key |
|---|---|---|
| Both thumbs close to index fingers | Fire missile | `Space` |
| Right thumb open, left thumb pinched | Deploy flares | `R` |
| Left thumb open, right thumb pinched | Gun fire (hold) | `Left Arrow` |
| Both index fingers close together | Activate booster | `Shift` |

### 3. Activation Sequence
To prevent accidental control, the system waits for a deliberate activation gesture (thumbs + pinkies up on both hands: `[1,0,0,0,1]`) before entering control mode. A 3-second delay follows before gesture control goes live.

### 4. Threading
All cooldowns (missile: 2s, flares: 2s, booster: 3s) and the activation delay run on **separate daemon threads** so the main loop never blocks.

---

## Gesture Map

```
FACE TRACKING                    HAND GESTURES
─────────────────────────────    ──────────────────────────────────
Head UP    → W (pitch up)        Both thumbs pinched  → 🚀 Missile
Head DOWN  → S (pitch down)      R.open + L.pinched   → 🔥 Flares
Head RIGHT → D (bank right)      L.open + R.pinched   → 🔫 Gun fire
Head LEFT  → A (bank left)       Index fingers close  → ⚡ Booster
```

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/GestureAircraftControl.git
cd GestureAircraftControl
```

### 2. Install Dependencies
```bash
pip install opencv-python cvzone mediapipe pyautogui
```

### 3. Verify Webcam Access
Make sure your webcam is connected and accessible at device index `0`.

---

## Usage

```bash
python main.py
```

**Steps:**
1. Sit in front of your webcam with your face clearly visible
2. Hold up both hands with **thumbs and pinkies extended** to activate gesture control
3. Wait 3 seconds for the confirmation message: `"Gesture Control On"`
4. Control your aircraft using head movements and hand gestures
5. Press `Q` to quit

> **Tip:** Run your flight simulator (e.g. War Thunder, Microsoft Flight Simulator) alongside this script. PyAutoGUI sends keystrokes to the active window.

---

## Project Structure

```
GestureAircraftControl/
│
├── main.py          # Main control loop — camera, detection, gesture logic
└── README.md
```

---

## Limitations

- Requires **good lighting** for reliable facial and hand landmark detection
- Best used with **both hands always in frame**
- Detection confidence drops at extreme angles or with partial occlusion
- PyAutoGUI sends inputs to whichever window is in focus — ensure the game window is active

---

## Future Improvements

- [ ] Add a GUI overlay showing current gesture state and active keys
- [ ] Support configurable key mappings via a config file
- [ ] Add head-roll detection for rudder control (yaw axis)
- [ ] Calibrate control thresholds dynamically based on seated distance from camera
- [ ] Package as a standalone `.exe` for non-Python users

---

## License

This project is open-source and available under the [MIT License](LICENSE).

---

## Acknowledgements

- [CVZone](https://github.com/cvzone/cvzone) by Murtaza Hassan for the FaceMesh and Hand detection wrappers
- [MediaPipe](https://mediapipe.dev/) by Google for the underlying landmark models
- [PyAutoGUI](https://pyautogui.readthedocs.io/) for cross-platform keyboard simulation
