"""Main menu page for application navigation."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from mancala_ai.config.builder import IncompleteConfigError
from mancala_ai.config.io import CorruptedFileError, FileTarget, reset_file
from mancala_ai.config.validation import CorruptedDataError

from mancala_ai.ui.format import make_buttons
from mancala_ai.ui.pages.configure_match import ConfigureMatch
from mancala_ai.ui.pages.page import Page
from mancala_ai.ui.pages.play_match import PlayMatch
from mancala_ai.ui.pages.user_settings import UserSettings

from mancala_ai.prepare import prepare_match, prepare_play, prepare_user


_TARGET_NAMES = {
    FileTarget.MATCH: "Match configuration", 
    FileTarget.USER: "User settings",
}


class MainMenu(Page):
    """Provide the application's main navigation menu."""

    def __init__(self):
        super().__init__("Mancala AI")

        button_map = {
            "Play Match": self._play_match,
            "Configure Match": self._configure_match,
            "User Settings": self._user_settings,
            "Quit": self.go_back.emit,
        }
        
        for button in make_buttons(button_map):
            self.main_layout.addWidget(
                button, 
                alignment=Qt.AlignmentFlag.AlignHCenter,
            )

        self.main_layout.addStretch()

    def _play_match(self):
        """Prepare and open a match."""
        try:
            play = prepare_play()

        except (CorruptedFileError, CorruptedDataError) as e:
            self._handle_corrupt_data(e)
            return

        except IncompleteConfigError as e:
            QMessageBox.warning(self, "Incomplete Configuration", str(e))
            return

        self.next_page.emit(PlayMatch(*play))

    def _configure_match(self):
        """Load and open the match configuration."""
        try:
            config = prepare_match()

        except (CorruptedFileError, CorruptedDataError) as e:
            self._handle_corrupt_data(e)
            return

        self.next_page.emit(ConfigureMatch(config))

    def _user_settings(self):
        """Load and open the user settings."""
        try:
            settings = prepare_user()

        except (CorruptedFileError, CorruptedDataError) as e:
            self._handle_corrupt_data(e)
            return

        self.next_page.emit(UserSettings(settings))

    def _handle_corrupt_data(self, e):
        """Prompt the user to reset corrupted configuration data."""
        name = _TARGET_NAMES[e.target]

        if isinstance(e, CorruptedFileError):
            message = f"{name} could not be read."
        else:
            message = f"{name} contains corrupted data:\n\n{e}"

        message += "\n\nReset data?"
       
        answer = QMessageBox.question(
            self,
            "Corrupted Data",
            message,
            buttons=QMessageBox.Reset | QMessageBox.Cancel,
        )
        
        if answer == QMessageBox.Reset:
            reset_file(e.target)
            QMessageBox.information(self, "Data Reset", f"{name} reset.")
