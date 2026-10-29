"""Shared UI presentation values and helpers."""

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QPushButton

BUTTON_WIDTH = 200
SECTION_SPACING = 25

BOOL_TEXT = {True: "On", False: "Off"}

_BOOL_COLOURS = {
    "light": {
        True: "#009000",
        False:  "#909090",
    },
    "dark": {
        True: "#90FF90",
        False:  "#C0C0C0",
    },
}

_PLAYER_COLOURS = {
    "light": {
        0: "#990099",
        1: "#009999",
    },
    "dark": {
        0: "#FF99FF",
        1: "#99FFFF",
    },
}


def _theme_colours(colours):
    """Return colours for the application's current theme."""
    background = QApplication.palette().color(QPalette.ColorRole.Window)
    theme = "dark" if background.lightness() < 128 else "light"

    return colours[theme]

def bool_colours():
    """Return boolean display colours for the current theme."""
    return _theme_colours(_BOOL_COLOURS)

def player_colours():
    """Return player colours for the current theme."""
    return _theme_colours(_PLAYER_COLOURS)


def make_buttons(button_map, min_width=BUTTON_WIDTH):
    """Create buttons mapped to their click handlers."""
    buttons = []

    for text, action in button_map.items():
        button = QPushButton(text)
        button.clicked.connect(action)

        if min_width is not None:
            button.setMinimumWidth(min_width)
        
        buttons.append(button)

    return buttons
