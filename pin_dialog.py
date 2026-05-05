"""Dialog that prompts the user for their four-digit PIN."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from auth_controller import AuthController


class PinDialog(QDialog):
    """Modal dialog that authenticates the owner before privileged actions.

    The dialog stays open until the user either enters a correct PIN, hits
    cancel, or runs out of attempts. On success, ``exec()`` returns
    ``QDialog.DialogCode.Accepted``.
    """

    def __init__(
        self,
        auth_controller: AuthController,
        parent: QWidget = None,
    ) -> None:
        """Build the dialog widgets and wire up the submit button.

        Args:
            auth_controller: The controller used to validate the PIN.
            parent: Optional parent widget for modal ownership.
        """
        super().__init__(parent)
        self._auth: AuthController = auth_controller
        self.setWindowTitle("Enter PIN")
        self.setModal(True)
        self.setMinimumWidth(280)

        layout = QVBoxLayout(self)

        self._prompt_label = QLabel(
            "Enter your 4-digit PIN to continue.\n"
            "(Default PIN on first run is 1234.)"
        )
        self._prompt_label.setWordWrap(True)
        layout.addWidget(self._prompt_label)

        self._pin_edit = QLineEdit()
        self._pin_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pin_edit.setMaxLength(4)
        self._pin_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pin_edit.setPlaceholderText("****")
        layout.addWidget(self._pin_edit)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: #b00020;")
        layout.addWidget(self._status_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_submit)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_submit(self) -> None:
        """Validate the PIN and accept the dialog if correct."""
        if self._auth.is_locked_out():
            QMessageBox.critical(
                self,
                "Locked out",
                "Too many failed PIN attempts. Restart the application.",
            )
            self.reject()
            return

        pin = self._pin_edit.text()
        try:
            success = self._auth.attempt_login(pin)
        except Exception as exc:
            # Surface any other unexpected error in a dialog.
            QMessageBox.critical(self, "Error", f"Unexpected error: {exc}")
            return

        if success:
            self.accept()
            return

        remaining = self._auth.remaining_attempts()
        if remaining <= 0:
            QMessageBox.critical(
                self,
                "Locked out",
                "Too many failed PIN attempts. Restart the application.",
            )
            self.reject()
            return

        self._status_label.setText(
            f"Incorrect PIN. {remaining} attempt(s) remaining."
        )
        self._pin_edit.clear()
        self._pin_edit.setFocus()
