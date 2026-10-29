"""Preparation of saved configuration for application use."""

from mancala_ai.config.builder import build_match
from mancala_ai.config.io import load_match, load_user
from mancala_ai.config.validation import validate_match, validate_user


def prepare_play():
    """Load, validate, and build the configured match."""
    config = prepare_match()
    settings = prepare_user()

    return build_match(config, settings)

def prepare_match():
    """Load and validate the saved match configuration."""
    config = load_match()
    validate_match(config)
    
    return config

def prepare_user():
    """Load and validate the saved user settings."""
    settings = load_user()
    validate_user(settings)
    
    return settings
