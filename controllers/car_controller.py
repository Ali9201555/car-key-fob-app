"""Controller for pairing, removing, and switching cars in the garage."""

from __future__ import annotations

from typing import List, Optional

from models.car import Car
from models.car_manager import CarManager
from models.event_log import EventLog


class CarController:
    """Mediates between the add/remove car dialogs and the CarManager.

    The controller owns input validation so the dialog code only has to
    forward the raw strings from its fields.
    """

    def __init__(self, car_manager: CarManager, event_log: EventLog) -> None:
        """Store references to the shared manager and event log.

        Args:
            car_manager: The CarManager that owns persistence.
            event_log: The EventLog used to record pair/remove operations.
        """
        self._manager: CarManager = car_manager
        self._log: EventLog = event_log

    def pair_car(
        self,
        plate: str,
        make: str,
        model: str,
        year_text: str,
        color: str,
    ) -> Car:
        """Validate the raw field text and pair a new car to the fob.

        Args:
            plate: License plate string from the dialog.
            make: Manufacturer name.
            model: Model name.
            year_text: Four-digit year as raw text from a line edit.
            color: Exterior color selection.

        Returns:
            The newly created and persisted Car.

        Raises:
            ValueError: If any field is blank, the year is not a number, or
                a car with the same plate is already paired.
        """
        plate = (plate or "").strip().upper()
        make = (make or "").strip()
        model = (model or "").strip()
        color = (color or "").strip()

        if not plate or not make or not model:
            raise ValueError("Plate, make, and model are all required.")

        try:
            year = int((year_text or "").strip())
        except ValueError as exc:
            raise ValueError("Year must be a whole number.") from exc

        car = Car(
            plate=plate,
            make=make,
            model=model,
            year=year,
            color=color,
        )
        self._manager.add_car(car)
        self._log.record(
            plate=car.plate,
            action="PAIR",
            detail=f"Paired {car.display_name}",
        )
        return car

    def remove_car(self, plate: str) -> None:
        """Remove a paired car and log the event.

        Args:
            plate: The plate of the car to remove.

        Raises:
            KeyError: If the plate is not registered.
        """
        plate = (plate or "").strip().upper()
        car = next(
            (c for c in self._manager.list_cars() if c.plate == plate),
            None,
        )
        self._manager.remove_car(plate)
        detail = f"Removed {car.display_name}" if car else f"Removed {plate}"
        self._log.record(plate=plate, action="UNPAIR", detail=detail)

    def switch_active(self, plate: str) -> Car:
        """Change which car is currently selected.

        Args:
            plate: The plate of the car to make active.

        Returns:
            The newly active Car.

        Raises:
            KeyError: If the plate is not registered.
        """
        self._manager.set_active(plate)
        active = self._manager.get_active()
        if active is None:
            # This branch is unreachable after a successful set_active, but
            # we keep the explicit guard so future refactors cannot silently
            # return None from a method whose return type is Car.
            raise KeyError("No active car after switch.")
        self._log.record(
            plate=active.plate,
            action="SWITCH",
            detail=f"Active car set to {active.display_name}",
        )
        return active

    def list_cars(self) -> List[Car]:
        """Return all paired cars in insertion order."""
        return self._manager.list_cars()

    def get_active(self) -> Optional[Car]:
        """Return the currently active car, or None when the garage is empty."""
        return self._manager.get_active()

    def save(self) -> None:
        """Persist any mutations made to car state."""
        self._manager.save()
