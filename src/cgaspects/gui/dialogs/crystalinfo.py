from PySide6.QtWidgets import QWidget
from . import crystalinfo_ui


class CrystalInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = crystalinfo_ui.Ui_CrystalInfoWidget()
        self.ui.setupUi(self)

    def update(self, crystal_info):
        self.setEnabled(True)

        def fmt(val):
            return f"{val:.2f}" if val is not None else "N/A"

        self.ui.ar1ValueLabel.setText(fmt(crystal_info.aspectRatio1))
        self.ui.ar2ValueLabel.setText(fmt(crystal_info.aspectRatio2))
        self.ui.shapeClassValueLabel.setText(f"{crystal_info.shapeClass}")
        self.ui.saVolRatioValueLabel.setText(fmt(crystal_info.surfaceAreaVolumeRatio))
        self.ui.saValueLabel.setText(fmt(crystal_info.surfaceArea))
        self.ui.volValueLabel.setText(fmt(crystal_info.volume))
