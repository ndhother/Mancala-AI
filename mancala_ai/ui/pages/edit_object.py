"""Page for editing configurable game and player objects."""

from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from mancala_ai.config.registry import (
    GAMES, 
    PLAYERS, 
    restore_game, 
    restore_player,
)
from mancala_ai.ui.config_widgets import (
    DefaultButton, 
    TypeWidget, 
    setting_widgets,
)
from mancala_ai.ui.format import BUTTON_WIDTH, SECTION_SPACING
from mancala_ai.ui.pages.dynamic_page import DynamicPage


class ObjCategory(Enum):
    """Define the configurable object categories."""

    GAME = ("Game", GAMES, restore_game)
    PLAYER = ("Player", PLAYERS, restore_player)

    def __init__(self, display_name, registry, restore):
        self.display_name = display_name
        self.registry = registry
        self.restore = restore


class EditObject(DynamicPage):
    """Edit the type and settings of a configurable object."""

    def __init__(self, obj, category, title):
        super().__init__(title)
        
        self._obj = obj
        self._category_name = category.display_name
        self._registry = category.registry
        self._restore = category.restore

        back_button = QPushButton("Back")
        back_button.setMinimumWidth(BUTTON_WIDTH)
        back_button.clicked.connect(self.go_back.emit)

        self.main_layout.addWidget(
            back_button, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.main_layout.addStretch()

    def _build_dynamic_content(self):
        """Build controls for the object's current type and settings."""

        name_map = {k: v["name"] for k, v in self._registry.items()}
        
        self.dynamic_layout.addWidget(
            TypeWidget(
                self._category_name, 
                self._obj, 
                name_map, 
                self._restore, 
                self.refresh,
            )
        )

        if obj_type := self._obj["type"]:
            self.dynamic_layout.addSpacing(15)

            spec = self._registry[obj_type]

            for widget in setting_widgets(
                self._obj["settings"], spec["settings"], self.refresh
            ):
                self.dynamic_layout.addWidget(widget)

            if spec.get("restore_settings", False):
                self.dynamic_layout.addSpacing(SECTION_SPACING)

                self.dynamic_layout.addWidget(
                    DefaultButton(
                        name_map[obj_type], 
                        self._obj, 
                        self._restore, 
                        self.refresh,
                    ),
                    alignment=Qt.AlignmentFlag.AlignHCenter,
                )
