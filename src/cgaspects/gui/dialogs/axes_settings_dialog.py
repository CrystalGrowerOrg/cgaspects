from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)


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
        self.style_combo.addItems(["Line", "Arrow", "Cylinder"])
        self.style_combo.setCurrentText("Cylinder")
        style_layout.addRow("Style:", self.style_combo)

        self.thickness_spinbox = QDoubleSpinBox()
        self.thickness_spinbox.setRange(1.0, 10.0)
        self.thickness_spinbox.setValue(3.5)
        self.thickness_spinbox.setSingleStep(0.5)
        self.thickness_spinbox.setDecimals(1)
        style_layout.addRow("Thickness:", self.thickness_spinbox)

        style_group.setLayout(style_layout)
        main_layout.addWidget(style_group)

        # Labels Group
        labels_group = QGroupBox("Axis Labels")
        labels_layout = QFormLayout()

        self.show_labels_checkbox = QCheckBox()
        self.show_labels_checkbox.setChecked(True)
        self.show_labels_checkbox.setToolTip("Show or hide axis labels (x, y, z or a, b, c)")
        labels_layout.addRow("Show Labels:", self.show_labels_checkbox)

        # Label color options
        self.label_color_same_as_axes = QCheckBox()
        self.label_color_same_as_axes.setChecked(False)
        self.label_color_same_as_axes.setToolTip("Use the same color as the axes for labels")
        labels_layout.addRow("Match Axes Color:", self.label_color_same_as_axes)

        # Custom label color (default black)
        label_color_layout = QHBoxLayout()
        self.label_color_button = QPushButton()
        self.label_color = QColor(0, 0, 0)  # Default black
        self._update_color_button(self.label_color_button, self.label_color)
        self.label_color_button.clicked.connect(self._pick_label_color)
        self.label_color_button.setToolTip("Click to choose label color")
        label_color_layout.addWidget(self.label_color_button)
        label_color_layout.addStretch()
        labels_layout.addRow("Label Color:", label_color_layout)

        labels_group.setLayout(labels_layout)
        main_layout.addWidget(labels_group)

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
        self.show_labels_checkbox.stateChanged.connect(self._emit_settings)
        self.label_color_same_as_axes.stateChanged.connect(self._on_label_color_mode_changed)
        self.length_multiplier_spinbox.valueChanged.connect(self._emit_settings)
        self.x_spinbox.valueChanged.connect(self._emit_settings)
        self.y_spinbox.valueChanged.connect(self._emit_settings)
        self.z_spinbox.valueChanged.connect(self._emit_settings)

        self.apply_button.clicked.connect(self._emit_settings)
        self.close_button.clicked.connect(self.close)

        # Initial state for label color button
        self._on_label_color_mode_changed()

    def _update_color_button(self, button, color):
        """Update a button's appearance to show the selected color."""
        button.setStyleSheet(
            f"background-color: {color.name()}; "
            f"border: 1px solid #888; "
            f"min-width: 60px; min-height: 24px;"
        )

    def _pick_label_color(self):
        """Open color picker for label color."""
        color = QColorDialog.getColor(self.label_color, self, "Select Label Color")
        if color.isValid():
            self.label_color = color
            self._update_color_button(self.label_color_button, color)
            self._emit_settings()

    def _on_label_color_mode_changed(self):
        """Handle changes to the 'match axes color' checkbox."""
        same_as_axes = self.label_color_same_as_axes.isChecked()
        self.label_color_button.setEnabled(not same_as_axes)
        self._emit_settings()

    def _emit_settings(self):
        self.settingsChanged.emit(self.get_settings())

    def get_settings(self):
        """Return current settings as a dictionary."""
        return {
            "style": self.style_combo.currentText().lower(),
            "thickness": self.thickness_spinbox.value(),
            "show_labels": self.show_labels_checkbox.isChecked(),
            "label_color_same_as_axes": self.label_color_same_as_axes.isChecked(),
            "label_color": (
                self.label_color.redF(),
                self.label_color.greenF(),
                self.label_color.blueF(),
            ),
            "length_multiplier": self.length_multiplier_spinbox.value(),
            "origin": (self.x_spinbox.value(), self.y_spinbox.value(), self.z_spinbox.value()),
        }

    def set_settings(self, settings):
        """Set dialog values from a settings dictionary."""
        if "style" in settings:
            style_text = settings["style"].capitalize()
            index = self.style_combo.findText(style_text)
            if index >= 0:
                self.style_combo.setCurrentIndex(index)

        if "thickness" in settings:
            self.thickness_spinbox.setValue(settings["thickness"])

        if "show_labels" in settings:
            self.show_labels_checkbox.setChecked(settings["show_labels"])

        if "label_color_same_as_axes" in settings:
            self.label_color_same_as_axes.setChecked(settings["label_color_same_as_axes"])

        if "label_color" in settings:
            r, g, b = settings["label_color"]
            self.label_color = QColor.fromRgbF(r, g, b)
            self._update_color_button(self.label_color_button, self.label_color)

        if "length_multiplier" in settings:
            self.length_multiplier_spinbox.setValue(settings["length_multiplier"])

        if "origin" in settings:
            origin = settings["origin"]
            self.x_spinbox.setValue(origin[0])
            self.y_spinbox.setValue(origin[1])
            self.z_spinbox.setValue(origin[2])
