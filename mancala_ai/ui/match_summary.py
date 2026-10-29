"""Match configuration summary widget."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from mancala_ai.config.registry import GAMES, PLAYERS
from mancala_ai.ui.format import BOOL_TEXT, SECTION_SPACING, bool_colours


class MatchSummary(QWidget):
    """Display a summary of a configured match."""

    def __init__(self, config):
        super().__init__()
        self._config = config

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(
            self._player_summary(), alignment=Qt.AlignmentFlag.AlignHCenter
        )
        layout.addSpacing(SECTION_SPACING)

        game_summary, rules = self._game_summary()

        layout.addWidget(game_summary, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(rules)

    def _player_summary(self):
        """Build the player configuration summary."""
        players = [
            f"Player {i}: {self._format_player_name(p)}" 
            for i, p in enumerate(self._config["players"], 1)
        ]
        return QLabel("\n".join(players))

    def _format_player_name(self, player):
        """Format a configured player's display name."""
        p_type = player["type"]
        settings = player["settings"]

        name = PLAYERS[p_type]["name"] if p_type else ""

        if p_type == "RandomAgent":
            seed = settings["seed"]

            if seed is not None:
                name += f" ({seed})"

        elif p_type == "MinimaxAgent":
            name = f"Minimax ({settings["heuristic"]}"
            
            if settings["pruning"]:
                name = f"AB-{name}"
            
            if depth_limit := settings["depth_limit"]:
                name += f", depth {depth_limit}"
            
            if time_limit := settings["time_limit"]:
                name += f", time {time_limit}s" 
            
            name += f", {settings["move_order"]})"
        
        return name

    def _game_summary(self):
        """Build the game configuration and rules summary."""
        game = self._config["game"]

        summary = "Game: "
        rules = []
        
        if game_type := game["type"]:
            settings = game["settings"]

            summary += f"{game_type}({settings["pits"]}, {settings["seeds"]})"
            summary += " - " + (
                "Clockwise" if settings["clockwise"] else "Counter-Clockwise"
            )
            for key, setting in GAMES[game_type]["settings"].items():
                if setting.get("rule", False):
                    rules.append(
                        f"• {setting["name"]}: \
                            {self._format_bool(settings[key])}"
                    )
        
        return QLabel(summary), QLabel("<br>".join(rules))

    def _format_bool(self, state):
        """Format a boolean value for display in the summary."""
        return (
            f"<font color='{bool_colours()[state]}'>{BOOL_TEXT[state]}</font>"
        )
