"""Dialog for pairing a new car with the virtual fob."""

from __future__ import annotations

from datetime import date
from typing import Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QWidget,
)

from controllers.car_controller import CarController
from models.car import Car


class AddCarDialog(QDialog):
    """Collects the fields required to pair a new Car with the fob."""

    def __init__(
        self,
        car_controller: CarController,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Build the form fields and wire up OK/Cancel.

        Args:
            car_controller: Controller used to pair the new car.
            parent: Optional parent widget for modal ownership.
        """
        super().__init__(parent)
        self._controller: CarController = car_controller
        self._created_car: Optional[Car] = None
        self.setWindowTitle("Pair New Car")
        self.setModal(True)
        self.setMinimumWidth(340)

        form = QFormLayout(self)

        self._plate_edit = QLineEdit()
        self._plate_edit.setMaxLength(8)
        self._plate_edit.setPlaceholderText("ABC-1234")
        form.addRow("License plate:", self._plate_edit)

        self._make_edit = QLineEdit()
        self._make_edit.setPlaceholderText("Toyota")
        form.addRow("Make:", self._make_edit)

        self._model_edit = QLineEdit()
        self._model_edit.setPlaceholderText("Camry")
        form.addRow("Model:", self._model_edit)

        self._year_spin = QSpinBox()
        self._year_spin.setRange(1900, 2100)
        self._year_spin.setValue(date.today().year)
        form.addRow("Year:", self._year_spin)

        self._color_combo = QComboBox()
        self._color_combo.addItems(list(Car.ALLOWED_COLORS))
        self._color_combo.setCurrentText("Silver")
        form.addRow("Color:", self._color_combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_submit(self) -> None:
        """Validate input and ask the controller to pair the car."""
        try:
            car = self._controller.pair_car(
                plate=self._plate_edit.text(),
                make=self._make_edit.text(),
                model=self._model_edit.text(),
                year_text=str(self._year_spin.value()),
                color=self._color_combo.currentText(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid input", str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self,
                "Error",
                f"Could not pair car: {exc}",
            )
            return
        self._created_car = car
        self.accept()

    def created_car(self) -> Optional[Car]:
        """Return the car that was paired, or None if the dialog was cancelled."""
        return self._created_car
