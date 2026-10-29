"""Abstract base class for Mancala agents."""

from abc import ABC, abstractmethod


class Agent(ABC):
    """Define the interface implemented by Mancala agents."""
    
    @abstractmethod
    def choose_action(self, game, state, cancel_event=None):
        """Select an action from the current game state."""
