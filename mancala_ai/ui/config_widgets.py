"""Widgets for editing configurable application settings."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox, 
    QCheckBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout, 
    QLabel, 
    QLineEdit,
    QPushButton, 
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QWidget,
    QVBoxLayout,
)

from mancala_ai.ui.format import BOOL_TEXT, BUTTON_WIDTH, bool_colours


_CONFIG_WIDGET_WIDTH = 450

_INFO_SPACING = 15
_CONTROL_SPACING = _INFO_SPACING + 35

_INFO_BUTTON_SIZE = (22, 22)
_POPUP_WIDTH = 320


class TypeWidget(QWidget):
    """Widget for selecting a configurable object's type."""

    def __init__(self, category, obj, text_map, restore, refresh):
        super().__init__()

        self._obj = obj
        self._restore = restore
        self._refresh = refresh

        self.setMinimumWidth(_CONFIG_WIDGET_WIDTH)

        combo_box, self._reverse_map = _prepare_combo(text_map, obj["type"])
        combo_box.currentTextChanged.connect(self._change_type)

        layout = QHBoxLayout(self)

        layout.addWidget(QLabel(f"{category} Type: "))
        layout.addWidget(combo_box)
        
        layout.addSpacing(_CONTROL_SPACING)

    def _change_type(self, text):
        """Change the object type and restore its default settings."""
        self._restore(self._obj, self._reverse_map[text])
        self._refresh()


class _SettingWidget(QWidget):
    """Base widget for editing a configurable setting."""

    changed = Signal()

    def __init__(self, obj, key, setting):
        super().__init__()
        
        self._obj = obj
        self._key = key

        self.setMinimumWidth(_CONFIG_WIDGET_WIDTH)

        self._box_layout = QHBoxLayout(self)
        self._box_layout.addWidget(QLabel(f"{setting["name"]}: "))

        self._input_widgets = []

        if info := setting.get("info"):
            self._box_layout.addSpacing(_INFO_SPACING)
            self._box_layout.addWidget(_InfoPopup(info))
        else:
            self._box_layout.addSpacing(_CONTROL_SPACING)

    def _add_input_widget(self, widget, index=1):
        """Add an editable control to the setting widget."""
        self._input_widgets.append(widget)
        self._box_layout.insertWidget(index, widget)

    def _set_input_enabled(self, enabled):
        """Enable or disable the setting's input controls."""
        for widget in self._input_widgets:
            widget.setEnabled(enabled)


class _BoolWidget(_SettingWidget):
    """Widget for editing a boolean setting."""

    def __init__(self, obj, key, setting):
        super().__init__(obj, key, setting)

        text_map = setting.get("text_map")

        self._text_map = text_map or BOOL_TEXT
        self._colour_map = bool_colours() if text_map is None else None
        
        self._button = QPushButton()

        self._format_button(obj[key])
        self._button.clicked.connect(self._change_bool)

        self._add_input_widget(self._button)

    def _format_button(self, state):
        """Update the button's text and colour for a boolean state."""
        self._button.setText(self._text_map[state])

        if self._colour_map:
            self._button.setStyleSheet(f"color: {self._colour_map[state]};")

    def _change_bool(self):
        """Toggle the boolean setting."""
        state = not self._obj[self._key]
        self._obj[self._key] = state
        self._format_button(state)

        self.changed.emit()


class _NumWidget(_SettingWidget):
    """Widget for editing a numeric setting."""

    def __init__(self, obj, key, setting):
        super().__init__(obj, key, setting)

        self._spin_box = (
            QDoubleSpinBox(singleStep=0.5) if setting["type"] is float 
            else QSpinBox()
        )

        if suffix := setting.get("suffix"):
            self._spin_box.setSuffix(suffix)

        min_value = setting.get("min_value")

        if min_value is not None:
            self._spin_box.setMinimum(min_value)

        value = obj[key]
        default_value = setting["default"]

        self._spin_box.setValue(
            value if value is not None 
            else default_value if default_value is not None
            else min_value if min_value is not None
            else 0
        )
        self._spin_box.valueChanged.connect(self._change_num)

        self._add_input_widget(self._spin_box)

        if setting.get("nullable", False):
            check_box = QCheckBox()

            check_box.setChecked(value is not None)
            self._spin_box.setEnabled(value is not None)
            
            check_box.toggled.connect(self._toggle_value)

            self._add_input_widget(check_box)

    def _change_num(self, value):
        """Update the numeric setting."""
        self._obj[self._key] = value
        self.changed.emit()

    def _toggle_value(self, enabled):
        """Enable or disable the nullable numeric setting."""
        self._spin_box.setEnabled(enabled)
        self._change_num(self._spin_box.value() if enabled else None)


class _ChoiceWidget(_SettingWidget):
    """Widget for selecting from a fixed set of values."""

    def __init__(self, obj, key, setting):
        super().__init__(obj, key, setting)
        
        combo_box, self._reverse_map = _prepare_combo(
            setting["text_map"], obj[key]
        )
        combo_box.currentTextChanged.connect(self._change_choice)

        self._add_input_widget(combo_box)

    def _change_choice(self, text):
        """Update the setting from the selected display value."""
        self._obj[self._key] = self._reverse_map[text]
        self.changed.emit()


class _StringWidget(_SettingWidget):
    """Widget for editing a validated string setting."""

    def __init__(self, obj, key, setting):
        super().__init__(obj, key, setting)

        self._validator = setting["validator"]

        self._line_edit = QLineEdit(obj[key])

        self._line_edit.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        self._line_edit.textChanged.connect(self._change_string)

        self._add_input_widget(self._line_edit)

    def _change_string(self, text):
        """Validate and update the string setting."""
        try:
            value = self._validator(text)
        
        except ValueError:
            self._line_edit.setStyleSheet("border: 1px solid red;")
            return

        self._line_edit.setStyleSheet("")
        self._obj[self._key] = value

        self.changed.emit()


class DefaultButton(QPushButton):
    """Button for restoring an object's default settings."""

    def __init__(self, obj_name, obj, restore, refresh):
        super().__init__(f"Restore Default {obj_name} Settings")

        self._obj = obj
        self._restore = restore
        self._refresh = refresh

        self.setMinimumWidth(BUTTON_WIDTH)
        self.clicked.connect(self._restore_settings)

    def _restore_settings(self):
        """Restore the object's default settings."""
        self._restore(self._obj)
        self._refresh()


class _InfoPopup(QToolButton):
    """Button that displays additional setting information."""

    def __init__(self, text):
        super().__init__()

        self.setText("?")
        
        self.setFixedSize(*_INFO_BUTTON_SIZE)
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid palette(mid);
                border-radius: 11px;
                font-weight: bold;
            }
            
            QToolButton:hover {
                background-color: palette(midlight);
            }
        """)

        self._popup = QFrame(f=Qt.WindowType.Popup)

        label = QLabel(text, wordWrap=True)
        label.setFixedWidth(_POPUP_WIDTH)
        
        layout = QVBoxLayout(self._popup)
        layout.addWidget(label)

        self.clicked.connect(self._show_popup)

    def _show_popup(self):
        """Display the setting information popup."""
        self._popup.move(self.mapToGlobal(self.rect().bottomRight()))
        self._popup.show()


def setting_widgets(obj, spec, refresh):
    """Build setting widgets from a configuration specification."""
    widgets = []
    
    dependencies = {
        setting["dependency"][0] 
        for setting in spec.values() 
        if "dependency" in setting
    }

    for key, setting in spec.items():
        dtype = setting["type"]

        if dtype is bool:
            widget_type = _BoolWidget

        elif dtype in (int, float):
            widget_type = _NumWidget

        elif dtype is str:
            widget_type = (
                _ChoiceWidget if setting.get("valid_set") else _StringWidget
            )
        else:
            raise TypeError(f"Unsupported setting type: {dtype}.")

        widget = widget_type(obj, key, setting)

        if dependency := setting.get("dependency"):
            dependency_key, value = dependency
            widget._set_input_enabled(obj[dependency_key] == value)

        if key in dependencies:
            widget.changed.connect(refresh)
        
        widgets.append(widget)

    return widgets


def _prepare_combo(text_map, current_choice):
    """Build a combo box and its reverse text mapping."""

    combo_box = QComboBox()
    combo_box.addItems(text_map.values())

    if current_choice is None:
        combo_box.setCurrentIndex(-1)
    else:
        combo_box.setCurrentText(text_map[current_choice])

    return combo_box, {v: k for k, v in text_map.items()}
