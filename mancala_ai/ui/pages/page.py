"""Base widget for application pages."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class Page(QWidget):
    """Base page with shared layout and navigation signals."""

    next_page = Signal(QWidget)
    go_back = Signal()
    status = Signal(str)

    def __init__(self, title):
        super().__init__()

        self.main_layout = QVBoxLayout(self)

        title_label = QLabel(
            f"<h2>{title}</h2>", 
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )
        self.main_layout.addStretch()
        self.main_layout.addWidget(title_label)
        self.main_layout.addStretch()

    def refresh(self):
        """Update the page before it is displayed."""
        pass
