from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QCheckBox, QDialog, QHBoxLayout

class GrowthRateAnalysisDialogue(QDialog):
    def __init__(self, directions):
        super().__init__()

        # Initialise Window
        self.setWindowTitle("Growth Rate Analysis Options")
        layout = QVBoxLayout()
        self.setLayout(layout)

        plotting_checkbox = QCheckBox("Auto-Generate Plots")

        self.selected_directions = []
        self.plotting_checkbox = plotting_checkbox

        for direction in directions:
            checkbox = QCheckBox(direction)
            layout.addWidget(checkbox)

            # Connect the checkbox state change event to a custom slot
            checkbox.stateChanged.connect(lambda state, dir=direction: self.checkbox_state_changed(state, dir))

        direction_layout = QHBoxLayout()
        direction_layout.addWidget(plotting_checkbox)
        layout.addLayout(direction_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def checkbox_state_changed(self, state, direction):
        if state == 2:  # 2 corresponds to checked state
            self.selected_directions.append(direction)
        else:
            self.selected_directions.remove(direction)

    def on_ok_button_clicked(self):
        auto_plotting = self.plotting_checkbox.isChecked()
        self.accept()