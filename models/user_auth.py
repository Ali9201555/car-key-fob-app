"""PIN-based authentication for privileged key fob operations."""

from __future__ import annotations

import hashlib
import os
import secrets
from typing import Optional


class UserAuth:
    """Manages the owner's PIN for operations like panic and remote start.

    The PIN is never written to disk in clear text. A random per-install
    salt is generated on first use, and only the SHA-256 hash of
    salt + PIN is persisted. This matches how a real fob pairs to a user
    account.
    """

    DEFAULT_PIN: str = "1234"
    PIN_LENGTH: int = 4
    MAX_ATTEMPTS: int = 3

    def __init__(self, auth_path: str) -> None:
        """Load the stored credential, creating a default one if needed.

        Args:
            auth_path: Absolute path to the credential file.
        """
        self._auth_path: str = auth_path
        self._salt: str = ""
        self._pin_hash: str = ""
        self._failed_attempts: int = 0
        self._load_or_initialize()

    def _load_or_initialize(self) -> None:
        """Read credentials from disk or seed them with the default PIN."""
        if os.path.exists(self._auth_path):
            try:
                with open(self._auth_path, "r", encoding="utf-8") as handle:
                    lines = handle.read().splitlines()
                if len(lines) >= 2 and lines[0] and lines[1]:
                    self._salt = lines[0]
                    self._pin_hash = lines[1]
                    return
            except OSError:
                # Fall through to re-initialization below.
                pass
        self._salt = secrets.token_hex(16)
        self._pin_hash = self._hash_pin(self.DEFAULT_PIN)
        self._save()

    def _save(self) -> None:
        """Persist the salt and current PIN hash to disk."""
        directory = os.path.dirname(self._auth_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self._auth_path, "w", encoding="utf-8") as handle:
            handle.write(f"{self._salt}\n{self._pin_hash}\n")

    def _hash_pin(self, pin: str) -> str:
        """Compute the SHA-256 hash of salt + pin.

        Args:
            pin: The clear text PIN entered by the user.

        Returns:
            The hexadecimal digest as a string.
        """
        digest = hashlib.sha256()
        digest.update(self._salt.encode("utf-8"))
        digest.update(pin.encode("utf-8"))
        return digest.hexdigest()

    @staticmethod
    def validate_pin_format(pin: Optional[str]) -> str:
        """Validate the shape of a PIN string coming from the UI.

        Args:
            pin: Raw text from the PIN entry field.

        Returns:
            The validated PIN, stripped of surrounding whitespace.

        Raises:
            ValueError: If the PIN is empty, too short, too long, or
                contains non-digit characters.
        """
        if pin is None:
            raise ValueError("PIN is required.")
        pin = pin.strip()
        if len(pin) != UserAuth.PIN_LENGTH:
            raise ValueError(
                f"PIN must be exactly {UserAuth.PIN_LENGTH} digits."
            )
        if not pin.isdigit():
            raise ValueError("PIN must contain only digits 0-9.")
        return pin

    def verify(self, pin: str) -> bool:
        """Check whether the supplied PIN matches the stored credential.

        Args:
            pin: The clear text PIN entered by the user.

        Returns:
            True when the PIN matches, False otherwise. On mismatch the
            internal failed-attempt counter is incremented; callers should
            check ``is_locked_out`` after a failure.
        """
        try:
            pin = self.validate_pin_format(pin)
        except ValueError:
            self._failed_attempts += 1
            return False

        candidate = self._hash_pin(pin)
        # secrets.compare_digest protects against timing attacks when
        # comparing two equal-length hex digests.
        if secrets.compare_digest(candidate, self._pin_hash):
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
        new_pin = self.validate_pin_format(new_pin)
        self._pin_hash = self._hash_pin(new_pin)
        self._failed_attempts = 0
        self._save()

    @property
    def failed_attempts(self) -> int:
        """Return how many consecutive wrong PINs have been entered."""
        return self._failed_attempts

    @property
    def is_locked_out(self) -> bool:
        """Return True once the maximum failed attempts have been reached."""
        return self._failed_attempts >= self.MAX_ATTEMPTS

    def reset_attempts(self) -> None:
        """Clear the failed-attempt counter, e.g. after a timed cooldown."""
        self._failed_attempts = 0
