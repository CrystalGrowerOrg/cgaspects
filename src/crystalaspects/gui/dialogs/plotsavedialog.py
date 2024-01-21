import logging
from pathlib import Path

from PySide6.QtCore import QFileInfo, QStandardPaths
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from crystalaspects.gui.dialogs import plotsavedialog_ui

logger = logging.getLogger("CA:PlotDialog")


class PlotSaveDialog(QDialog):
    def __init__(self, figure, parent=None):
        super(PlotSaveDialog, self).__init__(parent)
        # Create an instance of the UI class
        self.ui = plotsavedialog_ui.Ui_PlotSaveDialog()
        # Set up the UI
        self.ui.setupUi(self)
        self.figure = figure

        self.ui.fileTypeComboBox.addItems([".png", ".jpeg", ".eps", ".svg"])
        self.ui.fileTypeComboBox.currentTextChanged.connect(self.handleFileTypeChange)

        # grab the first title in the figure if any
        for ax in self.figure.get_axes():
            title = ax.get_title()
            break
        else:
            title = "plot"

        self.ui.fileLineEdit.setText(f"{title}{self.fileType()}")
        self.ui.filePushButton.clicked.connect(self.handleBrowseButton)

    def fileType(self):
        return self.ui.fileTypeComboBox.currentText()

    def fileName(self):
        return self.ui.fileLineEdit.text()

    def isTransparent(self):
        return self.ui.transparentCheckBox.isChecked()

    def dpi(self):
        return self.ui.dpiSpinBox.value()

    def handleFileTypeChange(self, filetype):
        text = self.ui.fileLineEdit.text()
        if not text:
            return
        p = Path(text)
        self.ui.fileLineEdit.setText(str(p.with_suffix(filetype)))

    def handleBrowseButton(self):
        currentFileType = self.fileType()
        filename, ok = QFileDialog.getSaveFileName(
            self,
            "Select file",
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation),
            f"Images (*{currentFileType})",
        )
        if ok:
            self.ui.fileLineEdit.setText(filename)

    def accept(self):
        file_info = QFileInfo(self.fileName())
        parent_dir = QFileInfo(file_info.dir().absolutePath())

        if (file_info.exists() and file_info.isWritable()) or parent_dir.isWritable():
            self.figure.savefig(
                self.fileName(), transparent=self.isTransparent(), dpi=self.dpi()
            )
            logger.info("Figure saved to %s", self.fileName())
            super().accept()
        else:
            msg = "Unable to write to file"
            logger.error("%s: filename = %s", msg, self.fileName())
            err = QMessageBox()
            err.setIcon(QMessageBox.Critical)
            err.setText(msg)
            err.setInformativeText(
                "Either you don't have write permissions, or it's an invalid file name."
            )
            err.setWindowTitle("Error: can't save plot")
            err.exec()
