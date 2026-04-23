"""Car model representing a single vehicle paired to the key fob."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class Car:
    """Represents a vehicle paired with the virtual key fob.

    Attributes:
        plate: The license plate number, used as the unique identifier.
        make: Vehicle manufacturer (e.g. "Toyota").
        model: Vehicle model name (e.g. "Camry").
        year: Model year as a four-digit integer.
        color: Exterior color, used for the on-screen rendering.
        locked: True when the doors are locked.
        trunk_open: True when the trunk/boot is open.
        engine_running: True when the engine is running (remote start).
        panic_active: True when the panic alarm is currently sounding.
        fuel_level: Fuel level as a percentage in the range [0, 100].
        odometer: Lifetime distance driven in miles.
    """

    plate: str
    make: str
    model: str
    year: int
    color: str = "Silver"
    locked: bool = True
    trunk_open: bool = False
    engine_running: bool = False
    panic_active: bool = False
    fuel_level: float = 75.0
    odometer: int = 0

    # Acceptable string values for the color field. Kept as a class-level
    # constant so the add-car view can populate a dropdown from the same list
    # the model uses for validation.
    ALLOWED_COLORS: tuple = field(
        default=(
            "Black",
            "White",
            "Silver",
            "Gray",
            "Red",
            "Blue",
            "Green",
            "Yellow",
        ),
        repr=False,
    )

    def __post_init__(self) -> None:
        """Normalize and validate the supplied fields after construction.

        Raises:
            ValueError: If any field fails validation.
        """
        self.plate = self.plate.strip().upper()
        self.make = self.make.strip().title()
        self.model = self.model.strip().title()
        self.color = self.color.strip().title()

        if not self.plate:
            raise ValueError("License plate cannot be empty.")
        if not self.make:
            raise ValueError("Make cannot be empty.")
        if not self.model:
            raise ValueError("Model cannot be empty.")
        if not (1900 <= int(self.year) <= 2100):
            raise ValueError("Year must be between 1900 and 2100.")
        if self.color not in self.ALLOWED_COLORS:
            raise ValueError(
                f"Color must be one of: {', '.join(self.ALLOWED_COLORS)}."
            )
        if not (0.0 <= float(self.fuel_level) <= 100.0):
            raise ValueError("Fuel level must be between 0 and 100 percent.")
        if int(self.odometer) < 0:
            raise ValueError("Odometer cannot be negative.")

        self.year = int(self.year)
        self.fuel_level = float(self.fuel_level)
        self.odometer = int(self.odometer)

    @property
    def display_name(self) -> str:
        """Return a human readable one-line label for the vehicle."""
        return f"{self.year} {self.make} {self.model} ({self.plate})"

    def to_dict(self) -> Dict[str, str]:
        """Serialize the car into a flat string dictionary for CSV storage.

        Returns:
            A dictionary whose keys match the CSV header row. All values are
            strings so they round-trip cleanly through csv.DictReader.
        """
        return {
            "plate": self.plate,
            "make": self.make,
            "model": self.model,
            "year": str(self.year),
            "color": self.color,
            "locked": str(self.locked),
            "trunk_open": str(self.trunk_open),
            "engine_running": str(self.engine_running),
            "panic_active": str(self.panic_active),
            "fuel_level": f"{self.fuel_level:.1f}",
            "odometer": str(self.odometer),
        }

    @classmethod
    def from_dict(cls, row: Dict[str, str]) -> "Car":
        """Build a Car from a CSV row dictionary.

        Args:
            row: Mapping of CSV column name to stringified value.

        Returns:
            A fully validated Car instance.

        Raises:
            KeyError: If a required column is missing from the row.
            ValueError: If any value cannot be coerced or fails validation.
        """
        return cls(
            plate=row["plate"],
            make=row["make"],
            model=row["model"],
            year=int(row["year"]),
            color=row.get("color", "Silver"),
            locked=row.get("locked", "True") == "True",
            trunk_open=row.get("trunk_open", "False") == "True",
            engine_running=row.get("engine_running", "False") == "True",
            panic_active=row.get("panic_active", "False") == "True",
            fuel_level=float(row.get("fuel_level", "75.0")),
            odometer=int(row.get("odometer", "0")),
        )
