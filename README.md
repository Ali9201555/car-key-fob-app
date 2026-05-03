# Car Key Fob App

A virtual car key fob desktop application built with **PyQt6**. The app
simulates a modern remote-keyless-entry device: you can pair multiple
vehicles, lock/unlock doors, pop the trunk, trigger the panic alarm, and
remote-start the engine. Fob battery drain, signal strength, and a
timestamped event history are all simulated and persisted between runs.

This project was built for CSCI 2680 Project 2.

## Features

- **Full PyQt6 GUI** with a custom-drawn car illustration that updates
  in real time to reflect lock, trunk, engine, and alarm state.
- **Five fob actions**: Lock, Unlock, Trunk, Remote Start, and Panic.
- **Multiple cars**: pair, remove, and switch between several vehicles.
  Each car has its own plate, make, model, year, color, fuel level, and
  odometer reading.
- **PIN-protected privileged actions**: Panic and Remote Start require
  the owner's 4-digit PIN. The PIN is salted and SHA-256 hashed before
  being written to disk; the clear-text PIN is never stored.
- **Fob battery simulation**: every button press draws a small amount of
  battery. Warnings appear at 20% and 5%, and the fob is disabled when
  the battery is dead. A "Replace Battery" menu item restores 100%.
- **Simulated radio signal** with a 0-4 bar indicator that fluctuates
  each time the fob transmits.
- **Event history**: every action is logged with a timestamp, plate,
  action label, and detail. The history is stored in a CSV file and
  viewable through the Tools menu.
- **CSV persistence**: cars, events, and auth data all survive a restart.

## Project structure

```
car_key_fob_app/
├── main.py                  # Entry point
├── car.py                   # Car class + validation
├── car_manager.py           # CSV-backed collection of cars
├── event_log.py             # Timestamped event history
├── fob_state.py             # Fob battery + signal persistence
├── user_auth.py             # PIN authentication
├── auth_controller.py       # PIN login + change-PIN
├── car_controller.py        # Pair / remove / switch cars
├── fob_controller.py        # Lock / unlock / trunk / panic / remote-start
├── main_window.py           # Top-level QMainWindow
├── car_status_widget.py     # Custom-painted car illustration
├── fob_widget.py            # Virtual key fob buttons + battery
├── add_car_dialog.py        # Pair a new car
├── pin_dialog.py            # Enter PIN
├── change_pin_dialog.py     # Replace current PIN
├── history_view.py          # Event-history dialog
├── requirements.txt
└── data/
    ├── cars.csv             # Sample garage, seeded on first run
    ├── events.csv           # Created on first action
    ├── fob_state.json       # Created on first use
    └── auth.txt             # Created on first launch
```

## Installation

1. Install Python 3.10 or newer.
2. Install the one dependency:

   ```
   pip install -r requirements.txt
   ```

## Running

From the project root:

```
python main.py
```

The application seeds two sample cars on first launch. You can remove
those and pair your own through **File → Pair New Car…**.

## Default PIN

The first time the app launches it creates a PIN of **`1234`**. Change
it from **Tools → Change PIN…** before using the app for anything that
matters. The PIN is required for the Panic and Remote Start buttons.

## Data validation

Every text field that accepts keyboard input is validated. Examples:

- License plate must not be empty; it is uppercased automatically.
- Year must be a four-digit integer between 1900 and 2100.
- Color must match one of the supported values.
- PIN must be exactly four digits (0-9).
- Paired cars must have a unique plate.

Invalid input triggers a `QMessageBox.warning` explaining which field
needs attention. Nothing is persisted until validation passes.

## Exception handling

All file I/O (CSV, JSON, auth) catches `OSError` and degrades to an
in-memory-only session rather than crashing. Unknown startup failures
are shown in a dialog via a top-level `try/except` in `main.py`.

## Requirement checklist for Project 2

- [x] GUI interface using PyQt6.
- [x] Code separated into `models/`, `views/`, `controllers/` packages.
- [x] Data stored in CSV files (`cars.csv`, `events.csv`) and JSON
      (`fob_state.json`).
- [x] Keyboard input validation on every editable field.
- [x] Exception handling around all file I/O and dialog submissions.
- [x] Docstrings for every class and function.
- [x] Type hints on every function header.
- [x] Descriptive variable, class, and file names throughout.
