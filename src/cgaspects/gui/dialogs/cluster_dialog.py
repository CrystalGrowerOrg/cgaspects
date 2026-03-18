from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QComboBox,
)

from ...utils.data_structures import cluster_options_tuple


class ClusterAnalysisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cluster Analysis Options")

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Beta warning
        warning_label = QLabel(
            "<b>\u26a0\ufe0f Beta Feature</b><br>"
            "Cluster analysis is intended for simulations with internal sites (not just surface particles). "
            "Clustering can be slow and may cause the application to become unresponsive "
            "when there are many points."
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet(
            "QLabel { background-color: #fff3cd; color: #856404; "
            "border: 1px solid #ffc107; border-radius: 4px; padding: 6px; }"
        )
        layout.addWidget(warning_label)

        # Mode selection
        self.ratios_only_checkbox = QCheckBox("Ratios only (skip clustering)")
        self.ratios_only_checkbox.setToolTip(
            "Only compute particle-type count ratios without running a clustering algorithm."
        )
        self.ratios_only_checkbox.toggled.connect(self._on_ratios_only_toggled)
        layout.addWidget(self.ratios_only_checkbox)

        # Algorithm selection
        algo_group = QGroupBox("Clustering Algorithm")
        algo_layout = QHBoxLayout()
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["DBSCAN", "OPTICS"])
        self.algo_combo.currentTextChanged.connect(self._on_algo_changed)
        algo_layout.addWidget(QLabel("Algorithm:"))
        algo_layout.addWidget(self.algo_combo)
        algo_layout.addStretch()
        algo_group.setLayout(algo_layout)
        layout.addWidget(algo_group)
        self._algo_group = algo_group

        # Parameters
        params_group = QGroupBox("Parameters")
        params_layout = QFormLayout()

        self.eps_label = QLabel("ε (neighbourhood radius):")
        self.eps_spin = QDoubleSpinBox()
        self.eps_spin.setRange(0.1, 100.0)
        self.eps_spin.setSingleStep(0.5)
        self.eps_spin.setValue(3.0)
        self.eps_spin.setDecimals(1)
        self.eps_spin.setToolTip(
            "DBSCAN: neighbourhood radius. OPTICS: max neighbourhood radius (0 = unlimited)."
        )
        params_layout.addRow(self.eps_label, self.eps_spin)

        self.min_samples_spin = QSpinBox()
        self.min_samples_spin.setRange(2, 200)
        self.min_samples_spin.setValue(5)
        self.min_samples_spin.setToolTip(
            "Minimum number of samples in a neighbourhood for a point to be a core point."
        )
        params_layout.addRow("Min samples:", self.min_samples_spin)

        self.frame_spin = QSpinBox()
        self.frame_spin.setRange(-1, 9999)
        self.frame_spin.setValue(-1)
        self.frame_spin.setToolTip(
            "Frame index to analyse per XYZ file. -1 = last frame, 0 = first frame."
        )
        params_layout.addRow("Frame index (−1 = last):", self.frame_spin)

        self.scale_checkbox = QCheckBox("Standardise coordinates (StandardScaler)")
        self.scale_checkbox.setToolTip(
            "Normalise coordinates to zero mean and unit variance before clustering."
        )
        params_layout.addRow("", self.scale_checkbox)

        self.downsample_spin = QDoubleSpinBox()
        self.downsample_spin.setRange(0.01, 1.0)
        self.downsample_spin.setSingleStep(0.05)
        self.downsample_spin.setValue(1.0)
        self.downsample_spin.setDecimals(2)
        self.downsample_spin.setToolTip(
            "Fraction of particles to keep before clustering (1.0 = no downsampling). "
            "Useful for speeding up analysis on very large XYZ files."
        )
        params_layout.addRow("Downsample fraction:", self.downsample_spin)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        self._params_group = params_group

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_algo_changed(self, algo):
        if algo == "OPTICS":
            self.eps_label.setText("Max ε (neighbourhood cap, 0 = none):")
        else:
            self.eps_label.setText("ε (neighbourhood radius):")

    def _on_ratios_only_toggled(self, checked: bool):
        self._algo_group.setEnabled(not checked)
        self._params_group.setEnabled(not checked)
        # Frame index is still relevant when ratios_only
        self.frame_spin.setEnabled(True)

    def get_options(self) -> cluster_options_tuple:
        return cluster_options_tuple(
            algorithm=self.algo_combo.currentText(),
            eps=self.eps_spin.value(),
            min_samples=self.min_samples_spin.value(),
            frame_index=self.frame_spin.value(),
            scale=self.scale_checkbox.isChecked(),
            downsample=self.downsample_spin.value(),
            ratios_only=self.ratios_only_checkbox.isChecked(),
        )
