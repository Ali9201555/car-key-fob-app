"""Numbered event log for key fob activity."""

import csv


class FobEvent:
    """A single recorded event such as a lock, unlock, or panic press."""

    def __init__(
        self,
        sequence: int,
        plate: str,
        action: str,
        detail: str,
    ) -> None:
        """Build a fob event record.

        Args:
            sequence: Auto-incrementing event number; the first event
                stored is 1, the second is 2, and so on.
            plate: License plate of the car involved (or empty for
                fob-level events such as battery replacement).
            action: Short uppercase action label (e.g. ``"LOCK"``).
            detail: Free-form description shown in the history view.
        """
        self.sequence = sequence
        self.plate = plate
        self.action = action
        self.detail = detail

    def to_dict(self) -> dict:
        """Serialize the event for CSV storage.

        Returns:
            A dictionary keyed by CSV column name.
        """
        return {
            "sequence": str(self.sequence),
            "plate": self.plate,
            "action": self.action,
            "detail": self.detail,
        }


class EventLog:
    """Append-only log of fob events, persisted to a CSV file."""

    CSV_FIELDS = ["sequence", "plate", "action", "detail"]
    MAX_EVENTS = 500  # Keep the log bounded to avoid unbounded growth.

    def __init__(self, csv_path: str) -> None:
        """Load the existing log or create a fresh in-memory list.

        Args:
            csv_path: Path to the event log CSV file.
        """
        self._csv_path = csv_path
        self._events = []
        self._next_sequence = 1
        self._load()

    def _load(self) -> None:
        """Read existing events from disk, ignoring malformed rows."""
        try:
            handle = open(self._csv_path, "r", newline="", encoding="utf-8")
        except FileNotFoundError:
            return
        except OSError:
            self._events = []
            return
        try:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    self._events.append(
                        FobEvent(
                            sequence=int(row["sequence"]),
                            plate=row.get("plate", ""),
                            action=row["action"],
                            detail=row.get("detail", ""),
                        )
                    )
                except (KeyError, ValueError):
                    continue
        finally:
            handle.close()
        if self._events:
            self._next_sequence = self._events[-1].sequence + 1

    def _write(self) -> None:
        """Persist the current in-memory event list to disk."""
        with open(self._csv_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for event in self._events:
                writer.writerow(event.to_dict())

    def record(self, plate: str, action: str, detail: str = "") -> FobEvent:
        """Append a new event with the next sequence number.

        Args:
            plate: Plate of the affected car, or empty string.
            action: Short uppercase action label.
            detail: Optional free-form description.

        Returns:
            The event that was recorded (useful for immediate UI updates).
        """
        event = FobEvent(
            sequence=self._next_sequence,
            plate=plate,
            action=action,
            detail=detail,
        )
        self._next_sequence += 1
        self._events.append(event)
        # Keep the log bounded; drop the oldest entries when over the cap.
        if len(self._events) > self.MAX_EVENTS:
            self._events = self._events[-self.MAX_EVENTS:]
        try:
            self._write()
        except OSError:
            # Logging must never crash the caller; worst case we keep the
            # event in memory for this session only.
            pass
        return event

    def recent(self, limit: int = 50) -> list:
        """Return the most recent events, newest first.

        Args:
            limit: Maximum number of events to return.

        Returns:
            A list of events ordered newest to oldest, capped at ``limit``.
        """
        if limit <= 0:
            return []
        recent_events = self._events[-limit:]
        recent_events = list(recent_events)
        recent_events.reverse()
        return recent_events

    def clear(self) -> None:
        """Erase the entire event history and persist the change."""
        self._events = []
        try:
            self._write()
        except OSError:
            pass
