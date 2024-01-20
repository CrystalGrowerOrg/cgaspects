import logging
from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

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
        self.aspect_ratio_checkbox = QCheckBox(
            "Aspect Ratio (PCA, OBA, Surface Area and Volume)"
        )

        self.cda_checkbox = QCheckBox("CDA")
        self.plotting_checkbox = QCheckBox("Auto-Generate Plots")
        layout.addWidget(self.aspect_ratio_checkbox)
        layout.addWidget(self.cda_checkbox)

        self.listWidget = QListWidget(parent=self)
        layout.addWidget(self.listWidget)

        self.combo_boxes: list[QComboBox] = []
        self.directions = directions
        self.checked_directions = None
        direction_layout = QHBoxLayout()

        for i in range(3):
            combo_box = QComboBox()
            combo_box.setEnabled(False)
            # Initially disable all comboboxes
            combo_box.addItem("Select Direction")
            direction_layout.addWidget(combo_box)
            self.combo_boxes.append(combo_box)

        layout.addLayout(direction_layout)
        layout.addWidget(self.plotting_checkbox)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.cda_checkbox.stateChanged.connect(self.enable_cda)

        self.listWidget.itemChanged.connect(self.update_checked_directions)

    def enable_cda(self, state):
        state = Qt.CheckState(state)
        if state == Qt.Checked:
            for direction in self.directions:
                item = QListWidgetItem(direction)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.listWidget.addItem(item)

            for combo_box in self.combo_boxes:
                combo_box.setEnabled(True)

        if state == Qt.Unchecked:
            self.listWidget.clear()
            for combo_box in self.combo_boxes:
                combo_box.setEnabled(False)

    def update_checked_directions(self, item):
        for combo_box in self.combo_boxes:
            combo_box.clear()

        self.checked_directions = []
        for index in range(self.listWidget.count()):
            item = self.listWidget.item(index)
            if item.checkState() == Qt.Checked:
                self.checked_directions.append(item.text())

        for combo_box in self.combo_boxes:
            combo_box.addItems(self.checked_directions)

    def update_combo_boxes(self):
        for combo_box in self.combo_boxes:
            if combo_box.count() > 0:
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
