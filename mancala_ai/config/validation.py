"""Validation utilities for application configuration data."""

from mancala_ai.config.io import FileTarget
from mancala_ai.config.registry import GAMES, PLAYERS, USER_SETTINGS


class CorruptedDataError(Exception):
    """Raised when configuration data is missing or invalid."""
    
    def __init__(self, message, target):
        super().__init__(message)
        self.target = target


def validate_match(config):
    """Validate a match configuration."""
    
    subject = "match data"
    target = FileTarget.MATCH

    _validate_dict(config, subject, target)
    _validate_keys(config, ("game", "players"), subject, target)
    
    _validate_obj(config["game"], GAMES, "game", target)

    players = config["players"]
    
    if not isinstance(players, list):
        raise CorruptedDataError("Players data is not a list.", target)
    
    num_players = len(players)

    if num_players != 2:
        raise CorruptedDataError(
            f"Invalid number of players: {num_players}.", target
        )

    for p in players:
        _validate_obj(p, PLAYERS, "player", target)

def validate_user(settings):
    """Validate user settings."""
    _validate_settings(settings, USER_SETTINGS, "user", FileTarget.USER)


def _validate_obj(config, registry, name, target):
    """Validate a configurable game or player object."""

    subject = f"{name} data"
    
    _validate_dict(config, subject, target)
    _validate_keys(config, ("type", "settings"), subject, target)

    obj_type = config["type"]
    obj_settings = config["settings"]

    if obj_type is None:
        if obj_settings != {}:
            raise CorruptedDataError(
                f"{name.capitalize()} settings exist without a {name} type.",
                target,
            )
    else:
        if obj_type not in registry:
            raise CorruptedDataError(
                # Use repr() for ambiguous values
                f"Unknown {name} type: {obj_type!r}.", target
            )
    
        _validate_settings(
            obj_settings, registry[obj_type]["settings"], name, target
        )

def _validate_settings(settings, spec, name, target):
    """Validate settings against their configuration specification."""
    
    _validate_dict(settings, f"{name} settings", target)
    _validate_keys(settings, spec.keys(), f"{name} setting", target)
    
    for key, setting in spec.items():
        value = settings[key]

        valid_empty = value is None and setting.get("nullable", False)
        valid_non_empty = False

        dtype = setting["type"]

        if type(value) is dtype or (dtype is float and type(value) is int):
            valid_non_empty = True

            min_value = setting.get("min_value")
            if min_value is not None:
                valid_non_empty &= value >= min_value
            
            valid_set = setting.get("valid_set")
            if valid_set is not None:
                valid_non_empty &= value in valid_set

            validator = setting.get("validator")
            if validator is not None:
                try:
                    value = validator(value)
                
                except ValueError:
                    valid_non_empty = False
                
                else:
                    settings[key] = value   # Update stored value

        if not (valid_empty or valid_non_empty):
            raise CorruptedDataError(
                # Use repr() for ambiguous values
                f"Invalid {name} setting: {key} = {value!r}.", target
            )

def _validate_dict(data, subject, target):
    """Validate that configuration data is a dictionary."""
    
    if not isinstance(data, dict):
        raise CorruptedDataError(
            f"{subject.capitalize()} is not a dictionary.", target
        )

def _validate_keys(data, spec, subject, target):
    """Validate that the configuration data contains the correct keys."""
    for key in data:
        if key not in spec:
            raise CorruptedDataError(f"Invalid {subject}: {key!r}.", target)
    
    for key in spec:
        if key not in data:
            raise CorruptedDataError(f"Missing {subject}: {key!r}.", target)
