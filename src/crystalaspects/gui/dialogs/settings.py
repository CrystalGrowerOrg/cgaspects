from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QHBoxLayout, QLabel, QScrollArea, QVBoxLayout,
                               QWidget)

from crystalaspects.gui.dialogs import settings_ui

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        # Create an instance of the UI class
        self.ui = settings_ui.Ui_Dialog()
        # Set up the UI
        self.ui.setupUi(self)

    
