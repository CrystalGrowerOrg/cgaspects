from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class GrowthRateAnalysisDialogue(QDialog):
    def __init__(self, directions):
        super().__init__()

        # Initialise Window
        self.setWindowTitle("Growth Rate Analysis Options")
        layout = QVBoxLayout()
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

        self.selected_directions = []

        for direction in directions:
            checkbox = QCheckBox(direction)
            layout.addWidget(checkbox)

            # Connect the checkbox state change event to a custom slot
            checkbox.stateChanged.connect(
                lambda state, dir=direction: self.checkbox_state_changed(state, dir)
            )

        # X-axis mode selection
        xaxis_group = QGroupBox("X-Axis for Growth Rate Fitting")
        xaxis_layout = QHBoxLayout()
        self._xaxis_auto = QRadioButton("Auto (time if available)")
        self._xaxis_time = QRadioButton("Force time column")
        self._xaxis_index = QRadioButton("Use row index")
        self._xaxis_auto.setChecked(True)
        self._xaxis_auto.setToolTip(
            "Use the time column if present and valid, otherwise fall back to row index"
        )
        self._xaxis_time.setToolTip(
            "Always use the time column; files without a valid time column will be skipped"
        )
        self._xaxis_index.setToolTip(
            "Always use row index, ignoring any time column"
        )
        xaxis_layout.addWidget(self._xaxis_auto)
        xaxis_layout.addWidget(self._xaxis_time)
        xaxis_layout.addWidget(self._xaxis_index)
        xaxis_group.setLayout(xaxis_layout)
        layout.addWidget(xaxis_group)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    @property
    def xaxis_mode(self):
        """Return the selected x-axis mode: 'auto', 'time', or 'index'."""
        if self._xaxis_time.isChecked():
            return "time"
        if self._xaxis_index.isChecked():
            return "index"
        return "auto"

    def checkbox_state_changed(self, state, direction):
        if state == 2:  # 2 corresponds to checked state
            self.selected_directions.append(direction)
        else:
            self.selected_directions.remove(direction)
