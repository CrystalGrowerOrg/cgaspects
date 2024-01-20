from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QFormLayout, QHBoxLayout, QLabel, QScrollArea,
                               QVBoxLayout, QWidget)

from crystalaspects.gui.dialogs import settings_ui
from crystalaspects.gui.utils.py_toggle import PyToggle


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        # Create an instance of the UI class
        self.ui = settings_ui.Ui_settings_Dialog()
        # Set up the UI
        self.ui.setupUi(self)

        self.ui.colourmode_comboBox.clear()
        self.ui.colour_comboBox.clear()
        self.ui.pointtype_comboBox.clear()
        self.ui.bgcolour_comboBox.clear()
        
        self.colour_list = [
            "Viridis",
            "Plasma",
            "Inferno",
            "Magma",
            "Cividis",
            "Twilight",
            "Twilight Shifted",
            "HSV",
        ]

        self.ui.colourmode_comboBox.addItems(
            [
                "Atom/Molecule Type",
                "Atom/Molecule Number",
                "Layer",
                "Single Colour",
                "Site Number",
                "Particle Energy",
            ]
        )
        self.ui.pointtype_comboBox.addItems(["Points", "Spheres"])
        self.ui.projection_comboBox.addItems(["Orthographic", "Perspective"])
        self.ui.colour_comboBox.addItems(self.colour_list)
        self.ui.bgcolour_comboBox.addItems(
            ["Black", "White"]
        )