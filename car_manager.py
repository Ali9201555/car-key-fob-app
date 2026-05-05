"""Persistent manager for the collection of paired vehicles."""

import csv

from car import Car, make_car_from_dict


class CarManager:
    """Loads, stores, and mutates the collection of paired vehicles.

    The manager is the single source of truth for car state during a
    run. It reads from and writes to a CSV file so state survives
    between launches.
    """

    CSV_FIELDS = [
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
            csv_path: Absolute path to the CSV file used for persistence.
                The file is created on first save if it does not exist.
        """
        self._csv_path = csv_path
        self._cars = {}
        self._active_plate = None
        self.load()

    def load(self) -> None:
        """Load all cars from disk into memory.

        Missing files are treated as an empty collection. Malformed
        rows are skipped but do not abort the whole load so a single
        bad entry cannot lock the user out of their other vehicles.
        """
        self._cars = {}
        try:
            handle = open(self._csv_path, "r", newline="", encoding="utf-8")
        except FileNotFoundError:
            return
        except OSError:
            self._cars = {}
            return
        try:
            reader = csv.DictReader(handle)
            for row in reader:
                try:
                    car = make_car_from_dict(row)
                    self._cars[car.plate] = car
                except (ValueError, KeyError):
                    # Skip malformed rows so one corrupt record does
                    # not hide the rest of the user's garage.
                    continue
        finally:
            handle.close()

        if self._cars and self._active_plate not in self._cars:
            # Pick the first car as the active one if none is selected.
            for plate in self._cars:
                self._active_plate = plate
                break

    def write(self) -> None:
        """Write the current in-memory state back to the CSV file.

        The ``data`` directory is committed to the repository, so the
        write target always exists when the app runs.

        Raises:
            OSError: If the file cannot be written. Callers should catch
                this and surface a user-friendly message.
        """
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
        self.write()

    def remove_car(self, plate: str) -> None:
        """Remove a car by license plate.

        Args:
            plate: The plate of the car to remove.

        Raises:
            KeyError: If the plate is not registered.
        """
        clean = plate.strip().upper()
        if clean not in self._cars:
            raise KeyError(f"No car paired with plate {clean}.")
        del self._cars[clean]
        if self._active_plate == clean:
            # Pick the next available car, or None when the garage is empty.
            self._active_plate = None
            for remaining in self._cars:
                self._active_plate = remaining
                break
        self.write()

    def set_active(self, plate: str) -> None:
        """Mark which car is currently selected in the UI.

        Args:
            plate: The plate to activate.

        Raises:
            KeyError: If the plate is not registered.
        """
        clean = plate.strip().upper()
        if clean not in self._cars:
            raise KeyError(f"No car paired with plate {clean}.")
        self._active_plate = clean

    def get_active(self) -> Car:
        """Return the currently active car, or None when empty.

        Returns:
            The active Car instance, or None if no cars are paired.
        """
        if self._active_plate is None:
            return None
        return self._cars.get(self._active_plate)

    def list_cars(self) -> list:
        """Return all cars in insertion order."""
        return list(self._cars.values())

    def count(self) -> int:
        """Return the number of paired cars."""
        return len(self._cars)
