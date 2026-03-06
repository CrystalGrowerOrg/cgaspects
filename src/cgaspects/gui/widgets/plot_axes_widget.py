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

        # Y-axis ComboBox (ListView with checkboxes for Custom mode)
        self.y_axis_label = QLabel("Y-axis (check multiple)", self)
        self.yAxisListWidget = CheckableListWidget()
        grid.addWidget(self.y_axis_label, 0, 1)
        grid.addWidget(self.yAxisListWidget, 1, 1)

        # Y-axis single selection (for Heatmap mode)
        self.yAxisListWidget_single = QListWidget(self)
        grid.addWidget(self.yAxisListWidget_single, 1, 1)
        self.yAxisListWidget_single.hide()  # Hidden by default

        # Color ComboBox
        self.color_label = QLabel("Color By (select one)", self)
        self.colorListWidget = QListWidget(self)
        self.colorListWidget.addItems(["None"])
        grid.addWidget(self.color_label, 0, 2)
        grid.addWidget(self.colorListWidget, 1, 2)

        self.setLayout(layout)

    def set_x_locked(self, items: list):
        """Populate x-axis with items and disable (lock) the widget."""
        self.xAxisListWidget.clear()
        self.xAxisListWidget.addItems(items)
        self.xAxisListWidget.setEnabled(False)
        self.x_axis_label.setText("X-axis: Interactions (auto-locked)")

    def restore_x(self, items: list):
        """Restore x-axis to normal selectable mode with items."""
        self.xAxisListWidget.clear()
        self.xAxisListWidget.addItems(items)
        self.xAxisListWidget.setEnabled(True)
        self.x_axis_label.setText("X-axis (select one)")

    def get_selections(self):
        x_item = self.xAxisListWidget.currentItem()
        x_selection = x_item.text() if x_item else None

        # Check which Y-axis widget is visible
        if self.yAxisListWidget_single.isVisible():
            # Single selection mode (Heatmap)
            y_item = self.yAxisListWidget_single.currentItem()
            y_selections = [(0, y_item.text())] if y_item else []
        else:
            # Multiple selection mode (Custom)
            y_selections = self.yAxisListWidget.checkedItems()

        color_item = self.colorListWidget.currentItem()
        color_selection = color_item.text() if color_item else "None"

        return x_selection, y_selections, color_selection
