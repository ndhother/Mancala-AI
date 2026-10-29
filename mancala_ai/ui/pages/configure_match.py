"""Match configuration page."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QPushButton

from mancala_ai.config.io import save_match
from mancala_ai.ui.format import BUTTON_WIDTH, SECTION_SPACING, make_buttons
from mancala_ai.ui.match_summary import MatchSummary
from mancala_ai.ui.pages.dynamic_page import DynamicPage
from mancala_ai.ui.pages.edit_object import EditObject, ObjCategory


class ConfigureMatch(DynamicPage):
    """Display and edit the current match configuration."""

    def __init__(self, config):
        super().__init__("Configure Match")
        self._config = config

        button_map = {
            "Save && Exit": self._save, 
            "Cancel": self.go_back.emit,
        }

        for button in make_buttons(button_map):
            self.main_layout.addWidget(
                button, 
                alignment=Qt.AlignmentFlag.AlignHCenter,
            )
        
        self.main_layout.addStretch()

    def _build_dynamic_content(self):
        """Build the current match configuration controls."""

        self.dynamic_layout.addWidget(MatchSummary(self._config))
        self.dynamic_layout.addSpacing(SECTION_SPACING)

        players = self._config["players"]

        for button in [
            self._obj_button(players[0], "Player 1", ObjCategory.PLAYER),
            self._obj_button(players[1], "Player 2", ObjCategory.PLAYER),
            self._switch_players_button(players),
            self._obj_button(self._config["game"], "Game", ObjCategory.GAME),
        ]:
            self.dynamic_layout.addWidget(
                button, 
                alignment=Qt.AlignmentFlag.AlignHCenter,
            )

    def _obj_button(self, obj, name, category):
        """Create a button for adding or editing a configurable object."""
        
        text = f"{"Edit" if obj["type"] else "Add"} {name}"
        
        button = QPushButton(text)
        button.setMinimumWidth(BUTTON_WIDTH)
        button.clicked.connect(
            lambda: self.next_page.emit(EditObject(obj, category, text))
        )
        return button

    def _switch_players_button(self, players):
        """Create a button for switching the configured players."""
        
        button = QPushButton("Switch Players")
        button.setMinimumWidth(BUTTON_WIDTH)

        def switch_players():
            players.reverse()
            self.refresh()

        button.clicked.connect(switch_players)
        button.setEnabled(any(p["type"] for p in players))

        return button

    def _save(self):
        """Save the match configuration and exit the page."""
        if unlimited := self._unlimited_minimax():
            if not self._confirm_unlimited(unlimited):
                return
        
        save_match(self._config)
        self.status.emit("Match configuration saved.")
        self.go_back.emit()

    def _unlimited_minimax(self):
        """Return player numbers of Minimax agents without a search limit."""
        unlimited = []

        for i, player in enumerate(self._config["players"], 1):
            if player["type"] == "MinimaxAgent":
                settings = player["settings"]

                if (
                    settings["depth_limit"] is None 
                    and settings["time_limit"] is None
                ):
                    unlimited.append(i)
        
        return unlimited

    def _confirm_unlimited(self, unlimited):
        """Confirm saving Minimax agents configured without a search limit."""
        message = QMessageBox(self)
        message.setIcon(QMessageBox.Icon.Warning)
        message.setWindowTitle("No Minimax Search Limit Set")
        
        subject = (
            "Players 1 and 2" if len(unlimited) == 2 
            else f"Player {unlimited[0]}"
        )
        message.setText(f"No Minimax search limit set for {subject}.")
        message.setInformativeText(
            "This may result in a very long search for complex game states."
        )

        save_button = message.addButton(
            "Save Anyway", QMessageBox.ButtonRole.AcceptRole
        )
        message.addButton(
            "Continue Editing", QMessageBox.ButtonRole.RejectRole
        )
        message.exec()

        return message.clickedButton() is save_button
