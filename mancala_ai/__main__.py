"""Application entry point for Mancala AI."""

from PySide6.QtWidgets import QApplication

from mancala_ai.ui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication()

    app.setApplicationName("Mancala AI")
    app.setOrganizationName("Nimmi Dhother")

    window = MainWindow()
    window.show()

    app.exec()
