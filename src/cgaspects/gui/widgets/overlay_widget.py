from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget


class TransparentOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label = QLabel("", parent=self)
        self.label.setAlignment(Qt.AlignLeft)
        self.setVisible(False)

    def setText(self, text):
        self.label.setText(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        parent_size = self.parent().size()

        # Set the size and position of the label
        label_width = 200  # Or any desired width
        label_height = 50  # Or any desired height
        self.label.setGeometry(
            parent_size.width() - label_width,
            parent_size.height() - label_height,
            label_width,
            label_height,
        )
