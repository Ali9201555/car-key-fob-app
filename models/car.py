"""Car model representing a single vehicle paired to the key fob."""


class Car:
    """Represents a vehicle paired with the virtual key fob."""

    # Acceptable string values for the color field. Kept as a class-level
    # constant so the add-car view can populate a dropdown from the same
    # list the model uses for validation.
    ALLOWED_COLORS = (
        "Black",
        "White",
        "Silver",
        "Gray",
        "Red",
        "Blue",
        "Green",
        "Yellow",
    )

    def __init__(
        self,
        plate: str,
        make: str,
        model: str,
        year: int,
        color: str = "Silver",
        locked: bool = True,
        trunk_open: bool = False,
        engine_running: bool = False,
        panic_active: bool = False,
        fuel_level: float = 75.0,
        odometer: int = 0,
    ) -> None:
        """Build a Car from its individual fields.

        Args:
            plate: License plate (used as the unique id).
            make: Manufacturer (e.g. ``"Toyota"``).
            model: Model name (e.g. ``"Camry"``).
            year: Four-digit year between 1900 and 2100.
            color: One of ``ALLOWED_COLORS``.
            locked: Whether the doors are locked at start.
            trunk_open: Whether the trunk is open.
            engine_running: Whether the engine is running.
            panic_active: Whether the panic alarm is sounding.
            fuel_level: Fuel percentage 0-100.
            odometer: Lifetime miles driven, must be non-negative.

        Raises:
            ValueError: If any field fails validation.
        """
        self.plate = plate.strip().upper()
        self.make = make.strip().title()
        self.model = model.strip().title()
        self.color = color.strip().title()
        self.locked = locked
        self.trunk_open = trunk_open
        self.engine_running = engine_running
        self.panic_active = panic_active
        self.fuel_level = float(fuel_level)
        self.odometer = int(odometer)

        if not self.plate:
            raise ValueError("License plate cannot be empty.")
        if not self.make:
            raise ValueError("Make cannot be empty.")
        if not self.model:
            raise ValueError("Model cannot be empty.")
        if not (1900 <= int(year) <= 2100):
            raise ValueError("Year must be between 1900 and 2100.")
        self.year = int(year)
        if self.color not in self.ALLOWED_COLORS:
            raise ValueError(
                f"Color must be one of: {', '.join(self.ALLOWED_COLORS)}."
            )
        if not (0.0 <= self.fuel_level <= 100.0):
            raise ValueError("Fuel level must be between 0 and 100 percent.")
        if self.odometer < 0:
            raise ValueError("Odometer cannot be negative.")

    @property
    def display_name(self) -> str:
        """Return a human readable one-line label for the vehicle."""
        return f"{self.year} {self.make} {self.model} ({self.plate})"

    def to_dict(self) -> dict:
        """Serialize the car into a flat string dictionary for CSV storage.

        Returns:
            A dictionary whose keys match the CSV header row.
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
    def from_dict(cls, row: dict) -> "Car":
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
