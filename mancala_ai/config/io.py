"""File I/O utilities for configuration data."""

import json
from enum import Enum, auto
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from mancala_ai.config.registry import default_user, empty_match


_CONFIG_DIR = Path(
    QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
)
_MATCH_FILE = _CONFIG_DIR / "match.json"
_USER_FILE = _CONFIG_DIR / "user.json"


class FileTarget(Enum):
    """Identify the configuration file targeted by an operation."""
    
    MATCH = auto()
    USER = auto()


class CorruptedFileError(Exception):
    """Raised when a configuration file contains invalid JSON."""

    def __init__(self, target):
        super().__init__()
        self.target = target


def load_match():
    """Load the saved match configuration."""
    return _load_or_new_json(_MATCH_FILE, _new_match, FileTarget.MATCH)

def load_user():
    """Load the saved user settings."""
    return _load_or_new_json(_USER_FILE, _new_user, FileTarget.USER)

def _load_or_new_json(filepath, template, target):
    """Load JSON or create a new file if missing."""
    try:
        data = _load_json(filepath)

    except FileNotFoundError:
        return template()

    except json.JSONDecodeError as e:
        raise CorruptedFileError(target) from e
    
    return data

def _load_json(filepath):
    """Load data from a JSON file."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(filepath, encoding="utf-8") as file:
        return json.load(file)


def reset_file(target):
    """Reset the targeted configuration file to its default data."""
    if target is FileTarget.MATCH:
        return _new_match()

    if target is FileTarget.USER:
        return _new_user()

    raise ValueError(f"Unsupported file target: {target}.")

def _new_match():
    """Create and save a new match configuration."""
    return _new_json(_MATCH_FILE, empty_match)

def _new_user():
    """Create and save new user settings."""
    return _new_json(_USER_FILE, default_user)

def _new_json(filepath, template):
    """Create and save JSON data using a template."""
    data = template()
    _save_json(filepath, data)

    return data


def save_match(config):
    """Save the match configuration."""
    _save_json(_MATCH_FILE, config)

def save_user(settings):
    """Save the user settings."""
    _save_json(_USER_FILE, settings)

def _save_json(filepath, data):
    """Save data to a JSON file."""
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
