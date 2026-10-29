"""User settings configuration page."""

from PySide6.QtCore import Qt

from mancala_ai.config.io import save_user
from mancala_ai.config.registry import USER_SETTINGS, restore_user
from mancala_ai.ui.config_widgets import DefaultButton, setting_widgets
from mancala_ai.ui.format import SECTION_SPACING, make_buttons
from mancala_ai.ui.pages.dynamic_page import DynamicPage


class UserSettings(DynamicPage):
    """Display and edit application user settings."""

    def __init__(self, settings):
        super().__init__("User Settings")
        self._settings = settings

        button_map = {
            "Save && Exit": self._save, 
            "Cancel": self.go_back.emit,
        }

        for button in make_buttons(button_map):
            self.main_layout.addWidget(
                button, alignment=Qt.AlignmentFlag.AlignHCenter
            )

        self.main_layout.addStretch()

    def _build_dynamic_content(self):
        """Build controls for the current user settings."""

        for widget in setting_widgets(
            self._settings, USER_SETTINGS, self.refresh
        ):
            self.dynamic_layout.addWidget(widget)
        
        self.dynamic_layout.addSpacing(SECTION_SPACING)
        
        self.dynamic_layout.addWidget(
            DefaultButton("User", self._settings, restore_user, self.refresh), 
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )

    def _save(self):
        """Save the user settings and exit the page."""
        
        save_user(self._settings)
        self.status.emit("User settings saved.")
        self.go_back.emit()
