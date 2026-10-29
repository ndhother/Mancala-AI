"""Interactive match page."""

from threading import Event

from PySide6.QtCore import Qt, QThreadPool, QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea

from mancala_ai.games.mancala import SWAP
from mancala_ai.ui.agent_worker import AgentWorker
from mancala_ai.ui.format import BUTTON_WIDTH, player_colours
from mancala_ai.ui.game_board import GameBoard
from mancala_ai.ui.pages.page import Page


_POV_MAP = {
    (True, True): -1, 
    (True, False): 0, 
    (False, True): 1, 
    (False, False): 0,
}

_MOVE_DELAY = 1250
_THINKING_DELAY = 500


class PlayMatch(Page):
    """Run and display an interactive Mancala match."""

    def __init__(self, runner, settings):
        super().__init__("Play Match")
        
        self._runner = runner
        self._skip_relay = settings["skip_relay"]

        human_players = (
            self._runner.agents[0] is None, self._runner.agents[1] is None
        )
        self._pov = _POV_MAP[human_players]
        
        human_game = any(human_players)
        
        self._step_mode = settings["step_mode"] and not human_game
        self._move_delay = (
            _MOVE_DELAY if human_game else settings["playback_delay"] * 1000
        )

        self._active = True
        self._agent_thinking = False
        self._thread_pool = QThreadPool(self)
        self._cancel_event = None

        self._turn_label = QLabel(alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self._turn_label)

        self.main_layout.addStretch()

        self._board = GameBoard(runner.game, player_colours())
        self._board.action_selected.connect(self._human_move)

        self._board_area = QScrollArea(alignment=Qt.AlignmentFlag.AlignCenter)
        self._board_area.viewport().setStyleSheet("background: transparent;")
        
        self._board_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._board_area.setFixedHeight(self._board.sizeHint().height())
        
        self._board_area.setWidget(self._board)
        self.main_layout.addWidget(self._board_area)

        self.main_layout.addStretch()

        self._swap_button = QPushButton("Swap Sides")
        self._swap_button.setMinimumWidth(BUTTON_WIDTH)
        self._swap_button.clicked.connect(lambda: self._human_move(SWAP))

        self.main_layout.addWidget(
            self._swap_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.main_layout.addStretch()

        self._search_label = QLabel(alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self._search_label)

        self._move_label = QLabel(alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self._move_label)

        self.main_layout.addStretch()

        self._effect_label = QLabel(alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addWidget(self._effect_label)

        self.main_layout.addStretch()

        self._next_button = QPushButton("Next Move")
        self._next_button.setMinimumWidth(BUTTON_WIDTH)
        self._next_button.clicked.connect(self._next_move)
        
        self.main_layout.addWidget(
            self._next_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.main_layout.addStretch()

        if not self._step_mode:
            self._next_button.hide()

        quit_button = QPushButton("Quit")
        quit_button.setMinimumWidth(BUTTON_WIDTH)
        quit_button.clicked.connect(self._quit_game)
        
        self.main_layout.addWidget(
            quit_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.main_layout.addStretch()

        self._last_move = None
        self._continue_game()

    def refresh(self, update_turn=True):
        """Refresh the displayed match state."""
        actions = self._runner.actions if self._runner.human_turn else []
        player = self._runner.current_player

        if update_turn:
            self._show_turn(player)
        
        self._board.refresh(
            self._runner.state, 
            actions, 
            pov=player if self._pov == -1 else self._pov,
            chosen=self._last_move,
        )
        self._swap_button.setVisible(SWAP in actions)

    def _continue_game(self):
        """Refresh the display and continue the match."""
        self.refresh(update_turn=not self._step_mode)

        if self._step_mode:
            if self._runner.finished:
                self._next_button.setText("Match Results")
            
            self._next_button.show()

        elif self._runner.finished:
            self._pause_before(self._finish_game)

        elif not self._runner.human_turn:
            self._pause_before(self._agent_move)

    def _pause_before(self, callback, msec=None):
        """Schedule a callback after a UI transition delay."""
        QTimer.singleShot(
            msec if msec is not None else self._move_delay, 
            lambda: callback() if self._active else None,
        )

    def _next_move(self):
        """Advance a step-mode match."""
        self._show_turn(self._runner.current_player)
        self._next_button.hide()

        if self._runner.finished:
            self._finish_game()
        else:
            self._agent_move()

    def _show_turn(self, player):
        """Display the current player's turn."""
        self._turn_label.setStyleSheet(f"color: {player_colours()[player]};")
        self._turn_label.setText(f"Player {player + 1}'s Turn:")

    def _agent_move(self):
        """Start the current agent's move."""
        self._agent_thinking = True
        self._cancel_event = Event()

        worker = AgentWorker(self._runner, self._cancel_event)
        worker.signal.result.connect(self._agent_move_ready)

        self._pause_before(self._show_thinking, msec=_THINKING_DELAY)
        self._thread_pool.start(worker)

    def _show_thinking(self):
        """Display the agent thinking indicator."""
        if self._agent_thinking:
            self._effect_label.setStyleSheet(
                f"color: {player_colours()[self._runner.current_player]};"
            )
            self._effect_label.setText("Thinking...")

    def _agent_move_ready(self, action, report):
        """Process the result returned by an agent worker."""
        self._agent_thinking = False

        if self._active:
            self._process_move(action, report)

    def _human_move(self, action):
        """Play an action selected by a human player."""
        if self._runner.human_turn:
            self._process_move(action)

    def _process_move(self, action, report=None):
        """Play an action and display its result."""

        player = self._runner.current_player
        move_info = self._runner.play(action)

        if move_info.swap:
            self._search_label.setText("")
            self._move_label.setText("Player 2 chose to swap sides!")
            self._effect_label.setText("")

            self._last_move = None
            self._continue_game()
            return

        self._show_search_report(report)

        self._move_label.setText(
            f"Player {player + 1} chose pit {self._board.pit_number(action)}"
        )
        self._effect_label.setStyleSheet(f"color: {player_colours()[player]};")

        self._last_move = (player, action)

        if not self._skip_relay and move_info.relay_states:
            self._show_relay(move_info, player)
        else:
            self._show_move_effects(move_info, player)

    def _show_search_report(self, report):
        """Display an agent's search result."""
        if report is None:
            text = ""

        elif report.full_search:
            text = f"Searched to bottom of game tree (depth {report.depth})"
        
        else:
            text = f"Reached search depth {report.depth}"
            
        self._search_label.setText(text)

    def _show_relay(self, move_info, player, index=0):
        """Display the states of a relay sequence."""
        
        state, pos = move_info.relay_states[index]
        self._board.refresh(
            state, 
            pov=player if self._pov == -1 else self._pov, 
            chosen=self._last_move,
            relay=pos,
        )

        index += 1

        self._effect_label.setText(self._format_event("Relay!", index))

        if index < len(move_info.relay_states):
            self._pause_before(
                lambda: self._show_relay(move_info, player, index), 
                msec=_MOVE_DELAY,
            )
        else:
            self._pause_before(
                lambda: self._show_move_effects(move_info, player)
            )

    def _format_event(self, event, count):
        """Format a move event with its repetition count."""
        return f"{event} x{count}" if count > 1 else event

    def _show_move_effects(self, move_info, player):
        """Display the effects produced by a move."""
        effects = []
        
        if move_info.relay_count:
            effects.append(self._format_event("Relay!", move_info.relay_count))

        if move_info.extra_turn:
            effects.append("Extra turn!")

        elif move_info.capture:
            effects.append(f"Capture! ({move_info.capture_seeds} + 1)")

        if move_info.grand_slam:
            effects.append("GRAND SLAM!")

        if move_info.harvest_count:
            event = self._format_event("Harvest!", move_info.harvest_count)
            effects.append(f"{event} ({move_info.harvest_seeds})")

        elif move_info.no_harvest:
            effects.append("No harvest... (Grand Slam not allowed)")

        if move_info.starvation:
            effects.append(f"Player {player + 1} is starving!")

        self._effect_label.setText("\n\n".join(effects))
        
        self._continue_game()

    def _finish_game(self):
        """Display the final match result."""
        self._turn_label.setText("")

        text = "Game over!"

        if self._runner.repetition:
            text += " (Repetition limit reached)"
        
        self._move_label.setText(text)

        if self._runner.scores[0] > self._runner.scores[1]:
            self._effect_label.setText("Player 1 wins!")
            colour = player_colours()[0]

        elif self._runner.scores[1] > self._runner.scores[0]:
            self._effect_label.setText("Player 2 wins!")
            colour = player_colours()[1]

        else:
            self._effect_label.setText("It's a draw!")
            colour = None

        self._effect_label.setStyleSheet(f"""
            color: {colour or "palette(text)"}; 
            font-weight: bold;
        """)

    def _quit_game(self):
        """Cancel active work and exit the match."""
        self._active = False

        if self._cancel_event:
            self._cancel_event.set()
        
        self.go_back.emit()
