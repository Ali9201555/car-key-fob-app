"""The interactive virtual key fob widget with five action buttons."""

from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FobWidget(QFrame):
    """Styled frame that looks like a physical key fob.

    The widget exposes its five action buttons through simple getter
    methods. The parent MainWindow uses those getters to connect each
    button's ``clicked`` event to a controller method.
    """

    def __init__(self, parent: QWidget = None) -> None:
        """Create every button and the battery/signal indicators.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setObjectName("fobFrame")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(self._stylesheet())
        self.setMinimumWidth(220)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("KEY FOB")
        title.setObjectName("fobTitle")
        layout.addWidget(title)

        self._lock_button = self._make_button("🔒  LOCK", "#2d6cdf")
        self._unlock_button = self._make_button("🔓  UNLOCK", "#2d8f47")
        self._trunk_button = self._make_button("🧳  TRUNK", "#5e4bd5")
        self._remote_start_button = self._make_button(
            "🔥  REMOTE START", "#c98a2e"
        )
        self._panic_button = self._make_button("🚨  PANIC", "#c0392b")

        layout.addWidget(self._lock_button)
        layout.addWidget(self._unlock_button)
        layout.addWidget(self._trunk_button)
        layout.addWidget(self._remote_start_button)
        layout.addWidget(self._panic_button)

        # Battery indicator along the bottom of the fob.
        self._battery_label = QLabel("Battery")
        self._battery_label.setObjectName("fobBattery")
        layout.addWidget(self._battery_label)

        self._battery_bar = QProgressBar()
        self._battery_bar.setRange(0, 100)
        self._battery_bar.setValue(100)
        self._battery_bar.setTextVisible(True)
        layout.addWidget(self._battery_bar)

        self._signal_label = QLabel("Signal: ▮▮▮▮")
        self._signal_label.setObjectName("fobSignal")
        layout.addWidget(self._signal_label)

    # ------------------------------------------------------------------
    # Public button accessors
    # ------------------------------------------------------------------

    def get_lock_button(self) -> QPushButton:
        """Return the LOCK button so a parent can wire its click handler."""
        return self._lock_button

    def get_unlock_button(self) -> QPushButton:
        """Return the UNLOCK button."""
        return self._unlock_button

    def get_trunk_button(self) -> QPushButton:
        """Return the TRUNK button."""
        return self._trunk_button

    def get_remote_start_button(self) -> QPushButton:
        """Return the REMOTE START button."""
        return self._remote_start_button

    def get_panic_button(self) -> QPushButton:
        """Return the PANIC button."""
        return self._panic_button

    # ------------------------------------------------------------------
    # Indicator updates
    # ------------------------------------------------------------------

    def update_battery(self, percent: float) -> None:
        """Update the battery progress bar and color it by severity.

        Args:
            percent: Battery percentage, 0.0 through 100.0.
        """
        # Clamp the incoming value into the 0-100 range.
        if percent < 0:
            clamped = 0
        elif percent > 100:
            clamped = 100
        else:
            clamped = int(percent)
        self._battery_bar.setValue(clamped)

        if clamped <= 5:
            chunk_color = "#ff4d4d"
        elif clamped <= 20:
            chunk_color = "#ffb84d"
        else:
            chunk_color = "#29cc74"
        self._battery_bar.setStyleSheet(self._battery_stylesheet(chunk_color))

    def update_signal(self, bars: int) -> None:
        """Update the text rendering of the signal strength indicator.

        Args:
            bars: Integer 0-4 showing how many bars to fill in.
        """
        if bars < 0:
            bars = 0
        elif bars > 4:
            bars = 4
        filled = "▮" * bars
        empty = "▯" * (4 - bars)
        self._signal_label.setText(f"Signal: {filled}{empty}")

    def set_enabled_buttons(self, enabled: bool) -> None:
        """Enable or disable every action button at once.

        Args:
            enabled: True to enable all buttons, False to grey them out.
        """
        self._lock_button.setEnabled(enabled)
        self._unlock_button.setEnabled(enabled)
        self._trunk_button.setEnabled(enabled)
        self._remote_start_button.setEnabled(enabled)
        self._panic_button.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Style helpers
    # ------------------------------------------------------------------

    def _make_button(self, text: str, color_hex: str) -> QPushButton:
        """Create a colored action button.

        Args:
            text: Label shown on the button.
            color_hex: The accent color as a ``#rrggbb`` string.

        Returns:
            The configured QPushButton.
        """
        button = QPushButton(text)
        button.setMinimumHeight(42)
        button.setStyleSheet(self._button_stylesheet(color_hex))
        return button

    def _button_stylesheet(self, color_hex: str) -> str:
        """Return the QSS style string for one of the action buttons.

        Args:
            color_hex: The accent color.

        Returns:
            A Qt stylesheet string.
        """
        return (
            "QPushButton {"
            "  background-color: " + color_hex + ";"
            "  color: white;"
            "  font-weight: 600;"
            "  border-radius: 10px;"
            "  padding: 6px 10px;"
            "}"
            "QPushButton:pressed { background-color: #0d0d0d; }"
            "QPushButton:disabled { background-color: #444; color: #aaa; }"
        )

    def _battery_stylesheet(self, chunk_color: str) -> str:
        """Return the QSS style string for the battery progress bar.

        Args:
            chunk_color: The fill color for the bar segment.

        Returns:
            A Qt stylesheet string.
        """
        return (
            "QProgressBar {"
            "  border: 1px solid #333;"
            "  border-radius: 6px;"
            "  background: #111;"
            "  text-align: center;"
            "  color: white;"
            "}"
            "QProgressBar::chunk {"
            "  background-color: " + chunk_color + ";"
            "  border-radius: 5px;"
            "}"
        )

    def _stylesheet(self) -> str:
        """Return the Qt stylesheet for the outer fob frame."""
        return (
            "QFrame#fobFrame {"
            "  background-color: #0f1218;"
            "  border-radius: 18px;"
            "  border: 2px solid #2a2f3a;"
            "}"
            "QLabel#fobTitle {"
            "  color: #dfe3ea;"
            "  font-weight: 700;"
            "  font-size: 14px;"
            "  qproperty-alignment: AlignCenter;"
            "  letter-spacing: 2px;"
            "}"
            "QLabel#fobBattery, QLabel#fobSignal {"
            "  color: #9aa0a6;"
            "  font-size: 11px;"
            "}"
        )
