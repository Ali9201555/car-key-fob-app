"""Dialog that lists recent fob events from the event log."""

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from models.event_log import EventLog


class HistoryView(QDialog):
    """Scrollable table of the most recent fob events."""

    def __init__(
        self,
        event_log: EventLog,
        parent: QWidget = None,
    ) -> None:
        """Build the table and populate it from the event log.

        Args:
            event_log: The EventLog to display.
            parent: Optional parent widget for modal ownership.
        """
        super().__init__(parent)
        self._log: EventLog = event_log
        self.setWindowTitle("Fob History")
        self.setMinimumSize(560, 360)

        layout = QVBoxLayout(self)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(
            ["Timestamp", "Plate", "Action", "Detail"]
        )
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        layout.addWidget(self._table)

        self._clear_button = QPushButton("Clear history")
        self._clear_button.clicked.connect(self._on_clear)
        layout.addWidget(self._clear_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        close_button = buttons.button(QDialogButtonBox.StandardButton.Close)
        if close_button is not None:
            close_button.clicked.connect(self.accept)
        layout.addWidget(buttons)

        self._populate()

    def _populate(self) -> None:
        """Refresh the table rows from the event log."""
        events = self._log.recent(limit=200)
        self._table.setRowCount(len(events))
        for row, event in enumerate(events):
            self._table.setItem(row, 0, QTableWidgetItem(event.timestamp))
            self._table.setItem(row, 1, QTableWidgetItem(event.plate))
            self._table.setItem(row, 2, QTableWidgetItem(event.action))
            self._table.setItem(row, 3, QTableWidgetItem(event.detail))

    def _on_clear(self) -> None:
        """Confirm and then wipe the event log."""
        reply = QMessageBox.question(
            self,
            "Clear history",
            "Delete every event from the fob history? This cannot be undone.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._log.clear()
        self._populate()
