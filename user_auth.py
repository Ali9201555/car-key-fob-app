"""PIN-based authentication for privileged key fob operations.

The owner's PIN guards the panic alarm and remote-start buttons. The
PIN is stored in a plain text file beside the other data files.
"""

import os


class UserAuth:
    """Manages the owner's PIN for operations like panic and remote start."""

    DEFAULT_PIN = "1234"
    PIN_LENGTH = 4
    MAX_ATTEMPTS = 3

    def __init__(self, auth_path: str) -> None:
        """Load the stored PIN, creating the default one if needed.

        Args:
            auth_path: Absolute path to the credential file.
        """
        self._auth_path = auth_path
        self._stored_pin = ""
        self._failed_attempts = 0
        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        """Read the stored PIN, or seed it with the default 1234."""
        if os.path.exists(self._auth_path):
            try:
                with open(self._auth_path, "r", encoding="utf-8") as handle:
                    saved = handle.read().strip()
                if saved:
                    self._stored_pin = saved
                    return
            except OSError:
                # Fall through and re-create the file with the default PIN.
                pass
        self._stored_pin = self.DEFAULT_PIN
        self._save()

    def _save(self) -> None:
        """Persist the current PIN to disk."""
        directory = os.path.dirname(self._auth_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self._auth_path, "w", encoding="utf-8") as handle:
            handle.write(self._stored_pin)

    def validate_pin_format(self, pin: str) -> str:
        """Validate the shape of a PIN string coming from the UI.

        Args:
            pin: Raw text from the PIN entry field.

        Returns:
            The validated PIN, stripped of surrounding whitespace.

        Raises:
            ValueError: If the PIN is empty, the wrong length, or
                contains non-digit characters.
        """
        if pin is None:
            raise ValueError("PIN is required.")
        clean = pin.strip()
        if len(clean) != self.PIN_LENGTH:
            raise ValueError(
                f"PIN must be exactly {self.PIN_LENGTH} digits."
            )
        if not clean.isdigit():
            raise ValueError("PIN must contain only digits 0-9.")
        return clean

    def verify(self, pin: str) -> bool:
        """Check whether the supplied PIN matches the stored one.

        Args:
            pin: The clear text PIN entered by the user.

        Returns:
            True when the PIN matches, False otherwise. On mismatch the
            internal failed-attempt counter is incremented; callers
            should check ``is_locked_out`` after a failure.
        """
        try:
            clean = self.validate_pin_format(pin)
        except ValueError:
            self._failed_attempts += 1
            return False

        if clean == self._stored_pin:
            self._failed_attempts = 0
            return True
        self._failed_attempts += 1
        return False

    def change_pin(self, old_pin: str, new_pin: str) -> None:
        """Replace the stored PIN after confirming the current one.

        Args:
            old_pin: The currently valid PIN.
            new_pin: The desired replacement PIN.

        Raises:
            PermissionError: If the old PIN does not match.
            ValueError: If the new PIN fails format validation.
        """
        if not self.verify(old_pin):
            raise PermissionError("Current PIN is incorrect.")
        clean_new = self.validate_pin_format(new_pin)
        self._stored_pin = clean_new
        self._failed_attempts = 0
        self._save()

    def get_failed_attempts(self) -> int:
        """Return how many consecutive wrong PINs have been entered."""
        return self._failed_attempts

    def is_locked_out(self) -> bool:
        """Return True once the maximum failed attempts have been reached."""
        return self._failed_attempts >= self.MAX_ATTEMPTS

    def reset_attempts(self) -> None:
        """Clear the failed-attempt counter."""
        self._failed_attempts = 0
