from PySide6.QtWidgets import QDialog
from . import about_ui


class AboutCGDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = about_ui.Ui_AboutCGDialog()
        self.ui.setupUi(self)
