"""Application entry point for the Car Key Fob GUI.

Run with:
    python main.py

The launcher wires every model, controller, and view together and then
hands control to the Qt event loop.
"""

import os
import sys
import traceback

from PyQt6.QtWidgets import QApplication, QMessageBox

from auth_controller import AuthController
from car_controller import CarController
from fob_controller import FobController
from car_manager import CarManager
from event_log import EventLog
from fob_state import FobState
from user_auth import UserAuth
from main_window import MainWindow


def _data_dir() -> str:
    """Return the absolute path to the ``data`` directory beside main.py.

    The directory is created on first run if it does not already exist.

    Returns:
        Absolute path to the data directory.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(here, "data")
    os.makedirs(data, exist_ok=True)
    return data


def main() -> int:
    """Bootstrap the app and return the Qt exit code.

    Returns:
        The integer returned by ``QApplication.exec``. 0 means clean exit.
    """
    data = _data_dir()

    # Model layer ------------------------------------------------------
    car_manager = CarManager(os.path.join(data, "cars.csv"))
    event_log = EventLog(os.path.join(data, "events.csv"))
    fob_state = FobState(os.path.join(data, "fob_state.txt"))
    auth = UserAuth(os.path.join(data, "auth.txt"))

    # Controller layer -------------------------------------------------
    car_ctrl = CarController(car_manager, event_log)
    fob_ctrl = FobController(car_manager, fob_state, event_log)
    auth_ctrl = AuthController(auth)

    # View layer -------------------------------------------------------
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
    except Exception:  # noqa: BLE001 - crash handler for top-level failures
        # Surface unexpected startup failures in a dialog instead of a
        # silent stack trace so end users know what happened.
        message = traceback.format_exc()
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal error", message)
        raise
