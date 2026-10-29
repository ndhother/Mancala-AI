"""Interactive Mancala game board widget."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget

_PIT_SIZE = (60, 60)
_STORE_SIZE = (60, 90)
_PIT_STORE_BORDER_RADIUS = 30

_TOOL_TIP_FONT_SIZE = 12
_TOOL_TIP_DURATION = 1000


class GameBoard(QWidget):
    """Display a Mancala board and handle pit selection."""

    action_selected = Signal(int)

    def __init__(self, game, player_colours):
        super().__init__()
        self._game = game

        self._grid = QGridLayout(self)
        self.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid;
                border-radius: {_PIT_STORE_BORDER_RADIUS}px;
            }}

            QPushButton:hover:enabled {{
                background-color: palette(midlight);
            }}

            QToolTip {{ 
                font-size: {_TOOL_TIP_FONT_SIZE}pt; 
            }}

            QLabel {{
                border: 2px solid;
                border-radius: {_PIT_STORE_BORDER_RADIUS}px;
            }}

            QPushButton[player="0"] {{
                color: palette(text);
                border-color: {player_colours[0]};
            }}

            QPushButton[player="1"] {{
                color: palette(text);
                border-color: {player_colours[1]};
            }}

            QLabel[player="0"] {{
                color: {player_colours[0]};
                border-color: {player_colours[0]};
            }}

            QLabel[player="1"] {{
                color: {player_colours[1]};
                border-color: {player_colours[1]};
            }}

            QPushButton[chosen="true"] {{
                border: 3px solid palette(text);
            }}

            QPushButton[relay="0"] {{
                color: {player_colours[0]};
                font: bold;
            }}

            QPushButton[relay="1"] {{
                color: {player_colours[1]};
                font: bold;
            }}
        """)

        self._pit_buttons = [[], []]

        for row in range(2):
            for col in range(game.pits):
                button = self._create_pit_button()
                self._grid.addWidget(button, row, col + 1)
                self._pit_buttons[row].append(button)

        self._left_store = self._create_store_label()
        self._right_store = self._create_store_label()

        self._grid.addWidget(self._left_store, 0, 0, 2, 1)
        self._grid.addWidget(self._right_store, 0, self._game.pits + 1, 2, 1)

    def _create_pit_button(self):
        """Create an interactive pit button."""
        button = QPushButton()
        button.setFixedSize(*_PIT_SIZE)
        button.clicked.connect(
            lambda _, b=button: self.action_selected.emit(b.property("pit"))
        )
        return button

    def _create_store_label(self):
        """Create a store display label."""
        label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        label.setFixedSize(*_STORE_SIZE)

        return label

    def refresh(self, state, actions=(), pov=0, chosen=None, relay=None):
        """Refresh the board for the current game state."""
        self._refresh_row(
            state, 
            visual_row=0,   # top row
            player=1 - pov, 
            reverse=not self._game.clockwise, 
            actions=actions, 
            chosen=chosen,
            relay=relay,
        )
        self._refresh_row(
            state, 
            visual_row=1,   # bottom row
            player=pov, 
            reverse=self._game.clockwise, 
            actions=actions, 
            chosen=chosen,
            relay=relay,
        )

    def _refresh_row(
        self, state, visual_row, player, reverse, actions, chosen, relay
    ):
        """Refresh a displayed row and its associated store."""
        pits = list(range(self._game.pits))

        if reverse:
            pits.reverse()
            store = self._left_store
        else:
            store = self._right_store

        for button, pit in zip(self._pit_buttons[visual_row], pits):
            button.setProperty("pit", pit)
            button.setProperty("player", player)
            button.setProperty("chosen", chosen == (player, pit))
            button.setProperty(
                "relay", state.player_turn if relay == (player, pit) else None
            )
            button.setText(str(state.board[player][pit]))

            self._update_style(button)

            button.setToolTip(f"Pit {self.pit_number(pit)}")
            button.setToolTipDuration(_TOOL_TIP_DURATION)

            button.setEnabled(player == state.player_turn and pit in actions)

        store.setProperty("player", player)
        store.setText(str(state.board[player][-1]))

        self._update_style(store)

    def pit_number(self, action):
        """Return the displayed pit number for an action."""
        return self._game.pits - action if self._game.clockwise else action + 1

    def _update_style(self, widget):
        """Reapply a widget's style after property changes."""
        widget.style().unpolish(widget)
        widget.style().polish(widget)
