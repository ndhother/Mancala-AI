"""Congkak game implementation."""

from mancala_ai.games.mancala import Mancala


class Congkak(Mancala):
    """Implementation of the Congkak variant of Mancala."""

    def __init__(
        self, 
        pits=7, 
        seeds=7, 
        clockwise=True, 
        pie_rule=False, 
        solo_capture=True, 
        restrict_first_moves=False,
    ):
        super().__init__(pits, seeds, clockwise, pie_rule)
        
        self.solo_capture = solo_capture
        self.restrict_first_moves = restrict_first_moves
    
    def _restricted(self, state):
        """Return whether the effects of the current move are restricted."""
        return self.restrict_first_moves and 0 in state.turns_taken

    def _should_skip_pit(self, player, _, row, col):
        # Skip over opponent's store
        return row == 1 - player and col == self.pits

    def _relay(self, state, row, col):
        # Non-empty pit continues sow phase
        return (
            col < self.pits 
            and state.board[row][col] > 1 
            and not self._restricted(state)
        )

    def _on_move_finished(self, state, player, row, col, info):
        """
        Capture seeds from the opposite pit if the last seed lands in an 
        eligible empty pit.
        """
        if (
            row == player 
            and col < self.pits 
            and state.board[row][col] == 1 
            and not self._restricted(state)
        ):
            # Identify opposite pit by counting down from end of row
            opp_pit = self.pits - 1 - col
            
            seeds = state.board[1 - player][opp_pit]
            
            if seeds or self.solo_capture:
                state.board[row][col] = 0
                state.board[1 - player][opp_pit] = 0
                state.board[row][self.pits] += seeds + 1
                
                info.capture = True
                info.capture_seeds = seeds

    def _update_turn(self, state, player, _, col, info):
        """Award an extra turn if the last seed lands in the player's store."""
        if col < self.pits or self.terminal(state) or self._restricted(state):
            return super()._update_turn(state, player, _, col, info)
        
        state.turns_taken[player] += 1
        info.extra_turn = True

    def terminal(self, state):
        """Return whether all pits on either player's side are empty."""
        return any(sum(row[:self.pits]) == 0 for row in state.board)
