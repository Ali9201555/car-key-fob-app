"""Application entry point for the Car Key Fob GUI.

Run with:
    python main.py

The launcher wires every model, controller, and view together and then
hands control to the Qt event loop.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from auth_controller import AuthController
from car_controller import CarController
from fob_controller import FobController
from car_manager import CarManager
from event_log import EventLog
from fob_state import FobState
from user_auth import UserAuth
from main_window import MainWindow


def main() -> int:
    """Bootstrap the app and return the Qt exit code.

    Returns:
        The integer returned by ``QApplication.exec``. 0 means clean exit.
    """
    # Model layer
    car_manager = CarManager("data/cars.csv")
    event_log = EventLog("data/events.csv")
    fob_state = FobState("data/fob_state.txt")
    auth = UserAuth("data/auth.txt")

    # Controller layer
    car_ctrl = CarController(car_manager, event_log)
    fob_ctrl = FobController(car_manager, fob_state, event_log)
    auth_ctrl = AuthController(auth)

    # View layer
    app = QApplication(sys.argv)
    app.setApplicationName("Car Key Fob")

    window = MainWindow(
        car_controller=car_ctrl,
        fob_controller=fob_ctrl,
        auth_controller=auth_ctrl,
        fob_state=fob_state,
        event_log=event_log,
    )
    window.show()

    return app.exec()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        # Surface unexpected startup failures in a dialog instead of a
        # silent stack trace so end users know what happened.
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal error", str(exc))
        raise
