"""Controller for the fob button actions (lock, unlock, trunk, panic, etc.)."""

from models.car_manager import CarManager
from models.event_log import EventLog
from models.fob_state import FobState


class FobActionResult:
    """Outcome of a single fob action, suitable for display in the UI."""

    def __init__(
        self,
        success: bool,
        message: str,
        chirp: bool = False,
        horn: bool = False,
    ) -> None:
        """Build a fob action result.

        Args:
            success: True when the action was accepted and applied.
            message: Human-readable message to show in the status bar.
            chirp: True when the UI should play the lock/unlock chirp.
            horn: True when the UI should play the panic horn sound.
        """
        self.success = success
        self.message = message
        self.chirp = chirp
        self.horn = horn


class FobController:
    """Translates button presses into car/fob state mutations and log entries.

    Every public method returns a FobActionResult so the view can
    surface a uniform success or failure message to the user without
    inspecting the underlying model state.
    """

    def __init__(
        self,
        car_manager: CarManager,
        fob_state: FobState,
        event_log: EventLog,
    ) -> None:
        """Wire the controller to its shared models.

        Args:
            car_manager: The CarManager holding the active car.
            fob_state: The FobState model tracking battery and signal.
            event_log: The EventLog that records every button press.
        """
        self._manager = car_manager
        self._fob = fob_state
        self._log = event_log

    def _preflight(self):
        """Check conditions that would block any action.

        Returns:
            A failure FobActionResult when the fob cannot transmit, or
            None when the caller may proceed.
        """
        if self._manager.count() == 0:
            return FobActionResult(
                success=False,
                message="No cars paired. Add a car before using the fob.",
            )
        if self._fob.is_dead:
            return FobActionResult(
                success=False,
                message="Fob battery is dead. Replace the battery first.",
            )
        return None

    def _commit(self, action: str, detail: str) -> None:
        """Save state, charge battery cost, and log the event.

        Args:
            action: The uppercase action label.
            detail: Descriptive text for the history view.
        """
        self._fob.apply_action(action)
        self._manager.save()
        active = self._manager.get_active()
        plate = active.plate if active is not None else ""
        self._log.record(plate=plate, action=action, detail=detail)

    def lock(self) -> FobActionResult:
        """Lock all doors and close the trunk.

        Returns:
            A FobActionResult reporting the outcome.
        """
        blocked = self._preflight()
        if blocked is not None:
            return blocked

        car = self._manager.get_active()
        if car.locked and not car.trunk_open:
            return FobActionResult(
                success=False,
                message=f"{car.display_name} is already locked.",
            )

        car.locked = True
        car.trunk_open = False
        self._commit("LOCK", f"Locked {car.display_name}")
        return FobActionResult(
            success=True,
            message=f"Locked {car.display_name}.",
            chirp=True,
        )

    def unlock(self) -> FobActionResult:
        """Unlock all doors.

        Returns:
            A FobActionResult reporting the outcome.
        """
        blocked = self._preflight()
        if blocked is not None:
            return blocked

        car = self._manager.get_active()
        if not car.locked:
            return FobActionResult(
                success=False,
                message=f"{car.display_name} is already unlocked.",
            )

        car.locked = False
        self._commit("UNLOCK", f"Unlocked {car.display_name}")
        return FobActionResult(
            success=True,
            message=f"Unlocked {car.display_name}.",
            chirp=True,
        )

    def toggle_trunk(self) -> FobActionResult:
        """Open or close the trunk.

        Returns:
            A FobActionResult reporting the new trunk state.
        """
        blocked = self._preflight()
        if blocked is not None:
            return blocked

        car = self._manager.get_active()
        car.trunk_open = not car.trunk_open
        # Opening the trunk auto-unlocks the car to match real behavior.
        if car.trunk_open:
            car.locked = False
        state_text = "opened" if car.trunk_open else "closed"
        self._commit("TRUNK", f"Trunk {state_text} on {car.display_name}")
        return FobActionResult(
            success=True,
            message=f"Trunk {state_text}.",
            chirp=True,
        )

    def panic(self, authenticated: bool) -> FobActionResult:
        """Toggle the panic alarm on the active car.

        Args:
            authenticated: True when the caller has already verified the
                owner's PIN. The panic button is PIN-protected to match
                real fobs that require a long-press.

        Returns:
            A FobActionResult reporting whether the alarm was started or
            silenced.
        """
        if not authenticated:
            return FobActionResult(
                success=False,
                message="PIN required to trigger the panic alarm.",
            )

        blocked = self._preflight()
        if blocked is not None:
            return blocked

        car = self._manager.get_active()
        car.panic_active = not car.panic_active
        state_text = "started" if car.panic_active else "silenced"
        self._commit(
            "PANIC",
            f"Panic alarm {state_text} on {car.display_name}",
        )
        return FobActionResult(
            success=True,
            message=f"Panic alarm {state_text}.",
            horn=car.panic_active,
        )

    def remote_start(self, authenticated: bool) -> FobActionResult:
        """Start or stop the engine remotely.

        Args:
            authenticated: True when the caller has verified the owner
                PIN. Remote start is PIN-protected because it leaves the
                car running while unattended.

        Returns:
            A FobActionResult reporting whether the engine was started
            or stopped.
        """
        if not authenticated:
            return FobActionResult(
                success=False,
                message="PIN required to remote start.",
            )

        blocked = self._preflight()
        if blocked is not None:
            return blocked

        car = self._manager.get_active()
        if not car.engine_running and car.fuel_level < 5.0:
            return FobActionResult(
                success=False,
                message="Not enough fuel to remote start.",
            )

        car.engine_running = not car.engine_running
        action = "REMOTE_START" if car.engine_running else "REMOTE_STOP"
        state_text = "started" if car.engine_running else "stopped"
        self._commit(action, f"Engine {state_text} on {car.display_name}")
        return FobActionResult(
            success=True,
            message=f"Engine {state_text}.",
            chirp=True,
        )

    def replace_battery(self) -> FobActionResult:
        """Simulate installing a new coin cell in the fob.

        Returns:
            A success FobActionResult showing a confirmation message.
        """
        self._fob.replace_battery()
        self._log.record(
            plate="",
            action="BATTERY",
            detail="Fob battery replaced",
        )
        return FobActionResult(
            success=True,
            message="Fob battery replaced. 100% charge.",
        )
