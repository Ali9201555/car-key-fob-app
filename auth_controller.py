"""Controller wrapping PIN authentication for the UI layer."""

from user_auth import UserAuth


class AuthController:
    """Mediates between the PIN dialog view and the UserAuth model.

    Keeping this logic out of the view makes it easy to change the
    authentication scheme later (e.g. biometrics) without touching GUI code.
    """

    def __init__(self, auth_model: UserAuth) -> None:
        """Store a reference to the UserAuth model.

        Args:
            auth_model: The configured UserAuth instance.
        """
        self._auth: UserAuth = auth_model

    def attempt_login(self, pin: str) -> bool:
        """Verify a PIN entered in the login dialog.

        Args:
            pin: Raw PIN text from the dialog field.

        Returns:
            True when the PIN matches, False on any failure.
        """
        return self._auth.verify(pin)

    def change_pin(self, old_pin: str, new_pin: str, confirm_pin: str) -> str:
        """Change the PIN after validating every field from the dialog.

        Args:
            old_pin: The currently valid PIN.
            new_pin: The desired new PIN.
            confirm_pin: Repeat of the new PIN to catch typos.

        Returns:
            A human-readable success message for the status bar.

        Raises:
            ValueError: If any field is empty, malformed, or if the new
                and confirmation PINs do not match.
            PermissionError: If the old PIN is incorrect.
        """
        if new_pin != confirm_pin:
            raise ValueError("New PIN and confirmation do not match.")
        # Let the model perform its own format validation and raise.
        self._auth.change_pin(old_pin, new_pin)
        return "PIN updated successfully."

    def remaining_attempts(self) -> int:
        """Return how many PIN attempts are left before the lockout kicks in."""
        return max(0, UserAuth.MAX_ATTEMPTS - self._auth.failed_attempts)

    def is_locked_out(self) -> bool:
        """True when the auth model has hit the failed-attempt cap."""
        return self._auth.is_locked_out

    def reset_attempts(self) -> None:
        """Clear the failed attempt counter after a lockout cooldown."""
        self._auth.reset_attempts()
