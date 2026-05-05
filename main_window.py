"""Main application window for the Car Key Fob app."""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from auth_controller import AuthController
from car_controller import CarController
from fob_controller import FobActionResult, FobController
from event_log import EventLog
from fob_state import FobState
from add_car_dialog import AddCarDialog
from car_status_widget import CarStatusWidget
from change_pin_dialog import ChangePinDialog
from fob_widget import FobWidget
from history_view import HistoryView
from pin_dialog import PinDialog


class MainWindow(QMainWindow):
    """Top-level window that hosts the car display and the virtual fob.

    The window owns references to every controller but does not touch the
    models directly. User interaction flows: button press -> controller
    method -> FobActionResult -> status bar and refreshed widgets.
    """

    PANIC_FLASH_INTERVAL_MS: int = 400

    def __init__(
        self,
        car_controller: CarController,
        fob_controller: FobController,
        auth_controller: AuthController,
        fob_state: FobState,
        event_log: EventLog,
    ) -> None:
        """Build the UI and wire every signal to its controller method.

        Args:
            car_controller: Controller for pairing/removing/switching cars.
            fob_controller: Controller for fob button actions.
            auth_controller: Controller used for PIN prompts.
            fob_state: The fob state model, inspected for battery warnings.
            event_log: Shared EventLog for the history dialog.
        """
        super().__init__()
        self._car_ctrl: CarController = car_controller
        self._fob_ctrl: FobController = fob_controller
        self._auth_ctrl: AuthController = auth_controller
        self._fob_state: FobState = fob_state
        self._event_log = event_log

        self.setWindowTitle("Car Key Fob")
        self.resize(760, 440)

        self._build_menu()
        self._build_central_widget()
        self._build_status_bar()

        self._panic_timer = QTimer(self)
        self._panic_timer.setInterval(self.PANIC_FLASH_INTERVAL_MS)
        self._panic_timer.timeout.connect(self._on_panic_tick)

        self._refresh_car_dropdown()
        self._refresh_active_car()
        self._refresh_fob_indicators()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        """Create the File and Tools menus."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        add_action = QAction("Pair &New Car...", self)
        add_action.triggered.connect(self._on_add_car)
        file_menu.addAction(add_action)

        remove_action = QAction("&Remove Active Car", self)
        remove_action.triggered.connect(self._on_remove_car)
        file_menu.addAction(remove_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        tools_menu = menu_bar.addMenu("&Tools")
        history_action = QAction("Show &History...", self)
        history_action.triggered.connect(self._on_show_history)
        tools_menu.addAction(history_action)

        change_pin_action = QAction("Change &PIN...", self)
        change_pin_action.triggered.connect(self._on_change_pin)
        tools_menu.addAction(change_pin_action)

        replace_battery_action = QAction("Replace Fob &Battery", self)
        replace_battery_action.triggered.connect(self._on_replace_battery)
        tools_menu.addAction(replace_battery_action)

    def _build_central_widget(self) -> None:
        """Lay out the car panel on the left and the fob on the right."""
        central = QWidget(self)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(16)

        # Left column: selector and car artwork.
        left = QVBoxLayout()
        left.setSpacing(10)

        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Active car:"))
        self._car_selector = QComboBox()
        self._car_selector.currentIndexChanged.connect(self._on_car_changed)
        selector_row.addWidget(self._car_selector, stretch=1)
        self._add_car_button = QPushButton("+ Add")
        self._add_car_button.clicked.connect(self._on_add_car)
        selector_row.addWidget(self._add_car_button)
        left.addLayout(selector_row)

        self._car_status = CarStatusWidget()
        left.addWidget(self._car_status, stretch=1)

        self._car_detail_label = QLabel("No car paired.")
        self._car_detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._car_detail_label.setStyleSheet("color: #dfe3ea; font-weight: 600;")
        left.addWidget(self._car_detail_label)

        root.addLayout(left, stretch=2)

        # Right column: the virtual fob.
        self._fob = FobWidget()
        self._fob.get_lock_button().clicked.connect(self._on_lock)
        self._fob.get_unlock_button().clicked.connect(self._on_unlock)
        self._fob.get_trunk_button().clicked.connect(self._on_trunk)
        self._fob.get_panic_button().clicked.connect(self._on_panic)
        self._fob.get_remote_start_button().clicked.connect(self._on_remote_start)
        root.addWidget(self._fob, stretch=1)

        central.setStyleSheet("QWidget { background-color: #121620; color: #dfe3ea; }")

    def _build_status_bar(self) -> None:
        """Create the bottom status bar for feedback messages."""
        status = QStatusBar(self)
        self.setStatusBar(status)
        status.showMessage("Ready")

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_car_changed(self, index: int) -> None:
        """Switch the active car when the combo box selection changes.

        Args:
            index: The newly selected index. A value of -1 means the list
                is empty.
        """
        if index < 0:
            return
        plate = self._car_selector.itemData(index)
        if not plate:
            return
        try:
            self._car_ctrl.switch_active(plate)
        except KeyError as exc:
            QMessageBox.warning(self, "Switch failed", str(exc))
            return
        self._refresh_active_car()

    def _on_add_car(self) -> None:
        """Open the add-car dialog and refresh the UI on success."""
        dialog = AddCarDialog(self._car_ctrl, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self._refresh_car_dropdown()
            new_car = dialog.created_car()
            if new_car is not None:
                self._select_plate(new_car.plate)
            self._refresh_active_car()
            self._set_status(f"Paired {new_car.get_display_name()}.")

    def _on_remove_car(self) -> None:
        """Remove the active car after a confirmation prompt."""
        car = self._car_ctrl.get_active()
        if car is None:
            QMessageBox.information(
                self,
                "Nothing to remove",
                "No car is currently paired.",
            )
            return
        reply = QMessageBox.question(
            self,
            "Remove car",
            f"Remove {car.get_display_name()} from the fob?",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self._car_ctrl.remove_car(car.plate)
        except KeyError as exc:
            QMessageBox.warning(self, "Remove failed", str(exc))
            return
        self._refresh_car_dropdown()
        self._refresh_active_car()
        self._set_status(f"Removed {car.get_display_name()}.")

    def _on_show_history(self) -> None:
        """Open the history dialog."""
        dialog = HistoryView(self._event_log, self)
        dialog.exec()

    def _on_change_pin(self) -> None:
        """Open the change-PIN dialog."""
        dialog = ChangePinDialog(self._auth_ctrl, self)
        dialog.exec()

    def _on_replace_battery(self) -> None:
        """Simulate inserting a fresh coin-cell battery in the fob."""
        result = self._fob_ctrl.replace_battery()
        self._apply_result(result)
        self._refresh_fob_indicators()

    def _on_lock(self) -> None:
        """Handle the fob lock button."""
        self._apply_result(self._fob_ctrl.lock())
        self._refresh_active_car()
        self._refresh_fob_indicators()

    def _on_unlock(self) -> None:
        """Handle the fob unlock button."""
        self._apply_result(self._fob_ctrl.unlock())
        self._refresh_active_car()
        self._refresh_fob_indicators()

    def _on_trunk(self) -> None:
        """Handle the trunk toggle button."""
        self._apply_result(self._fob_ctrl.toggle_trunk())
        self._refresh_active_car()
        self._refresh_fob_indicators()

    def _on_panic(self) -> None:
        """Prompt for the PIN then toggle the panic alarm."""
        authenticated = self._prompt_pin()
        result = self._fob_ctrl.panic(authenticated=authenticated)
        self._apply_result(result)
        self._refresh_active_car()
        self._refresh_fob_indicators()
        self._update_panic_timer()

    def _on_remote_start(self) -> None:
        """Prompt for the PIN then toggle remote engine start."""
        authenticated = self._prompt_pin()
        result = self._fob_ctrl.remote_start(authenticated=authenticated)
        self._apply_result(result)
        self._refresh_active_car()
        self._refresh_fob_indicators()

    def _on_panic_tick(self) -> None:
        """Flash the car widget red while the alarm is active."""
        self._car_status.toggle_panic_flash()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _prompt_pin(self) -> bool:
        """Open the PIN dialog and return whether the owner authenticated.

        Returns:
            True on a correct PIN, False when the user cancels or enters
            the wrong PIN.
        """
        if self._auth_ctrl.is_locked_out():
            QMessageBox.critical(
                self,
                "Locked out",
                "Too many failed PIN attempts. Restart the application.",
            )
            return False
        dialog = PinDialog(self._auth_ctrl, self)
        return dialog.exec() == dialog.DialogCode.Accepted

    def _apply_result(self, result: FobActionResult) -> None:
        """Display the outcome of a fob action in the status bar.

        Args:
            result: The FobActionResult returned by a controller method.
        """
        self._set_status(result.message)
        if not result.success:
            # Use a subtle tone for information-level failures.
            self.statusBar().setStyleSheet("color: #ffb84d;")
        else:
            self.statusBar().setStyleSheet("color: #dfe3ea;")

    def _set_status(self, message: str) -> None:
        """Proxy for status-bar updates so the string is set in one place."""
        self.statusBar().showMessage(message, 6000)

    def _refresh_car_dropdown(self) -> None:
        """Repopulate the car dropdown from the controller."""
        self._car_selector.blockSignals(True)
        self._car_selector.clear()
        for car in self._car_ctrl.list_cars():
            self._car_selector.addItem(car.get_display_name(), car.plate)
        active = self._car_ctrl.get_active()
        if active is not None:
            self._select_plate(active.plate)
        self._car_selector.blockSignals(False)

    def _select_plate(self, plate: str) -> None:
        """Set the combo selection to the entry with the given plate."""
        for index in range(self._car_selector.count()):
            if self._car_selector.itemData(index) == plate:
                self._car_selector.setCurrentIndex(index)
                return

    def _refresh_active_car(self) -> None:
        """Update the car widget and caption for the active car."""
        car = self._car_ctrl.get_active()
        self._car_status.set_car(car)
        if car is None:
            self._car_detail_label.setText("No car paired.")
            self._fob.set_enabled_buttons(False)
        else:
            self._car_detail_label.setText(car.get_display_name())
            self._fob.set_enabled_buttons(True)
        self._update_panic_timer()

    def _refresh_fob_indicators(self) -> None:
        """Sync the fob battery bar and signal indicator with the model."""
        self._fob.update_battery(self._fob_state.get_battery())
        self._fob.update_signal(self._fob_state.get_signal_bars())

        if self._fob_state.is_critical_battery():
            self.statusBar().setStyleSheet("color: #ff4d4d;")
            self._set_status(
                "Fob battery critical! Replace the battery in Tools."
            )
        elif self._fob_state.is_low_battery():
            self.statusBar().setStyleSheet("color: #ffb84d;")

    def _update_panic_timer(self) -> None:
        """Start or stop the panic flash timer based on car state."""
        car = self._car_ctrl.get_active()
        if car is not None and car.panic_active:
            if not self._panic_timer.isActive():
                self._panic_timer.start()
        else:
            if self._panic_timer.isActive():
                self._panic_timer.stop()
            self._car_status.update()

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event: object) -> None:
        """Persist state one last time before the window closes.

        The method name is camelCase because Qt's parent class declares
        it that way; we override it to flush state on shutdown.
        """
        try:
            self._car_ctrl.write()
        except OSError:
            # Saving is best-effort on shutdown; we still allow close.
            pass
        super().closeEvent(event)
