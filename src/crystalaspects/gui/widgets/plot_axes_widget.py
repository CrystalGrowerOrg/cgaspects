from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QListView,
)
from PySide6.QtCore import Qt, Signal
from PySide6 import QtCore
from PySide6 import QtGui


class CheckableView(QListView):
    def mousePressEvent(self, event):
        self.clearSelection()
        QListView.mousePressEvent(self, event)
        self.setSelection(
            self.rectForIndex(self.currentIndex()), QtCore.QItemSelectionModel.Select
        )


class CheckableComboBox(QComboBox):
    # Signal to emit when the check state of an item changes
    itemCheckedStateChanged = Signal(int, bool)  # item index, checked state

    def __init__(self):
        super(CheckableComboBox, self).__init__()
        self._model = QtGui.QStandardItemModel(self)
        self.setModel(self._model)

        self._view = CheckableView(self)
        self._view.setModel(self._model)
        self.setView(self._view)

        self._view.pressed.connect(self.handleItemPressed)

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
        # Handle item check state
        item = self._model.itemFromIndex(index)
        newState = Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Checked
        item.setCheckState(newState)
        self.itemCheckedStateChanged.emit(index.row(), newState == Qt.Checked)

        # Keep the combobox open
        self.showPopup()

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
        # combo_layout = QHBoxLayout()
        # layout.addLayout(combo_layout)

        # # X-axis ComboBox
        # self.x_axis_label = QLabel("X-axis:", self)
        # self.x_axis_label.setAlignment(Qt.AlignRight)
        # self.x_axis_combobox = QComboBox(self)

        # combo_layout.addWidget(self.x_axis_label)
        # combo_layout.addWidget(self.x_axis_combobox)

        # # Y-axis ComboBox (ListView with checkboxes)
        # self.y_axis_label = QLabel("Y-axis:", self)
        # self.y_axis_label.setAlignment(Qt.AlignRight)
        # self.y_axis_combobox = CheckableComboBox()
        # combo_layout.addWidget(self.y_axis_label)
        # combo_layout.addWidget(self.y_axis_combobox)

        # # Color ComboBox
        # self.color_label = QLabel("Custom Coloring:", self)
        # self.color_label.setAlignment(Qt.AlignRight)
        # self.color_combobox = QComboBox(self)
        # self.color_combobox.addItems(["None"])
        # combo_layout.addWidget(self.color_label)
        # combo_layout.addWidget(self.color_combobox)

        # # Set the main layout
        # self.setLayout(layout)

        grid = QGridLayout()
        layout.addLayout(grid)

        # X-axis ComboBox
        self.x_axis_label = QLabel("X-axis:", self)
        self.x_axis_combobox = QComboBox(self)
        grid.addWidget(self.x_axis_label, 0, 0)
        grid.addWidget(self.x_axis_combobox, 0, 1)

        # Y-axis ComboBox (ListView with checkboxes)
        self.y_axis_label = QLabel("Y-axis:", self)
        self.y_axis_combobox = CheckableComboBox()
        grid.addWidget(self.y_axis_label, 0, 2)
        grid.addWidget(self.y_axis_combobox, 0, 3)

        # Color ComboBox
        self.color_label = QLabel("Custom Coloring:", self)
        self.color_combobox = QComboBox(self)
        self.color_combobox.addItems(["None"])
        grid.addWidget(self.color_label, 0, 4)
        grid.addWidget(self.color_combobox, 0, 5)

        # Set alignment to right for all labels and combo boxes
        for i in range(grid.rowCount()):
            for j in range(grid.columnCount()):
                widget = grid.itemAtPosition(i, j).widget()
                if widget:
                    grid.setAlignment(widget, Qt.AlignRight)

        self.setLayout(layout)

    def get_selections(self):
        x_selection = self.x_axis_combobox.currentText()
        y_selections = self.y_axis_combobox.checkedItems()
        color_selection = self.color_combobox.currentText()

        return x_selection, y_selections, color_selection
