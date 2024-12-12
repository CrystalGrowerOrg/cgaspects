from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox,
                               QHBoxLayout, QScrollArea, QVBoxLayout, QWidget)


class GrowthRateAnalysisDialogue(QDialog):
    def __init__(self, directions):
        super().__init__()

        # Initialise Window
        self.setWindowTitle("Growth Rate Analysis Options")
        # select_all = QCheckBox("Select All")
        layout = QVBoxLayout()
        # layout.addWidget(select_all)
        self.setLayout(layout)

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

        # plotting_checkbox = QCheckBox("Auto-Generate Plots")

        self.selected_directions = []
        # self.plotting_checkbox = plotting_checkbox

        """if select_all.isChecked():
            for direction in directions:
                checkbox = QCheckBox(direction)
                checkbox.stateChanged.connect(lambda state, dir=direction: self.checkbox_state_changed(state, dir))"""

        for direction in directions:
            checkbox = QCheckBox(direction)
            layout.addWidget(checkbox)

            # Connect the checkbox state change event to a custom slot
            checkbox.stateChanged.connect(
                lambda state, dir=direction: self.checkbox_state_changed(state, dir)
            )

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
