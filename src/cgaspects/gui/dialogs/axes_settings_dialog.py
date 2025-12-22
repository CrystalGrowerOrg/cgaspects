from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDoubleSpinBox,
                               QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                               QPushButton, QVBoxLayout)


class AxesSettingsDialog(QDialog):
    settingsChanged = Signal(dict)

    def __init__(self, parent=None):
        super(AxesSettingsDialog, self).__init__(parent)
        self.setWindowTitle("Axes Rendering Settings")
        self.setModal(False)
        self.resize(400, 500)

        main_layout = QVBoxLayout(self)

        # Rendering Style Group
        style_group = QGroupBox("Rendering Style")
        style_layout = QFormLayout()

        self.style_combo = QComboBox()
        self.style_combo.addItems(["Line", "Arrow"])
        self.style_combo.setCurrentText("Arrow")
        style_layout.addRow("Style:", self.style_combo)

        self.thickness_spinbox = QDoubleSpinBox()
        self.thickness_spinbox.setRange(1.0, 10.0)
        self.thickness_spinbox.setValue(2.0)
        self.thickness_spinbox.setSingleStep(0.5)
        self.thickness_spinbox.setDecimals(1)
        style_layout.addRow("Thickness:", self.thickness_spinbox)

        style_group.setLayout(style_layout)
        main_layout.addWidget(style_group)

        # # Labels Group
        # labels_group = QGroupBox("Axis Labels")
        # labels_layout = QFormLayout()

        # self.labels_combo = QComboBox()
        # self.labels_combo.addItems(["x, y, z", "a, b, c"])
        # self.labels_combo.setCurrentText("x, y, z")
        # labels_layout.addRow("Label Style:", self.labels_combo)

        # labels_group.setLayout(labels_layout)
        # main_layout.addWidget(labels_group)

        # Scale Group
        scale_group = QGroupBox("Scale Settings")
        scale_layout = QFormLayout()

        self.length_multiplier_spinbox = QDoubleSpinBox()
        self.length_multiplier_spinbox.setRange(0.1, 10.0)
        self.length_multiplier_spinbox.setValue(1.0)
        self.length_multiplier_spinbox.setSingleStep(0.1)
        self.length_multiplier_spinbox.setDecimals(2)
        self.length_multiplier_spinbox.setToolTip("Multiply the axes length by this factor")
        scale_layout.addRow("Length Multiplier:", self.length_multiplier_spinbox)

        scale_group.setLayout(scale_layout)
        main_layout.addWidget(scale_group)

        # Position Group
        position_group = QGroupBox("Position")
        position_layout = QFormLayout()

        position_label = QLabel("Axes Origin Coordinates:")
        position_layout.addRow(position_label)

        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(-10.0, 10.0)
        self.x_spinbox.setValue(0.0)
        self.x_spinbox.setSingleStep(0.1)
        self.x_spinbox.setDecimals(2)
        position_layout.addRow("X:", self.x_spinbox)

        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(-10.0, 10.0)
        self.y_spinbox.setValue(0.0)
        self.y_spinbox.setSingleStep(0.1)
        self.y_spinbox.setDecimals(2)
        position_layout.addRow("Y:", self.y_spinbox)

        self.z_spinbox = QDoubleSpinBox()
        self.z_spinbox.setRange(-10.0, 10.0)
        self.z_spinbox.setValue(0.0)
        self.z_spinbox.setSingleStep(0.1)
        self.z_spinbox.setDecimals(2)
        position_layout.addRow("Z:", self.z_spinbox)

        position_group.setLayout(position_layout)
        main_layout.addWidget(position_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Apply")
        self.close_button = QPushButton("Close")
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.close_button)
        main_layout.addLayout(button_layout)

        # Connect signals
        self.style_combo.currentTextChanged.connect(self._emit_settings)
        self.thickness_spinbox.valueChanged.connect(self._emit_settings)
        # self.labels_combo.currentTextChanged.connect(self._emit_settings)
        self.length_multiplier_spinbox.valueChanged.connect(self._emit_settings)
        self.x_spinbox.valueChanged.connect(self._emit_settings)
        self.y_spinbox.valueChanged.connect(self._emit_settings)
        self.z_spinbox.valueChanged.connect(self._emit_settings)

        self.apply_button.clicked.connect(self._emit_settings)
        self.close_button.clicked.connect(self.close)

    def _emit_settings(self):
        self.settingsChanged.emit(self.get_settings())

    def get_settings(self):
        """Return current settings as a dictionary."""
        return {
            'style': self.style_combo.currentText().lower(),
            'thickness': self.thickness_spinbox.value(),
            # 'label_style': self.labels_combo.currentText(),
            'length_multiplier': self.length_multiplier_spinbox.value(),
            'origin': (
                self.x_spinbox.value(),
                self.y_spinbox.value(),
                self.z_spinbox.value()
            )
        }

    def set_settings(self, settings):
        """Set dialog values from a settings dictionary."""
        if 'style' in settings:
            style_text = settings['style'].capitalize()
            index = self.style_combo.findText(style_text)
            if index >= 0:
                self.style_combo.setCurrentIndex(index)

        if 'thickness' in settings:
            self.thickness_spinbox.setValue(settings['thickness'])

        # if 'label_style' in settings:
        #     index = self.labels_combo.findText(settings['label_style'])
        #     if index >= 0:
        #         self.labels_combo.setCurrentIndex(index)

        if 'length_multiplier' in settings:
            self.length_multiplier_spinbox.setValue(settings['length_multiplier'])

        if 'origin' in settings:
            origin = settings['origin']
            self.x_spinbox.setValue(origin[0])
            self.y_spinbox.setValue(origin[1])
            self.z_spinbox.setValue(origin[2])
