"""State for the virtual fob device itself, independent of any car."""

from __future__ import annotations

import json
import os
import random


class FobState:
    """Tracks the fob's own battery level and simulated signal strength.

    A real key fob uses a small coin-cell battery that discharges over
    time. Each button press draws current, and remote start draws more
    than a lock/unlock. We model the same behavior so the UI can warn the
    user when the battery is low.
    """

    STARTING_BATTERY: float = 100.0
    LOW_BATTERY_THRESHOLD: float = 20.0
    CRITICAL_BATTERY_THRESHOLD: float = 5.0

    # Per-action battery drain in percentage points. Values are intentionally
    # small so an average session does not empty the battery, but heavy use
    # will eventually trigger the low-battery warning.
    ACTION_COST = {
        "LOCK": 0.3,
        "UNLOCK": 0.3,
        "TRUNK": 0.5,
        "PANIC": 0.8,
        "REMOTE_START": 1.2,
        "REMOTE_STOP": 0.6,
    }

    def __init__(self, state_path: str) -> None:
        """Load the persisted fob state, creating defaults when absent.

        Args:
            state_path: Absolute path to the JSON file used for persistence.
        """
        self._state_path: str = state_path
        self._battery: float = self.STARTING_BATTERY
        self._signal_bars: int = 4
        self._load()

    def _load(self) -> None:
        """Read the stored state, tolerating corrupt or missing files."""
        if not os.path.exists(self._state_path):
            return
        try:
            with open(self._state_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            self._battery = float(data.get("battery", self.STARTING_BATTERY))
            self._signal_bars = int(data.get("signal_bars", 4))
        except (OSError, json.JSONDecodeError, ValueError):
            # Fall back to defaults if the file is unreadable.
            self._battery = self.STARTING_BATTERY
            self._signal_bars = 4

    def _save(self) -> None:
        """Persist the current state to disk."""
        directory = os.path.dirname(self._state_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        try:
            with open(self._state_path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "battery": self._battery,
                        "signal_bars": self._signal_bars,
                    },
                    handle,
                )
        except OSError:
            # Persistence failure should not crash the app; we just lose
            # battery state between runs in the worst case.
            pass

    def apply_action(self, action: str) -> None:
        """Charge the battery cost for a given fob action and refresh signal.

        Args:
            action: The action label, matching a key in ACTION_COST. Unknown
                actions draw a nominal 0.1 percentage points.
        """
        cost = self.ACTION_COST.get(action, 0.1)
        self._battery = max(0.0, self._battery - cost)
        # Simulated radio signal bars fluctuate each time the fob transmits.
        self._signal_bars = random.randint(2, 4)
        self._save()

    def replace_battery(self) -> None:
        """Return the battery to full charge, as if a fresh coin cell was inserted."""
        self._battery = self.STARTING_BATTERY
        self._save()

    @property
    def battery(self) -> float:
        """Return the current battery level as a percentage."""
        return self._battery

    @property
    def signal_bars(self) -> int:
        """Return the most recent simulated signal strength (0-4 bars)."""
        return self._signal_bars

    @property
    def is_low_battery(self) -> bool:
        """True when battery is under the warning threshold."""
        return self._battery <= self.LOW_BATTERY_THRESHOLD

    @property
    def is_critical_battery(self) -> bool:
        """True when battery is dangerously low and actions may misfire."""
        return self._battery <= self.CRITICAL_BATTERY_THRESHOLD

    @property
    def is_dead(self) -> bool:
        """True when the battery has no remaining charge."""
        return self._battery <= 0.0
