"""Timestamped event log for key fob activity."""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class FobEvent:
    """A single recorded event such as a lock, unlock, or panic press.

    Attributes:
        timestamp: ISO-8601 formatted local time when the event occurred.
        plate: License plate of the car involved, or an empty string for
            fob-level events such as "Fob battery replaced".
        action: Short label describing what happened (e.g. "LOCK", "UNLOCK").
        detail: Free-form description of the event for the history view.
    """

    timestamp: str
    plate: str
    action: str
    detail: str

    def to_dict(self) -> dict:
        """Serialize the event for CSV storage."""
        return {
            "timestamp": self.timestamp,
            "plate": self.plate,
            "action": self.action,
            "detail": self.detail,
        }


class EventLog:
    """Append-only log of fob events, persisted to a CSV file."""

    CSV_FIELDS: List[str] = ["timestamp", "plate", "action", "detail"]
    MAX_EVENTS: int = 500  # Keep the log bounded to avoid unbounded growth.

    def __init__(self, csv_path: str) -> None:
        """Load the existing log or create a fresh in-memory list.

        Args:
            csv_path: Absolute path to the event log CSV file.
        """
        self._csv_path: str = csv_path
        self._events: List[FobEvent] = []
        self._load()

    def _load(self) -> None:
        """Read existing events from disk, ignoring malformed rows."""
        if not os.path.exists(self._csv_path):
            return
        try:
            with open(self._csv_path, "r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    try:
                        self._events.append(
                            FobEvent(
                                timestamp=row["timestamp"],
                                plate=row.get("plate", ""),
                                action=row["action"],
                                detail=row.get("detail", ""),
                            )
                        )
                    except KeyError:
                        continue
        except OSError:
            self._events = []

    def _save(self) -> None:
        """Persist the current in-memory event list to disk."""
        directory = os.path.dirname(self._csv_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self._csv_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for event in self._events:
                writer.writerow(event.to_dict())

    def record(self, plate: str, action: str, detail: str = "") -> FobEvent:
        """Append a new event with the current timestamp.

        Args:
            plate: Plate of the affected car, or empty string.
            action: Short uppercase action label.
            detail: Optional free-form description.

        Returns:
            The event that was recorded (useful for immediate UI updates).
        """
        event = FobEvent(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            plate=plate,
            action=action,
            detail=detail,
        )
        self._events.append(event)
        # Keep the log bounded; drop the oldest entries when over the cap.
        if len(self._events) > self.MAX_EVENTS:
            self._events = self._events[-self.MAX_EVENTS :]
        try:
            self._save()
        except OSError:
            # Logging must never crash the caller; worst case we keep the
            # event in memory for this session only.
            pass
        return event

    def recent(self, limit: int = 50) -> List[FobEvent]:
        """Return the most recent events, newest first.

        Args:
            limit: Maximum number of events to return.

        Returns:
            A list of events ordered newest to oldest, capped at ``limit``.
        """
        if limit <= 0:
            return []
        return list(reversed(self._events[-limit:]))

    def clear(self) -> None:
        """Erase the entire event history and persist the change."""
        self._events.clear()
        try:
            self._save()
        except OSError:
            pass
