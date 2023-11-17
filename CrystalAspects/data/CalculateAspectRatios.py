from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QCheckBox, QDialog, QHBoxLayout, QComboBox, QScrollArea, QWidget
from PyQt5.QtCore import Qt

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
        aspect_ratio_checkbox = QCheckBox("Aspect Ratio (PCA, OBA, Surface Area and Volume)")
        cda_checkbox = QCheckBox("CDA")
        plotting_checkbox = QCheckBox("Auto-Generate Plots")
        layout.addWidget(aspect_ratio_checkbox)
        layout.addWidget(cda_checkbox)

        self.aspect_ratio_checkbox = aspect_ratio_checkbox
        self.cda_checkbox = cda_checkbox
        self.plotting_checkbox = plotting_checkbox
        self.checkboxes = []
        self.combo_boxes = []
        self.selected_directions = []

        for direction in directions:
            checkbox = QCheckBox(direction)
            checkbox.setEnabled(False)  # Initially disable all direction checkboxes
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        direction_layout = QHBoxLayout()

        for i in range(3):
            combo_box = QComboBox()
            combo_box.setEnabled(False)  # Initially disable all combo boxes
            combo_box.addItem("Select Direction")
            direction_layout.addWidget(combo_box)
            self.combo_boxes.append(combo_box)

        layout.addLayout(direction_layout)
        layout.addWidget(plotting_checkbox)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        cda_checkbox.stateChanged.connect(self.toggle_directions)  # Connect the stateChanged signal

        for checkbox in self.checkboxes:
            checkbox.toggled.connect(self.update_selected_directions)

    def toggle_directions(self, state):
        enabled = state == Qt.Checked
        for checkbox in self.checkboxes:
            checkbox.setEnabled(enabled)

        for combo_box in self.combo_boxes:
            combo_box.setEnabled(enabled)

    def update_selected_directions(self):
        self.selected_directions = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        self.update_combo_boxes()

    def update_combo_boxes(self):
        for combo_box in self.combo_boxes:
            combo_box.clear()
            combo_box.addItem("Select Direction")
            combo_box.addItems(self.selected_directions)

    def get_selected_directions(self):
        return self.selected_directions

    def get_selected_combo_values(self):
        selected_combo_values = []
        for combo_box in self.combo_boxes:
            selected_combo_values.append(combo_box.currentText())
        return selected_combo_values

    def get_options(self):
        selected_aspect_ratio = self.aspect_ratio_checkbox.isChecked()
        selected_cda = self.cda_checkbox.isChecked()
        selected_directions = self.get_selected_directions()
        selected_direction_aspect_ratio = []
        plotting = self.plotting_checkbox.isChecked()

        for i in range(3):
            selected_direction = self.combo_boxes[i].currentText()
            if selected_direction != "Select Direction" and selected_direction in selected_directions:
                selected_direction_aspect_ratio.append(selected_direction)

        return selected_aspect_ratio, selected_cda, selected_directions, selected_direction_aspect_ratio, plotting