"""Base Mancala implementation."""

from mancala_ai.games.move_info import MoveInfo
from mancala_ai.games.state import State

SWAP = -1


class Mancala:
    """Base implementation and common rules for Mancala games."""

    def __init__(self, pits, seeds, clockwise=False, pie_rule=False):
        if not pits:
            raise ValueError("Mancala requires at least 1 pit per player.")
        if not seeds:
            raise ValueError("Mancala requires at least 1 seed per pit.")

        self.pits = pits
        self.seeds = seeds
        self.clockwise = clockwise
        self.pie_rule = pie_rule

        self.initial = State(0, [[seeds] * pits + [0], [seeds] * pits + [0]])

    def actions(self, state):
        """Return the set of legal moves from a given state."""
        player = state.player_turn
        actions = [
            pit for pit in range(self.pits) if state.board[player][pit] > 0
        ]
        if self.pie_rule and player == 1 and state.turns_taken[1] == 0:
            actions.append(SWAP)
        
        return actions

    def result(self, state, action):
        """Apply the state transition model and return the resulting state."""
        if action not in self.actions(state):
            raise ValueError("Illegal move.")

        # All changes are made to a fresh copy of state
        state = state.copy()

        # Acting player recorded once and used throughout transition
        player = state.player_turn

        # Reset info before each move
        info = MoveInfo()
        
        if action == SWAP:
            state.player_turn = 0
            state.board[0], state.board[1] = state.board[1], state.board[0]
            state.turns_taken[1] += 1

            info.swap = True

            return state, info
        
        row = player
        col = action
        
        while True:
            row, col = self._sow(state, player, action, row, col)
            
            if not self._relay(state, row, col):
                break
            
            # Relay sowing...
            info.relay_count += 1
            info.relay_states.append((state.copy(), (row, col)))
        
        self._on_move_finished(state, player, row, col, info)
        self._update_turn(state, player, row, col, info)
        
        return state, info
    
    def _sow(self, state, player, action, row, col):
        """Perform one sowing phase. Return the position of the last seed."""
        seeds = self._pick_up_seeds(state, row, col)
        
        while seeds:    # Continue until all seeds are sown
            row, col = self._next_pit(row, col)
            
            if not self._should_skip_pit(player, action, row, col):
                seeds = self._drop_seeds(state, seeds, row, col)
        
        return row, col

    def _pick_up_seeds(self, state, row, col):
        """
        Remove all seeds from a given pit. Return the number of seeds found.
        """
        seeds = state.board[row][col]
        state.board[row][col] = 0

        return seeds

    def _next_pit(self, row, col):
        """Return the next position in the sowing sequence."""
        return (1 - row, 0) if col >= self.pits else (row, col + 1)

    def _should_skip_pit(self, player, action, row, col):
        """Return whether a pit should be skipped during sowing."""
        return False
        
    def _drop_seeds(self, state, seeds, row, col):
        """
        Add one seed to a given pit. Return the number of seeds yet to be sown.
        """
        state.board[row][col] += 1
        return seeds - 1
    
    def _relay(self, state, row, col):
        """Return whether a given pit triggers relay sowing."""
        return False

    def _on_move_finished(self, state, player, row, col, info):
        """Apply variant-specific rules after sowing is complete."""
        pass

    def _update_turn(self, state, player, row, col, info):
        """
        Record one turn taken by the current player and switch the turn.
        """
        state.turns_taken[player] += 1
        state.player_turn = 1 - player

    def scores(self, state):
        """Return the number of seeds in each player's store."""
        return (state.board[0][self.pits], state.board[1][self.pits])

    def terminal(self, state):
        """Return True if no further actions can be made from the state."""
        return not self.actions(state)

    def utility(self, state, player):
        """Return difference in ownership of seeds at a terminal state."""

        assert self.terminal(state), \
            "Utility function called on non-terminal state."

        return sum(state.board[player]) - sum(state.board[1 - player])

    def remaining_seeds(self, state):
        """
        Return the number of seeds on the board not stored by either player.
        """
        return sum(row[pit] for pit in range(self.pits) for row in state.board)

    def collect_all(self, state):
        """Apply endgame transition to a terminal state."""
        state = state.copy()
        
        for row in state.board:
            for pit in range(self.pits):
                seeds = row[pit]

                # Sweep all seeds into respective store
                row[pit] = 0
                row[self.pits] += seeds
        
        return state
