from PySide6.QtWidgets import QWidget
from crystalaspects.gui.dialogs import crystalinfo_ui


class CrystalInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = crystalinfo_ui.Ui_CrystalInfoWidget()
        self.ui.setupUi(self)

    def update(self, crystal_info):
        self.setEnabled(True)
        self.ui.ar1ValueLabel.setText(f"{crystal_info.aspectRatio1:.2f}")
        self.ui.ar2ValueLabel.setText(f"{crystal_info.aspectRatio2:.2f}")
        self.ui.shapeClassValueLabel.setText(f"{crystal_info.shapeClass}")
        self.ui.saVolRatioValueLabel.setText(
            f"{crystal_info.surfaceAreaVolumeRatio:.2f}"
        )
        self.ui.saValueLabel.setText(f"{crystal_info.surfaceArea:.2f}")
        self.ui.volValueLabel.setText(f"{crystal_info.volume:.2f}")
