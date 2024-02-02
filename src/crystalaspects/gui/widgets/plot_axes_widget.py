from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QListWidget,
)
from PySide6.QtCore import Qt
from .checkablelistwidget import CheckableListWidget


class PlotAxesWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Main layout
        layout = QVBoxLayout(self)
        grid = QGridLayout()
        layout.addLayout(grid)

        # X-axis ComboBox
        self.x_axis_label = QLabel("X-axis (select one)", self)
        self.xAxisListWidget = QListWidget(self)
        grid.addWidget(self.x_axis_label, 0, 0)
        grid.addWidget(self.xAxisListWidget, 1, 0)

        # Y-axis ComboBox (ListView with checkboxes)
        self.y_axis_label = QLabel("Y-axis (check multiple)", self)
        self.yAxisListWidget = CheckableListWidget()
        grid.addWidget(self.y_axis_label, 0, 1)
        grid.addWidget(self.yAxisListWidget, 1, 1)

        # Color ComboBox
        self.color_label = QLabel("Color By (select one)", self)
        self.colorListWidget = QListWidget(self)
        self.colorListWidget.addItems(["None"])
        grid.addWidget(self.color_label, 0, 2)
        grid.addWidget(self.colorListWidget, 1, 2)

        self.setLayout(layout)

    def get_selections(self):
        x_item = self.xAxisListWidget.currentItem()
        x_selection = x_item.text() if x_item else None

        y_selections = self.yAxisListWidget.checkedItems()

        color_item = self.colorListWidget.currentItem()
        color_selection = color_item.text() if color_item else "None"

        return x_selection, y_selections, color_selection
