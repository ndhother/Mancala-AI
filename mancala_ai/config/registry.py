"""Definitions and utilities for configurable objects and settings."""

from mancala_ai.config.move_order import MOVE_ORDER_INFO, parse_move_order


HUMAN_PLAYER = "HUMAN"

_PITS = {
    "name": "Pits per Player", 
    "type": int, 
    "min_value": 1, 
}

_SEEDS = {
    "name": "Seeds per Pit",
    "type": int, 
    "min_value": 1, 
}

_CLOCKWISE = {
    "name": "Sowing Direction", 
    "type": bool, 
    "text_map": {True: "Clockwise", False: "Counter-Clockwise"},
}

_PIE_RULE = {
    "name": "Pie Rule", 
    "rule": True, 
    "type": bool, 
    "info": "Allows Player 2 to swap sides after Player 1's opening move.",
    "default": False,
}

GAMES = {
    "Kalah": {
        "name": "Kalah",
        "settings": {
            "pits": {**_PITS, "default": 6},
            "seeds": {**_SEEDS, "default": 4},
            "clockwise": {**_CLOCKWISE, "default": False},
            "pie_rule": {**_PIE_RULE},
            "sow_to_opp_store": {
                "name": "Sow to Opponent Store", 
                "rule": True, 
                "type": bool, 
                "info": (
                    "Allows seeds to be sown into the opponent's store, "
                    "however no extra turns are awarded."
                ),
                "default": False,
            },
        },
        "restore_settings": True,
    },
    "Oware": {
        "name": "Oware",
        "settings": {
            "pits": {**_PITS, "default": 6},
            "seeds": {**_SEEDS, "default": 4},
            "clockwise": {**_CLOCKWISE, "default": False},
            "pie_rule": {**_PIE_RULE},
            "grand_slam": {
                "name": "Grand Slams", 
                "rule": True, 
                "type": bool, 
                "info": (
                    "Allows a move that captures all of the opponent's seeds."
                ),
                "default": False,
            },
        },
        "restore_settings": True,
    },
    "Congkak": {
        "name": "Congkak",
        "settings": {
            "pits": {**_PITS, "default": 7},
            "seeds": {**_SEEDS, "default": 7},
            "clockwise": {**_CLOCKWISE, "default": True},
            "pie_rule": {**_PIE_RULE},
            "solo_capture": {
                "name": "Solo Captures", 
                "rule": True, 
                "type": bool, 
                "info": (
                    "Allows a capture when the opposite pit is empty, so the "
                    "final seed is captured on its own."
                ),
                "default": True,
            },
            "restrict_first_moves": {
                "name": "First Move Restrictions", 
                "rule": True, 
                "type": bool, 
                "info": (
                    "Prevents captures, relays, and extra turns on each "
                    "player's first move."
                ),
                "default": False,
            },
        },
        "restore_settings": True,
    },
}

_HEURISTICS = {
    "H1": "Score Difference (H1)",
    "H2": "Greedy (H2)",
    "H3": "Row Hoarding (H3)", 
    "H4": "Largest Pile (H4)",
    "H5": "Mobility (H5)",
    "H6": "Turn Advantage (H6)",
}

PLAYERS = {
    HUMAN_PLAYER: {
        "name": "Human Player", 
        "settings": {},
    },
    "RandomAgent": {
        "name": "Random Agent",
        "settings": {
            "seed": {
                "name": "Random Seed", 
                "type": int, 
                "min_value": None,
                "nullable": True, 
                "info": (
                    "Controls the Random Agent's sequence of moves. Using the "
                    "same seed makes its random choices reproducible.\n\n"
                    "Leave unset for different random behaviour between games."
                ),
                "default": None,
            },
        },
    },
    "GreedyAgent": {
        "name": "Greedy Agent", 
        "settings": {},
    },
    "MinimaxAgent": {
        "name": "Minimax Agent",
        "settings": {
            "depth_limit": {
                "name": "Depth Limit", 
                "type": int, 
                "min_value": 1,
                "nullable": True, 
                "info": (
                    "Sets the maximum number of moves Minimax searches "
                    "ahead.\n"
                    "Higher values can improve decision-making but take "
                    "longer to calculate.\n\n"
                    "If no time limit is set, Minimax searches directly to "
                    "this depth."
                ),
                "default": None,
            },
            "time_limit": {
                "name": "Time Limit", 
                "type": float,
                "min_value": 0.01, 
                "suffix": " s",
                "nullable": True, 
                "info": (
                    "Sets the maximum time allowed for each search.\n\n"
                    "Minimax uses iterative deepening, repeatedly searching "
                    "at greater depths until the time limit, depth limit, or "
                    "bottom of the game tree is reached."
                ),
                "default": 1.0,
            },
            "pruning": {
                "name": "Alpha-Beta Pruning", 
                "type": bool,
                "info": (
                    "Skips branches of the search tree that cannot affect the "
                    "final decision.\n"
                    "This can make Minimax search much faster without "
                    "changing the result."
                ),
                "default": True,
            },
            "heuristic": {
                "name": "Heuristic Strategy", 
                "type": str, 
                "valid_set": tuple(_HEURISTICS),
                "text_map": _HEURISTICS,
                "info": (
                    "Chooses how Minimax evaluates a game state when it "
                    "cannot search to the end of the game.\n\n"
                    "Different heuristics favour different features of the "
                    "current position."
                ),
                "default": "H1",
            },
            "move_order": {
                "name": "Move Ordering", 
                "type": str, 
                "validator": parse_move_order,
                "info": MOVE_ORDER_INFO,
                "default": "A",
            },
        },
        "restore_settings": True,
    },
}

USER_SETTINGS = {
    "repetition_limit": {
        "name": "Repetition Limit", 
        "type": int,
        "min_value": 2,
        "nullable": True,
        "info": (
            "Sets how many times the same game state can occur before "
            "the game is ended.\n"
            "Disable to allow unlimited repetitions."
        ),
        "default": 3,
    },
    "skip_relay": {
        "name": "Skip Relays", 
        "type": bool, 
        "info": (
            "Skips the step-by-step display of relay sowing and shows "
            "the finished board state immediately."
        ),
        "default": False,
    },
    "step_mode": {
        "name": "AI vs AI Step Mode",
        "type": bool, 
        "info": (
            "Pauses after each move in AI vs AI matches until Next Move "
            "is clicked."
        ),
        "default": True,
    },
    "playback_delay": {
        "name": "AI vs AI Playback Delay",
        "type": float,
        "min_value": 0.0,
        "suffix": " s",
        "dependency": ("step_mode", False),
        "info": (
            "Sets the time between moves during automatic AI vs AI matches.\n"
            "Has no effect when AI vs AI Step Mode is enabled."
        ),
        "default": 2.5,
    },
}


def empty_match():
    """Return a new empty match configuration."""
    return {
        "game": _new_obj(), 
        "players": [_new_obj(), _new_obj()],
    }

def default_user():
    """Return a new default user settings configuration."""
    return _defaults(USER_SETTINGS)


def restore_game(obj, game_type=None):
    """Reset a game configuration to its default values."""
    _restore_defaults(obj, _default_obj(GAMES, game_type or obj["type"]))

def restore_player(obj, player_type=None):
    """Reset a player configuration to its default values."""
    _restore_defaults(obj, _default_obj(PLAYERS, player_type or obj["type"]))

def restore_user(settings):
    """Reset a user settings configuration to default values."""
    _restore_defaults(settings, _defaults(USER_SETTINGS))


def _new_obj():
    """Return a new empty game or player configuration."""
    return {
        "type": None, 
        "settings": {},
    }

def _default_obj(registry, obj_type):
    """Create a default game or player configuration."""
    return {
        "type": obj_type, 
        "settings": _defaults(registry[obj_type]["settings"]),
    }

def _defaults(spec):
    """Return the default values defined in a configuration specification."""
    result = {}
    
    for k, v in spec.items():
        key = "default"

        if isinstance(v, dict) and key in v:
            result[k] = v[key]
        
        elif isinstance(v, dict):       # For nested defaults
            result[k] = _defaults(v)
    
    return result

def _restore_defaults(config, default):
    """Reset a configuration to its default values."""
    config.clear()
    config.update(default)
