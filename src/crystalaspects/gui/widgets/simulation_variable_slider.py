from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QDoubleSpinBox, QHBoxLayout, QLabel, QSlider,
                               QWidget)


class SimulationVariableSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, label, values, parent=None):
        super().__init__(parent)

        self.values = values

        self.label = QLabel(label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(len(self.values) - 1)

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min(self.values), max(self.values))
        self.variableValue = min(self.values)

        # Connect signals to slots
        self.slider.valueChanged.connect(self.slider_changed)
        self.spinbox.valueChanged.connect(self.spin_changed)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

    def _calculate_step(self, index):
        if index < len(self.values) - 1:
            return self.values[index + 1] - self.values[index]
        else:
            return self.values[index] - self.values[index - 1]

    def setValue(self, value):
        self.spin_changed(value)

    def slider_changed(self, index):
        value = self.values[index]
        self.variableValue = value
        self.spinbox.setValue(value)
        self.spinbox.setSingleStep(self._calculate_step(index))
        self.valueChanged.emit(self.variableValue)

    def spin_changed(self, value):
        if value in self.values:
            index = self.values.index(value)
            self.variableValue = value
            self.slider.setValue(index)
            self.spinbox.setSingleStep(self._calculate_step(index))
            self.valueChanged.emit(self.variableValue)
        else:
            # Optionally handle the case when value is not in self.values
            pass
