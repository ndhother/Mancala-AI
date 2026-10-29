"""Main application window and page navigation."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QMainWindow, QStackedWidget

from mancala_ai.ui.pages.main_menu import MainMenu


_MIN_WINDOW_SIZE = (700, 700)
_FONT_SIZE = 15


class MainWindow(QMainWindow):
    """Manage the application window, page navigation, and status messages."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mancala AI")

        self.resize(*_MIN_WINDOW_SIZE)
        self.setMinimumSize(*_MIN_WINDOW_SIZE)

        self.setStyleSheet(f"font: {_FONT_SIZE}px;")

        self._status_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("color: palette(text)")
        
        self.statusBar().addWidget(self._status_label, 1)

        self._page_history = []
        
        self._stacked_widget = QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        self.navigate_to(MainMenu())

    def navigate_to(self, page):
        """Add and navigate to a new page."""

        # Connect the page's signals to the Main Window's slots
        page.next_page.connect(self.navigate_to)
        page.go_back.connect(self.navigate_back)
        page.status.connect(self.show_status)

        self._page_history.append(page)
        self._stacked_widget.addWidget(page)

        self._show_page(page)

    def navigate_back(self):
        """Remove the current page and show the previous page."""
        page = self._page_history.pop()

        if self._page_history:
            self._stacked_widget.removeWidget(page)
            page.deleteLater()

            self._show_page(self._page_history[-1])

        else:
            self.close()    # Quit app

    def _show_page(self, page):
        """Refresh and display a page."""
        page.refresh()
        self._stacked_widget.setCurrentWidget(page)

    def show_status(self, message):
        """Display a temporary status message."""
        self._status_label.setText(message)
        QTimer.singleShot(2500, self._status_label.clear)
