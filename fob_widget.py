"""The interactive virtual key fob widget with five action buttons."""

from PyQt6.QtCore import pyqtSignal
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

    Each button emits its own signal rather than calling the controller
    directly so the parent MainWindow can wire them up however it likes
    (e.g., requiring PIN before calling a controller method).
    """

    lock_pressed = pyqtSignal()
    unlock_pressed = pyqtSignal()
    trunk_pressed = pyqtSignal()
    panic_pressed = pyqtSignal()
    remote_start_pressed = pyqtSignal()

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

        self._lock_button.clicked.connect(self.lock_pressed.emit)
        self._unlock_button.clicked.connect(self.unlock_pressed.emit)
        self._trunk_button.clicked.connect(self.trunk_pressed.emit)
        self._remote_start_button.clicked.connect(self.remote_start_pressed.emit)
        self._panic_button.clicked.connect(self.panic_pressed.emit)

        for button in (
            self._lock_button,
            self._unlock_button,
            self._trunk_button,
            self._remote_start_button,
            self._panic_button,
        ):
            layout.addWidget(button)

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

    @staticmethod
    def _make_button(text: str, color_hex: str) -> QPushButton:
        """Create a colored action button.

        Args:
            text: Label shown on the button.
            color_hex: The accent color as a ``#rrggbb`` string.

        Returns:
            The configured QPushButton.
        """
        button = QPushButton(text)
        button.setMinimumHeight(42)
        button.setCursor(button.cursor())
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color_hex};
                color: white;
                font-weight: 600;
                border-radius: 10px;
                padding: 6px 10px;
            }}
            QPushButton:pressed {{
                background-color: #0d0d0d;
            }}
            QPushButton:disabled {{
                background-color: #444;
                color: #aaa;
            }}
            """
        )
        return button

    def update_battery(self, percent: float) -> None:
        """Update the battery progress bar and color it by severity.

        Args:
            percent: Battery percentage, 0.0 through 100.0.
        """
        clamped = max(0, min(100, int(percent)))
        self._battery_bar.setValue(clamped)
        if clamped <= 5:
            chunk_color = "#ff4d4d"
        elif clamped <= 20:
            chunk_color = "#ffb84d"
        else:
            chunk_color = "#29cc74"
        self._battery_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #333;
                border-radius: 6px;
                background: #111;
                text-align: center;
                color: white;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                border-radius: 5px;
            }}
            """
        )

    def update_signal(self, bars: int) -> None:
        """Update the text rendering of the signal strength indicator.

        Args:
            bars: Integer 0-4 showing how many bars to fill in.
        """
        bars = max(0, min(4, bars))
        filled = "▮" * bars
        empty = "▯" * (4 - bars)
        self._signal_label.setText(f"Signal: {filled}{empty}")

    def set_enabled_buttons(self, enabled: bool) -> None:
        """Enable or disable every action button at once.

        Args:
            enabled: True to enable all buttons, False to grey them out.
        """
        for button in (
            self._lock_button,
            self._unlock_button,
            self._trunk_button,
            self._remote_start_button,
            self._panic_button,
        ):
            button.setEnabled(enabled)

    @staticmethod
    def _stylesheet() -> str:
        """Return the Qt stylesheet for the outer fob frame."""
        return """
        QFrame#fobFrame {
            background-color: #0f1218;
            border-radius: 18px;
            border: 2px solid #2a2f3a;
        }
        QLabel#fobTitle {
            color: #dfe3ea;
            font-weight: 700;
            font-size: 14px;
            qproperty-alignment: AlignCenter;
            letter-spacing: 2px;
        }
        QLabel#fobBattery, QLabel#fobSignal {
            color: #9aa0a6;
            font-size: 11px;
        }
        """
