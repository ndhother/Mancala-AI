"""Random agent implementation for Mancala games."""

import random

from mancala_ai.agents.agent import Agent


class RandomAgent(Agent):
    """Mancala agent that selects randomly from the available moves."""

    def __init__(self, seed=None):
        self._rng = random.Random(seed)   # Independent RNG for reproducibility

    def choose_action(self, game, state, cancel_event=None):
        """Select a random legal action."""
        moves = game.actions(state)
        return (self._rng.choice(moves) if moves else None), None
