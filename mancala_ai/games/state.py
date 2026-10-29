"""Representation of a Mancala game state."""


class State:
    """Represent the board and turn state of a Mancala game."""

    def __init__(self, player_turn, board, turns_taken=None):
        self.player_turn = player_turn
        self.board = board
        self.turns_taken = [0, 0] if turns_taken is None else turns_taken

    def copy(self):
        """Return a deep copy of the state."""
        return State(
            self.player_turn, 
            [row[:] for row in self.board], 
            self.turns_taken[:],
        )

    def key(self):
        """Return a hashable board representation."""
        return (self.player_turn, tuple(tuple(row) for row in self.board))
