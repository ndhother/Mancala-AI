"""Engine for running individual Mancala matches."""

class GameRunner:
    """Manage a single Mancala match between two players."""

    def __init__(self, game, agents, repetition_limit=3):
        self.game = game
        self.agents = agents
        self.repetition_limit = repetition_limit

        self.state = game.initial
        self.scores = None

        self.repetition = False
        self._visited = {}

        self._check_state()

    @property
    def current_player(self):
        return self.state.player_turn

    @property
    def current_agent(self):
        return self.agents[self.current_player]

    @property
    def human_turn(self):
        return self.current_agent is None

    @property
    def actions(self):
        return self.game.actions(self.state)

    @property
    def finished(self):
        return self.scores is not None

    def choose_action(self, cancel_event=None):
        """Return an action from the current AI agent."""
        if self.human_turn:
            raise RuntimeError("Current player is human.")

        return self.current_agent.choose_action(
            self.game, self.state, cancel_event=cancel_event
        )

    def play(self, action):
        """Apply an action to the current state."""
        if self.finished:
            raise RuntimeError("Game has already finished.")

        assert action in self.actions, "Illegal move."

        self.state, move_info = self.game.result(self.state, action)
        self._check_state()

        return move_info

    def _check_state(self):
        """Handle terminal states and repetition draws."""
        if self.game.terminal(self.state):
            self.state = self.game.collect_all(self.state)
            self.scores = self.game.scores(self.state)
            return

        if self.repetition_limit:
            key = self.state.key()
            
            repeats = self._visited.get(key, 0) + 1
            self._visited[key] = repeats

            if repeats >= self.repetition_limit:
                scores = self.game.scores(self.state)
                equal_split = self.game.remaining_seeds(self.state) / 2

                self.scores = (
                    scores[0] + equal_split, scores[1] + equal_split
                )
                self.repetition = True
