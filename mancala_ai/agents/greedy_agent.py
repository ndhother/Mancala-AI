"""Greedy agent implementation for Mancala games."""

import math

from mancala_ai.agents.agent import Agent


class GreedyAgent(Agent):
    """Mancala agent that selects moves using a greedy strategy."""

    def choose_action(self, game, state, cancel_event=None):
        """Select the action with the highest immediate score gain."""
        value = -math.inf
        move = None

        for action in game.actions(state):
            new_state, _ = game.result(state, action)
            new_value = game.scores(new_state)[state.player_turn]

            if new_value > value:
                value = new_value
                move = action
        
        return move, None
