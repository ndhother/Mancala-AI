"""Kalah game implementation."""

from mancala_ai.games.mancala import Mancala


class Kalah(Mancala):
    """Implementation of the Kalah variant of Mancala."""

    def __init__(
        self, 
        pits=6, 
        seeds=4, 
        clockwise=False, 
        pie_rule=False, 
        sow_to_opp_store=False,
    ):
        super().__init__(pits, seeds, clockwise, pie_rule)
        
        self.sow_to_opp_store = sow_to_opp_store

    def _should_skip_pit(self, player, _, row, col):
        return (
            not self.sow_to_opp_store 
            and row == 1 - player 
            and col == self.pits
        )
        
    def _on_move_finished(self, state, player, row, col, info):
        """
        Capture seeds from the opposite pit if the last seed lands in a 
        player's own empty pit.
        """
        if row == player and col < self.pits and state.board[row][col] == 1:

            # Identify opposite pit by counting down from end of row
            opp_pit = self.pits - 1 - col
            
            if seeds := state.board[1 - player][opp_pit]:
                state.board[row][col] = 0
                state.board[1 - player][opp_pit] = 0
                state.board[row][self.pits] += seeds + 1
                
                info.capture = True
                info.capture_seeds = seeds
        
    def _update_turn(self, state, player, row, col, info):
        """Award an extra turn if the last seed lands in the player's store."""
        if row != player or col < self.pits or self.terminal(state):
            return super()._update_turn(state, player, row, col, info)
        
        state.turns_taken[player] += 1
        info.extra_turn = True

    def terminal(self, state):
        """Return whether all pits on either player's side are empty."""
        return any(sum(row[:self.pits]) == 0 for row in state.board)
