"""Widget that renders the active car with live status indicators."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPaintEvent, QPen, QBrush, QFont
from PyQt6.QtWidgets import QWidget

from car import Car


class CarStatusWidget(QWidget):
    """Cartoon car rendered with QPainter, colored by car state.

    We draw the car programmatically instead of shipping image assets so
    the project stays self-contained inside the repository. The drawing
    updates reactively to lock, trunk, engine, and panic state.
    """

    _COLOR_MAP = {
        "Black": "#111111",
        "White": "#f5f5f5",
        "Silver": "#c0c0c0",
        "Gray": "#808080",
        "Red": "#c0392b",
        "Blue": "#2d6cdf",
        "Green": "#2ecc71",
        "Yellow": "#f1c40f",
    }

    def __init__(self, parent: QWidget = None) -> None:
        """Initialize the widget with no active car.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._car = None
        self._panic_flash = False
        self.setMinimumSize(380, 220)

    def set_car(self, car: Car) -> None:
        """Change which car is currently rendered.

        Args:
            car: The new active Car, or None to clear the widget.
        """
        self._car = car
        self.update()

    def toggle_panic_flash(self) -> None:
        """Flip the alarm-flash state; called on a timer while panic is on."""
        self._panic_flash = not self._panic_flash
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Draw the current car and overlays each time the widget repaints.

        Args:
            event: The Qt paint event (unused, Qt supplies the clip).
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background wash
        painter.fillRect(self.rect(), QColor("#1a1f2b"))

        if self._car is None:
            self._draw_empty(painter)
            painter.end()
            return

        width = self.width()
        height = self.height()
        body_color = QColor(self._COLOR_MAP.get(self._car.color, "#c0c0c0"))

        # If panic is active, alternate the background between red and normal.
        if self._car.panic_active and self._panic_flash:
            painter.fillRect(self.rect(), QColor("#5b0b0b"))

        # --- Car body ---
        body_x = int(width * 0.12)
        body_y = int(height * 0.45)
        body_w = int(width * 0.76)
        body_h = int(height * 0.28)

        painter.setBrush(QBrush(body_color))
        painter.setPen(QPen(QColor("#111111"), 2))
        painter.drawRoundedRect(body_x, body_y, body_w, body_h, 14, 14)

        # Roof / cabin
        roof_x = int(width * 0.28)
        roof_y = int(height * 0.28)
        roof_w = int(width * 0.44)
        roof_h = int(height * 0.22)
        painter.drawRoundedRect(roof_x, roof_y, roof_w, roof_h, 18, 18)

        # Windows
        window_color = QColor("#8fc9ff") if not self._car.engine_running else QColor(
            "#ffd27f"
        )
        painter.setBrush(QBrush(window_color))
        painter.setPen(QPen(QColor("#0f1114"), 2))
        painter.drawRect(roof_x + 10, roof_y + 8, (roof_w // 2) - 16, roof_h - 18)
        painter.drawRect(
            roof_x + (roof_w // 2) + 6,
            roof_y + 8,
            (roof_w // 2) - 16,
            roof_h - 18,
        )

        # --- Wheels ---
        wheel_radius = int(height * 0.08)
        wheel_y = int(height * 0.7)
        painter.setBrush(QBrush(QColor("#111111")))
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawEllipse(body_x + 16, wheel_y, wheel_radius * 2, wheel_radius * 2)
        painter.drawEllipse(
            body_x + body_w - 16 - wheel_radius * 2,
            wheel_y,
            wheel_radius * 2,
            wheel_radius * 2,
        )

        # --- Headlights (bright when engine running) ---
        light_color = (
            QColor("#fff7b3") if self._car.engine_running else QColor("#caa66a")
        )
        painter.setBrush(QBrush(light_color))
        painter.setPen(QPen(QColor("#111111"), 1))
        painter.drawRect(body_x + body_w - 8, body_y + 8, 8, 12)

        # --- Trunk (rear, opens upward) ---
        if self._car.trunk_open:
            painter.setBrush(QBrush(body_color.lighter(115)))
            painter.setPen(QPen(QColor("#111111"), 2))
            painter.drawRect(body_x - 4, body_y - 30, 22, 34)

        # --- Indicator overlay (top-left) ---
        self._draw_indicators(painter)
        painter.end()

    def _draw_empty(self, painter: QPainter) -> None:
        """Render a placeholder when no car is active."""
        painter.setPen(QPen(QColor("#9aa0a6")))
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            self.rect(),
            int(Qt.AlignmentFlag.AlignCenter),
            "No car paired.\nUse Add Car to begin.",
        )

    def _draw_indicators(self, painter: QPainter) -> None:
        """Paint the lock/engine/panic status labels in the corner."""
        if self._car is None:
            return

        lines = []
        lines.append(("LOCKED" if self._car.locked else "UNLOCKED",
                      "#29cc74" if self._car.locked else "#ffb84d"))
        if self._car.trunk_open:
            lines.append(("TRUNK OPEN", "#ffb84d"))
        if self._car.engine_running:
            lines.append(("ENGINE ON", "#29cc74"))
        if self._car.panic_active:
            lines.append(("ALARM!", "#ff4d4d"))

        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)

        x = 12
        y = 22
        for text, color in lines:
            painter.setPen(QPen(QColor(color)))
            painter.drawText(x, y, text)
            y += 16

        # Fuel and odometer summary at the bottom.
        painter.setPen(QPen(QColor("#dfe3ea")))
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(
            12,
            self.height() - 12,
            f"Fuel {self._car.fuel_level:.0f}%  ·  Odo {self._car.odometer:,} mi",
        )
