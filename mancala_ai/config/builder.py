"""Build game, agent, and match objects from valid configurations."""

from mancala_ai.agents.greedy_agent import GreedyAgent
from mancala_ai.agents.minimax_agent import MinimaxAgent
from mancala_ai.agents.random_agent import RandomAgent
from mancala_ai.config.registry import HUMAN_PLAYER
from mancala_ai.engine.game_runner import GameRunner
from mancala_ai.games.congkak import Congkak
from mancala_ai.games.kalah import Kalah
from mancala_ai.games.oware import Oware

_GAME_CLS = {game.__name__: game for game in (Kalah, Oware, Congkak)}

_AGENT_CLS = {
    agent.__name__: agent 
    for agent in (RandomAgent, GreedyAgent, MinimaxAgent)
}


class IncompleteConfigError(Exception):
    """Raised when a required configuration component is missing."""
    pass


def build_match(config, user_settings):
    """Build a game runner from a match configuration and user settings."""
    
    game_config = config["game"]
    player_configs = config["players"]

    game_type = game_config["type"]
    player_types = [p["type"] for p in player_configs]

    if game_type is None and all(p_type is None for p_type in player_types):
        raise IncompleteConfigError(
            "No saved configuration.\nPlease configure a match first."
        )

    if game_type is None:
        raise IncompleteConfigError(
            "Configuration incomplete:\nPlease configure a game."
        )

    if any(p_type is None for p_type in player_types):
        raise IncompleteConfigError(
            "Configuration incomplete:\nPlease configure two players."
        )

    game = _build_game(game_config)
    agents = [_build_agent(p) for p in player_configs]

    runner = GameRunner(game, agents, user_settings["repetition_limit"])

    return runner, user_settings

def _build_game(config):
    """Build a game instance from its configuration."""
    return _GAME_CLS[config["type"]](**config["settings"])

def _build_agent(config):
    """
    Build an AI agent instance from its configuration, or return None for a 
    human player.
    """
    player_type = config["type"]

    if player_type == HUMAN_PLAYER:
        return None

    return _AGENT_CLS[player_type](**config["settings"])
