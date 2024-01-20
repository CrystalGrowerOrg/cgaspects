from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6 import QtCore
from PySide6 import QtGui


class CheckableComboBox(QComboBox):
    # Signal to emit when the check state of an item changes
    itemCheckedStateChanged = Signal(int, bool)  # item index, checked state

    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self._model = QtGui.QStandardItemModel(self)
        self.setModel(self._model)
        self.view().pressed.connect(self.handleItemPressed)

    def addItem(self, text, data=None):
        item = QtGui.QStandardItem()
        item.setText(text)
        item.setData(data)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self._model.appendRow(item)

    def addItems(self, texts):
        for text in texts:
            self.addItem(text)

    def handleItemPressed(self, index):
        item = self._model.itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self.itemCheckedStateChanged.emit(index.row(), item.checkState() == Qt.Checked)
        self.updateDisplayText()

    def checkedItems(self):
        checked_items = []
        for row in range(self._model.rowCount()):
            item = self._model.item(row)
            if item.checkState() == Qt.Checked:
                checked_items.append(item.text())
        return checked_items

    def updateDisplayText(self):
        checked_items = self.checkedItems()
        display_text = ", ".join(checked_items) if checked_items else "Select items"
        self.setEditText(display_text)


class PlotAxesComboBoxes(QWidget):
    def __init__(self):
        super().__init__()
        # Main layout
        layout = QVBoxLayout(self)

        # Layout for combo boxes and their labels
        combo_layout = QHBoxLayout()
        layout.addLayout(combo_layout)

        # X-axis ComboBox
        self.x_axis_label = QLabel("X-axis:", self)
        self.x_axis_combobox = QComboBox(self)

        combo_layout.addWidget(self.x_axis_label)
        combo_layout.addWidget(self.x_axis_combobox)

        # Y-axis ComboBox (ListView with checkboxes)
        self.y_axis_label = QLabel("Y-axis:", self)
        self.y_axis_combobox = CheckableComboBox()
        combo_layout.addWidget(self.y_axis_label)
        combo_layout.addWidget(self.y_axis_combobox)

        # Color ComboBox
        self.color_label = QLabel("Color:", self)
        self.color_combobox = QComboBox(self)
        combo_layout.addWidget(self.color_label)
        combo_layout.addWidget(self.color_combobox)

        # Plot button
        self.plot_button = QPushButton("Plot")
        combo_layout.addWidget(self.plot_button)

        # Set the main layout
        self.setLayout(layout)

    def get_selections(self):
        x_selection = self.x_axis_combobox.currentText()

        y_selections = []
        for index in range(self.y_axis_model.rowCount()):
            item = self.y_axis_model.item(index)
            if item.checkState() == Qt.Checked:
                y_selections.append(item.text())

        color_selection = self.color_combobox.currentText()

        return x_selection, y_selections, color_selection
