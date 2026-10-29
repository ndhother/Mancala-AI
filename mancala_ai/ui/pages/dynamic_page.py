"""Base page for dynamically rebuilt application content."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from mancala_ai.ui.pages.page import Page


class DynamicPage(Page):
    """Base page whose dynamic content is rebuilt when refreshed."""
    
    def __init__(self, title):
        super().__init__(title)

        self.dynamic_layout = QVBoxLayout()
        self.dynamic_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.main_layout.addLayout(self.dynamic_layout)
        self.main_layout.addStretch()

    def _build_dynamic_content(self):
        """Build the page's dynamic content."""
        raise NotImplementedError

    def refresh(self):
        """Rebuild the page's dynamic content."""
        self._clear_layout(self.dynamic_layout)
        self._build_dynamic_content()

    def _clear_layout(self, layout):
        """Remove all widgets and child layouts from a layout."""
        while layout.count():
            item = layout.takeAt(0)

            if widget := item.widget():
                widget.deleteLater()

            elif child_layout := item.layout():
                self._clear_layout(child_layout)
