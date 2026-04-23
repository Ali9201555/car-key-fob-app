"""Dialog letting the owner change their stored PIN."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QWidget,
)

from controllers.auth_controller import AuthController


class ChangePinDialog(QDialog):
    """Three-field dialog for replacing the current PIN."""

    def __init__(
        self,
        auth_controller: AuthController,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Lay out the three password fields and OK/Cancel buttons.

        Args:
            auth_controller: Controller used to validate and apply the change.
            parent: Optional parent widget for modal ownership.
        """
        super().__init__(parent)
        self._auth: AuthController = auth_controller
        self.setWindowTitle("Change PIN")
        self.setModal(True)
        self.setMinimumWidth(320)

        form = QFormLayout(self)

        self._old_edit = self._make_pin_edit()
        self._new_edit = self._make_pin_edit()
        self._confirm_edit = self._make_pin_edit()

        form.addRow("Current PIN:", self._old_edit)
        form.addRow("New PIN:", self._new_edit)
        form.addRow("Confirm new PIN:", self._confirm_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_submit)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    @staticmethod
    def _make_pin_edit() -> QLineEdit:
        """Build one of the three password-mode PIN fields."""
        edit = QLineEdit()
        edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.setMaxLength(4)
        edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return edit

    def _on_submit(self) -> None:
        """Ask the controller to change the PIN and close on success."""
        try:
            self._auth.change_pin(
                self._old_edit.text(),
                self._new_edit.text(),
                self._confirm_edit.text(),
            )
        except PermissionError as exc:
            QMessageBox.warning(self, "Access denied", str(exc))
            return
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid PIN", str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Error", f"Unexpected error: {exc}")
            return
        QMessageBox.information(
            self,
            "PIN changed",
            "Your PIN has been updated.",
        )
        self.accept()
