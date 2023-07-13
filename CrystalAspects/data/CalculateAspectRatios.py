from PyQt5.QtWidgets import QVBoxLayout, \
    QDialogButtonBox, QCheckBox, QDialog, \
    QHBoxLayout, QComboBox

from CrystalAspects.tools.shape_analysis import AspectRatioCalc

class AnalysisOptionsDialog(QDialog):
    def __init__(self, directions):
        super().__init__()

        self.setWindowTitle("Analysis Options")
        layout = QVBoxLayout()
        self.setLayout(layout)

        aspect_ratio_checkbox = QCheckBox("Aspect Ratio")
        cda_checkbox = QCheckBox("CDA")
        layout.addWidget(aspect_ratio_checkbox)
        layout.addWidget(cda_checkbox)


        self.aspect_ratio_checkbox = aspect_ratio_checkbox
        self.cda_checkbox = cda_checkbox
        direction_layout = QHBoxLayout()
        self.checkboxes = []

        for direction in directions:
            checkbox = QCheckBox(direction)
            layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        direction_layout = QHBoxLayout()
        self.combo_boxes = []

        for i in range(3):
            combo_box = QComboBox()
            combo_box.addItem("Select Direction")
            combo_box.addItems(directions)
            direction_layout.addWidget(combo_box)
            self.combo_boxes.append(combo_box)

        layout.addLayout(direction_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_directions(self):
        selected_directions = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                selected_directions.append(checkbox.text())
        return selected_directions

    def get_selected_combo_values(self):
        selected_combo_values = []
        for combo_box in self.combo_boxes:
            selected_combo_values.append(combo_box.currentText())
        return selected_combo_values


    def get_options(self):
        selected_aspect_ratio = self.aspect_ratio_checkbox.isChecked()
        selected_cda = self.cda_checkbox.isChecked()
        selected_directions = self.directions_checkbox.isChecked()
        selected_direction_aspect_ratio = self.direction_aspect_ratio_combobox.currentText()

        return selected_aspect_ratio, selected_cda, selected_directions, selected_direction_aspect_ratio
