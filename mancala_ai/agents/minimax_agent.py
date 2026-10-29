"""Minimax search agent implementation for Mancala games."""

import math
import time
from dataclasses import dataclass

from mancala_ai.agents.agent import Agent
from mancala_ai.games.mancala import SWAP


class SearchCancelled(Exception):
    """Raised when a Minimax search is cancelled externally."""
    pass


@dataclass
class SearchReport:
    """Summary of a completed iterative-deepening search."""
    
    depth: int
    full_search: bool


class MinimaxAgent(Agent):
    """Mancala agent with configurable Minimax search and move ordering."""
    
    def __init__(
        self, 
        depth_limit=None, 
        time_limit=None, 
        pruning=False, 
        heuristic="H1", 
        move_order="A", 
    ):
        # Configuration
        self.depth_limit = depth_limit
        self.time_limit = time_limit
        self.pruning = pruning
        self.heuristic = heuristic
        self.move_order = move_order

        # Search state
        self._cancel = None
        self._search_time = None
        self._player = None
        self._i_order = {}

    def choose_action(self, game, state, cancel_event=None):
        """
        Select an action using depth-limited Minimax search or time-limited 
        iterative deepening.
        """
        self._cancel = cancel_event
        self._search_time = None
        self._player = state.player_turn
        self._i_order.clear()

        i_root = "I" in self.move_order

        actions = self._moves(game, state, i_root=i_root)
        assert actions, "Non-terminal state had no legal actions."

        search_report = None

        max_depth = self.depth_limit or math.inf

        if self.time_limit:
            self._search_time = time.perf_counter() + self.time_limit
            
            # True if subtree is fully explored without heuristic cutoff
            full_search = False
            
            move = None
            depth = 1
            
            while depth <= max_depth:
                try:
                    _, move, full_search = self._minimax(
                        game, state, depth, -math.inf, math.inf, i_root=i_root
                    )
                except TimeoutError:
                    break

                depth += 1

                if full_search:
                    break

            search_report = SearchReport(
                depth=depth - 1, full_search=full_search
            )
        
        else:
            _, move, _ = self._minimax(
                game, state, max_depth, -math.inf, math.inf, path=set()
            )

        if move is None:
            move = actions[0]   # Fallback in case of timeout before depth 1
        
        return move, search_report

    def _check_interruption(self):
        """Raise an exception if the current search should be interrupted."""
        if self._cancel and self._cancel.is_set():
            raise SearchCancelled()

        if self._search_time and time.perf_counter() > self._search_time:
            raise TimeoutError()

    def _minimax(
        self, game, state, depth, alpha, beta, path=None, i_root=False
    ):
        """
        Search the game tree using minimax with optional alpha-beta pruning.
        """
        self._check_interruption()
        
        # Final state evaluation always from root player's perspective
        
        if game.terminal(state):
            return game.utility(state, self._player), None, True

        if depth == 0:
            return self._eval(game, state, self._player), None, False
        
        # Cycle detection
        if path is not None:
            key = state.key()

            if key in path:
                return 0, None, True    # Treated as draw
            
            path.add(key)

        full_search = True
        move = None

        maximising = state.player_turn == self._player
        value = -math.inf if maximising else math.inf

        for action in self._moves(game, state, i_root=i_root):
            new_value, _, search = self._minimax(
                game, 
                game.result(state, action)[0], 
                depth - 1, 
                alpha, 
                beta, 
                path,
            )
            full_search = full_search and search

            # Store root values to guide next iteration ordering (code "I")
            if i_root:
                self._i_order[action] = new_value

            if maximising:
                if new_value > value:
                    value = new_value
                    move = action

                if self.pruning:
                    alpha = max(alpha, value)

                    if value >= beta:
                        break
            
            else:
                if new_value < value:
                    value = new_value
                    move = action
                
                if self.pruning:
                    beta = min(beta, value)

                    if value <= alpha:
                        break
        
        if path is not None:
            path.remove(key)    # Backtrack cycle detection

        return value, move, full_search

    def _eval(self, game, state, player):
        """
        Evaluate a non-terminal state from the given player's perspective.
        """
        if self.heuristic == "H1":  # Score difference
            scores = game.scores(state)
            return scores[player] - scores[1 - player]
    
        if self.heuristic == "H2":  # Greedy (asymmetric)
            return 2 * (game.scores(state)[player] - game.pits * game.seeds)
        
        if self.heuristic == "H3":  # Row hoarding
            return (
                sum(state.board[player][:-1]) 
                - sum(state.board[1 - player][:-1])
            )
        
        if self.heuristic == "H4":  # Largest pile
            return (
                max(state.board[player][:-1]) 
                - max(state.board[1 - player][:-1])
            )
        
        if self.heuristic == "H5":  # Mobility
            state1 = state.copy()
            state1.player_turn = player
            mobility = len([a for a in game.actions(state1) if a != SWAP])

            state2 = state.copy()
            state2.player_turn = 1 - player
            opp_mobility = len([a for a in game.actions(state2) if a != SWAP])

            return 2 * game.seeds * (mobility - opp_mobility)

        if self.heuristic == "H6":  # Turn advantage
            return state.turns_taken[player] - state.turns_taken[1 - player]

    def _moves(self, game, state, i_root=False):
        """Return legal moves in the configured search order."""
        
        # BASE: Ascending order (furthest from store first)
        if "A" in self.move_order:
            moves = game.actions(state)

        # BASE: Descending order (closest to store first)
        elif "D" in self.move_order:
            moves = list(reversed(game.actions(state)))

            # Keep SWAP at the end of moves list
            if SWAP in moves:
                moves.remove(SWAP)
                moves.append(SWAP)
        
        codes = [
            c for c in self.move_order 
            if c not in "AD" and (c != "I" or i_root)
        ]

        if not codes:
            return moves
        
        # Only compute result if required by ordering heuristics
        call_result = any(c in codes for c in "HXCRV")

        def priority(move):
            key = []
            
            if call_result:
                new_state, info = game.result(state, move)
            
            for code in codes:

                # Least to most seeds
                if code == "L":
                    key.append(
                        -state.board[state.player_turn][move] if move != SWAP 
                        else -math.inf
                    )
                
                # Most to least seeds
                elif code == "M":
                    key.append(
                        state.board[state.player_turn][move] if move != SWAP 
                        else -math.inf
                    )

                # Iterative deepening ranking
                elif code == "I" and i_root:
                    key.append(self._i_order.get(move, -math.inf))
                
                # Heuristic evaluation - from moving player's perspective
                elif code == "H":
                    key.append(self._eval(game, new_state, state.player_turn))
                
                # Prioritise extra turns
                elif code == "X":
                    key.append(info.extra_turn)
                
                # Prioritise captures
                elif code == "C":
                    key.append(info.capture)
                
                # Prioritise relay chains
                elif code == "R":
                    key.append(info.relay_count)
                
                # Prioritise harvest chains
                elif code == "V":
                    key.append(info.harvest_count)
            
            return key

        return sorted(moves, key=priority, reverse=True)
