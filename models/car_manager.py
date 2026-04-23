"""Persistent manager for the collection of paired vehicles."""

from __future__ import annotations

import csv
import os
from typing import Dict, List, Optional

from models.car import Car


class CarManager:
    """Loads, stores, and mutates the collection of paired vehicles.

    The manager is the single source of truth for car state during a run. It
    reads from and writes to a CSV file so state survives between launches.
    """

    CSV_FIELDS: List[str] = [
        "plate",
        "make",
        "model",
        "year",
        "color",
        "locked",
        "trunk_open",
        "engine_running",
        "panic_active",
        "fuel_level",
        "odometer",
    ]

    def __init__(self, csv_path: str) -> None:
        """Initialize the manager and load any existing data from disk.

        Args:
            csv_path: Absolute path to the CSV file used for persistence. The
                file is created on first save if it does not exist.
        """
        self._csv_path: str = csv_path
        self._cars: Dict[str, Car] = {}
        self._active_plate: Optional[str] = None
        self.load()

    def load(self) -> None:
        """Load all cars from disk into memory.

        Missing or empty files are treated as an empty collection. Malformed
        rows are skipped but do not abort the whole load so a single bad
        entry cannot lock the user out of their other vehicles.
        """
        self._cars.clear()
        if not os.path.exists(self._csv_path):
            return
        try:
            with open(self._csv_path, "r", newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    try:
                        car = Car.from_dict(row)
                        self._cars[car.plate] = car
                    except (ValueError, KeyError):
                        # Skip malformed rows so one corrupt record does not
                        # hide the rest of the user's garage.
                        continue
        except OSError:
            # File exists but cannot be read; leave the in-memory list empty
            # rather than crashing the application.
            self._cars.clear()

        if self._cars and self._active_plate not in self._cars:
            self._active_plate = next(iter(self._cars))

    def save(self) -> None:
        """Write the current in-memory state back to the CSV file.

        Raises:
            OSError: If the file cannot be written. Callers should catch
                this and surface a user-friendly message.
        """
        directory = os.path.dirname(self._csv_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self._csv_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
            for car in self._cars.values():
                writer.writerow(car.to_dict())

    def add_car(self, car: Car) -> None:
        """Add a new car to the garage.

        Args:
            car: A validated Car instance.

        Raises:
            ValueError: If the plate is already registered.
        """
        if car.plate in self._cars:
            raise ValueError(
                f"A car with plate {car.plate} is already paired."
            )
        self._cars[car.plate] = car
        if self._active_plate is None:
            self._active_plate = car.plate
        self.save()

    def remove_car(self, plate: str) -> None:
        """Remove a car by license plate.

        Args:
            plate: The plate of the car to remove.

        Raises:
            KeyError: If the plate is not registered.
        """
        plate = plate.strip().upper()
        if plate not in self._cars:
            raise KeyError(f"No car paired with plate {plate}.")
        del self._cars[plate]
        if self._active_plate == plate:
            self._active_plate = next(iter(self._cars), None)
        self.save()

    def set_active(self, plate: str) -> None:
        """Mark which car is currently selected in the UI.

        Args:
            plate: The plate to activate.

        Raises:
            KeyError: If the plate is not registered.
        """
        plate = plate.strip().upper()
        if plate not in self._cars:
            raise KeyError(f"No car paired with plate {plate}.")
        self._active_plate = plate

    def get_active(self) -> Optional[Car]:
        """Return the currently active car, or None if the garage is empty."""
        if self._active_plate is None:
            return None
        return self._cars.get(self._active_plate)

    def list_cars(self) -> List[Car]:
        """Return all cars in insertion order."""
        return list(self._cars.values())

    def count(self) -> int:
        """Return the number of paired cars."""
        return len(self._cars)
