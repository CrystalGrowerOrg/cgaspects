from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget
from PySide6.QtGui import QPixmap


class TransparentOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.label = QLabel("", parent=self)
        self.label.setAlignment(Qt.AlignCenter)

    def setText(self, text):
        self.label.setText(text)

    def showIcon(self):
        pixmap = QPixmap(":/app_icons/app_icons/Overlay.png")
        pixmap = pixmap.scaled(
            self.width() / 2,
            self.width() / 2,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        parent_size = self.parent().size()

        # Set the size and position of the label
        self.label.setGeometry(0, 0, parent_size.width(), parent_size.height())
