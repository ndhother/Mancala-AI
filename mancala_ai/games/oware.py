"""Oware game implementation."""

from mancala_ai.games.mancala import Mancala


class Oware(Mancala):
    """Implementation of the Oware variant of Mancala."""
    
    def __init__(
        self, 
        pits=6, 
        seeds=4, 
        clockwise=False, 
        pie_rule=False, 
        grand_slam=False,
    ):
        super().__init__(pits, seeds, clockwise, pie_rule)
        
        self.grand_slam = grand_slam

    def _starvation(self, state, player):
        """Return whether the given player's pits are all empty."""
        return sum(state.board[player][:self.pits]) == 0

    def actions(self, state):
        player = state.player_turn

        if not self._starvation(state, 1 - player):  # Opponent is not starving
            return super().actions(state)
        
        actions = []

        for pit in range(self.pits):
            seeds = state.board[player][pit]

            # Only include actions where sowing will reach the opponent's side
            if pit + seeds >= self.pits:
                actions.append(pit)
        
        return actions
    
    def _should_skip_pit(self, player, action, row, col):
        return col == self.pits or row == player and col == action    # "Kroo"
    
    def _on_move_finished(self, state, player, row, col, info):
        """
        Harvest seeds if the last seed forms a group of 2 or 3 on the 
        opponent's side.
        """
        if row == player:
            return
        
        harvest = 0
        harvest_chain = 0

        chain_start = col
        
        while col >= 0:
            seeds = state.board[row][col]

            if seeds < 2 or seeds > 3:
                break

            harvest += seeds
            harvest_chain += 1
            
            col -= 1

        chain_end = col

        if harvest == sum(state.board[row][:self.pits]):
            if self.grand_slam:
                info.grand_slam = True
            else:
                harvest_chain = 0
                info.no_harvest = True
        
        if harvest_chain:
            for pit in range(chain_end + 1, chain_start + 1):
                state.board[row][pit] = 0
                info.harvest_count += 1
            
            state.board[player][self.pits] += harvest
            info.harvest_seeds = harvest

        info.starvation = self._starvation(state, player)
