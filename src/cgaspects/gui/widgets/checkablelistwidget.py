from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt, Signal


class CheckableListWidget(QListWidget):
    # Signal to emit when the check state of an item changes
    itemCheckedStateChanged = Signal(int, bool)  # item index, checked state

    def __init__(self):
        super().__init__()
        self.itemChanged.connect(self.handleItemChanged)

    def addItem(self, text, checked=False):
        item = QListWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        super().addItem(item)

    def addItems(self, texts, checked=False):
        for text in texts:
            self.addItem(text, checked)

    def handleItemChanged(self, item):
        index = self.row(item)
        checked = item.checkState() == Qt.Checked
        self.itemCheckedStateChanged.emit(index, checked)

    def checkedItems(self):
        checked_items = []
        for index in range(self.count()):
            item = self.item(index)
            if item.checkState() == Qt.Checked:
                checked_items.append((index, item.text()))
        return checked_items
