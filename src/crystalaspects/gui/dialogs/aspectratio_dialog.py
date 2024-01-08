import logging
from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QHBoxLayout, QScrollArea, QVBoxLayout, QWidget)

logger = logging.getLogger("CA:AspectDaliog")


class AnalysisOptionsDialog(QDialog):
    def __init__(self, directions):
        super().__init__()

        # Initialise Window
        self.setWindowTitle("Analysis Options")
        # Create the main layout for all your widgets
        layout = QVBoxLayout()

        # Create a widget for the main layout
        main_widget = QWidget(self)
        main_widget.setLayout(layout)

        # Create a scroll area and set the main widget as its widget
        scroll = QScrollArea(self)
        scroll.setWidget(main_widget)
        scroll.setWidgetResizable(True)

        # Set the scroll area as the main layout for the dialog
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll)

        # Initialise Checkboxes
        aspect_ratio_checkbox = QCheckBox(
            "Aspect Ratio (PCA, OBA, Surface Area and Volume)"
        )
        cda_checkbox = QCheckBox("CDA")
        plotting_checkbox = QCheckBox("Auto-Generate Plots")
        layout.addWidget(aspect_ratio_checkbox)
        layout.addWidget(cda_checkbox)

        self.aspect_ratio_checkbox = aspect_ratio_checkbox
        self.cda_checkbox = cda_checkbox
        self.plotting_checkbox = plotting_checkbox
        self.checkboxes = []
        self.combo_boxes = []
        self.checked_directions = []

        for direction in directions:
            checkbox = QCheckBox(direction)
            # Initially disable all direction checkboxes
            checkbox.setEnabled(False)
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        direction_layout = QHBoxLayout()

        for i in range(3):
            combo_box = QComboBox()
            combo_box.setEnabled(False)
            # Initially disable all comboboxes
            combo_box.addItem("Select Direction")
            direction_layout.addWidget(combo_box)
            self.combo_boxes.append(combo_box)

        layout.addLayout(direction_layout)
        layout.addWidget(plotting_checkbox)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        cda_checkbox.stateChanged.connect(self.toggle_directions)

        for checkbox in self.checkboxes:
            checkbox.toggled.connect(self.update_checked_directions)

    def toggle_directions(self, state):
        enabled = state == Qt.Checked
        for checkbox in self.checkboxes:
            checkbox.setEnabled(True)

        for combo_box in self.combo_boxes:
            combo_box.setEnabled(True)

    def update_checked_directions(self):
        self.checked_directions = [
            checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()
        ]
        self.update_combo_boxes()

    def update_combo_boxes(self):
        for combo_box in self.combo_boxes:
            combo_box.clear()
            combo_box.addItem("Select Direction")
            combo_box.addItems(self.checked_directions)

    def get_selected_combo_values(self):
        selected_combo_values = []
        for combo_box in self.combo_boxes:
            selected_combo_values.append(combo_box.currentText())
        return selected_combo_values

    def get_options(self):
        selected_aspect_ratio = self.aspect_ratio_checkbox.isChecked()
        selected_cda = self.cda_checkbox.isChecked()
        checked_directions = self.checked_directions
        selected_directions = []
        plotting = self.plotting_checkbox.isChecked()

        options = namedtuple(
            "Options",
            [
                "selected_ar",
                "selected_cda",
                "checked_directions",
                "selected_directions",
                "plotting",
            ],
        )

        for i in range(3):
            selected_direction = self.combo_boxes[i].currentText()
            if (
                selected_direction != "Select Direction"
                and selected_direction in checked_directions
            ):
                selected_directions.append(selected_direction)

        return options(
            selected_ar=selected_aspect_ratio,
            selected_cda=selected_cda,
            checked_directions=checked_directions,
            selected_directions=selected_directions,
            plotting=plotting,
        )
