from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QHBoxLayout, QLabel, QScrollArea, QVBoxLayout,
                               QWidget, QFormLayout)

from crystalaspects.gui.dialogs import settings_ui
from crystalaspects.gui.utils.py_toggle import PyToggle

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        # Create an instance of the UI class
        self.ui = settings_ui.Ui_settings_Dialog()
        # Set up the UI
        self.ui.setupUi(self)

        self.projection_toggle = PyToggle(
            min_width=275,
            expanding=True,
            state_text=["Perspective", "Orthographic"],
            bg_color="#ff9966",
            active_color="#00BCFF"
        )
        self.ui.display_options_formLayout.setWidget(8, QFormLayout.FieldRole, self.projection_toggle)
    

    
