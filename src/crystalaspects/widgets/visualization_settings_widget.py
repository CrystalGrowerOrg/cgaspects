from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSlider,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QToolButton,
    QColorDialog,
)

from PySide6.QtGui import QPixmap, QIcon, QColor


MARGINS = (5, 5, 5, 5)


class LabelledComboBox(QWidget):
    valueChanged = Signal()

    def __init__(self, label, options, parent=None):
        super().__init__(parent)

        self.label = QLabel(label)

        self.options = options

        self.comboBox = QComboBox()
        self.comboBox.addItems(options)

        # Connect signals to slots
        self.comboBox.currentIndexChanged.connect(self.currentIndexChanged)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(*MARGINS)
        layout.addWidget(self.label)
        layout.addWidget(self.comboBox)
        self.setLayout(layout)

    def setValue(self, value):
        idx = self.options.index(value)
        if idx > -1:
            self.comboBox.setCurrentIndex(idx)

    @property
    def value(self):
        return self.options[self.comboBox.currentIndex()]

    def currentIndex(self):
        return self.comboBox.currentIndex()

    def currentIndexChanged(self, idx):
        self.valueChanged.emit()

    def setOptions(self, options):
        self.comboBox.removeItems()
        self.options = options
        self.comboBox.addItems(options)


def create_colored_icon(color, size=(50, 50)):
    pixmap = QPixmap(*size)
    pixmap.fill(color)
    return QIcon(pixmap)


class LabelledColorSelector(QWidget):
    valueChanged = Signal()

    def __init__(self, label, color=Qt.red, parent=None):
        super().__init__(parent)
        self.label = QLabel(label)

        self.button = QToolButton()
        self.button.clicked.connect(self.openColorDialog)

        self.setValue(color)

        layout = QHBoxLayout()
        layout.setContentsMargins(*MARGINS)
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setValue(self, color):
        self.color = QColor(color)
        self.color = color
        self.icon = create_colored_icon(self.color)
        self.button.setIcon(self.icon)
        self.valueChanged.emit()

    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.setValue(color)

    @property
    def value(self):
        return self.color


class LabelledDoubleSlider(QWidget):
    valueChanged = Signal()

    def __init__(self, label, parent=None, vrange=(0, 1), steps=10):
        super().__init__(parent)

        self.label = QLabel(label)

        self.minimum, self.maximum = vrange
        self.steps = steps

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.steps)
        self.slider.setSingleStep(self.step)

        # Connect signals to slots
        self.slider.valueChanged.connect(self.valueChanged)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(*MARGINS)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    @property
    def step(self):
        return (self.maximum - self.minimum) / self.steps

    def setValue(self, value):
        self.slider.setValue(value)

    @property
    def value(self):
        return self.minimum + self.slider.value() * self.step


class VisualizationSettingsWidget(QWidget):
    settingsChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(5)
        self.widgets = {}

        w = LabelledDoubleSlider(
            "Point Size", vrange=(1.0, 20.0), steps=20, parent=self
        )
        w.setValue(6.0)

        self.widgets["Point Size"] = w
        w.valueChanged.connect(self.settingsChanged)

        # self.widgets["Point Type"] = LabelledComboBox("Point Type", ("Point", "Sphere"))

        # TODO avoid hard coding these
        w = LabelledComboBox(
            "Color Map",
            (
                "Viridis",
                "Cividis",
                "Plasma",
                "Inferno",
                "Magma",
                "Twilight",
                "HSV",
            ),
        )

        self.widgets["Color Map"] = w
        w.valueChanged.connect(self.settingsChanged)

        w = LabelledComboBox(
            "Color By",
            (
                "Layer",
                "Atom/Molecule Type",
                "Atom/Molecule Number",
                "Single Colour",
                "Site Number",
                "Particle Energy",
            ),
        )
        self.widgets["Color By"] = w
        w.valueChanged.connect(self.settingsChanged)

        w = LabelledColorSelector("Background Color", QColor(Qt.white))
        self.widgets["Background Color"] = w
        w.valueChanged.connect(self.settingsChanged)

        w = LabelledComboBox(
            "Projection",
            (
                "Orthographic",
                "Perspective",
            ),
        )
        self.widgets["Projection"] = w
        w.valueChanged.connect(self.settingsChanged)

        for w in self.widgets.values():
            layout.addWidget(w)

        self.setLayout(layout)

    def values(self):
        return {"Point Size": self.pointSizeSlider.value}

    def setAvailableOptions(self, key, options):
        if key not in self.widgets:
            return
        w = self.widgets[key]
        if isinstance(w, LabelledComboBox):
            w.setOptions(options)

    def setEnabled(self, enabled=True):
        for v in self.widgets.values():
            v.setEnabled(enabled)

    def settings(self):
        return {k: w.value for k, w in self.widgets.items()}
