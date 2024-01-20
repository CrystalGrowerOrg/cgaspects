from PySide6.QtCore import QSignalBlocker, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .simulation_variable_slider import SimulationVariableSlider


class SimulationVariablesWidget(QWidget):
    variableCombinationChanged = Signal()

    def __init__(self, variables, parent=None):
        super().__init__(parent)

        self.variables = variables
        layout = QVBoxLayout()

        self.sliders = []

        for name, values in self.variables.items():
            slider = SimulationVariableSlider(str(name), values, parent=self)
            layout.addWidget(slider)
            self.sliders.append((name, slider))
            slider.valueChanged.connect(self.variableCombinationChanged)

        self.setLayout(layout)

    def _calculate_step(self, index):
        if index < len(self.values) - 1:
            return self.values[index + 1] - self.values[index]
        else:
            return self.values[index] - self.values[index - 1]

    def variableNames(self):
        return tuple(x[0] for x in self.sliders)

    def setValues(self, values):
        with QSignalBlocker(self):
            for val, (name, slider) in zip(values, self.sliders):
                slider.setValue(val)

    def currentValues(self):
        return tuple(slider.variableValue for _, slider in self.sliders)
