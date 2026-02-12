"""Dialog for adding crystallographic directions to the 3D visualization."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QSlider,
    QToolButton,
    QVBoxLayout,
)


def _colored_icon(color, size=(50, 50)):
    pixmap = QPixmap(*size)
    pixmap.fill(color)
    return QIcon(pixmap)


class DirectionsDialog(QDialog):
    directionsChanged = Signal(list)
    directionsCleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Directions")
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(500, 580)

        self._crystallography = None
        self._max_extent = 1.0
        self._directions = []
        self._editing_index = None

        main_layout = QVBoxLayout(self)

        # Cell info section
        self._cell_group = QGroupBox("Cell Parameters")
        cell_layout = QVBoxLayout()
        self._cell_info_label = QLabel("No lattice parameters set")
        self._cell_info_label.setWordWrap(True)
        self._cell_info_label.setStyleSheet("color: #b26500; font-style: italic;")
        cell_layout.addWidget(self._cell_info_label)
        self._cell_group.setLayout(cell_layout)
        main_layout.addWidget(self._cell_group)

        # Coordinate mode
        mode_group = QGroupBox("Coordinate Mode")
        mode_layout = QHBoxLayout()
        self._fractional_radio = QRadioButton("Fractional [u v w]")
        self._cartesian_radio = QRadioButton("Cartesian (x, y, z)")
        self._cartesian_radio.setChecked(True)
        self._fractional_radio.setEnabled(False)
        self._fractional_radio.setToolTip("Set lattice parameters first to enable fractional mode")
        mode_layout.addWidget(self._fractional_radio)
        mode_layout.addWidget(self._cartesian_radio)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Direction input - horizontal
        input_group = QGroupBox("Direction Vector")
        input_layout = QHBoxLayout()
        self._u_spin = QDoubleSpinBox()
        self._v_spin = QDoubleSpinBox()
        self._w_spin = QDoubleSpinBox()
        for spin, label_text, default in [
            (self._u_spin, "u/x:", 1.0),
            (self._v_spin, "v/y:", 0.0),
            (self._w_spin, "w/z:", 0.0),
        ]:
            spin.setRange(-100.0, 100.0)
            spin.setValue(default)
            spin.setSingleStep(0.1)
            spin.setDecimals(3)
            input_layout.addWidget(QLabel(label_text))
            input_layout.addWidget(spin)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Origin offset - horizontal
        origin_group = QGroupBox("Origin Offset")
        origin_layout = QHBoxLayout()
        self._ox_spin = QDoubleSpinBox()
        self._oy_spin = QDoubleSpinBox()
        self._oz_spin = QDoubleSpinBox()
        for spin, label_text in [
            (self._ox_spin, "X:"),
            (self._oy_spin, "Y:"),
            (self._oz_spin, "Z:"),
        ]:
            spin.setRange(-1000.0, 1000.0)
            spin.setValue(0.0)
            spin.setSingleStep(0.5)
            spin.setDecimals(3)
            origin_layout.addWidget(QLabel(label_text))
            origin_layout.addWidget(spin)
        origin_group.setLayout(origin_layout)
        main_layout.addWidget(origin_group)

        # Rendering settings - horizontal
        render_group = QGroupBox("Rendering")
        render_layout = QHBoxLayout()

        self._style_combo = QComboBox()
        self._style_combo.addItems(["Line", "Arrow", "Cylinder"])
        self._style_combo.setCurrentText("Cylinder")
        render_layout.addWidget(QLabel("Style:"))
        render_layout.addWidget(self._style_combo)

        self._thickness_spin = QDoubleSpinBox()
        self._thickness_spin.setRange(1.0, 100.0)
        self._thickness_spin.setValue(12.0)
        self._thickness_spin.setSingleStep(0.5)
        self._thickness_spin.setDecimals(1)
        render_layout.addWidget(QLabel("Thickness:"))
        render_layout.addWidget(self._thickness_spin)

        self._length_spin = QDoubleSpinBox()
        self._length_spin.setRange(0.1, 5.0)
        self._length_spin.setValue(1.2)
        self._length_spin.setSingleStep(0.1)
        self._length_spin.setDecimals(2)
        self._length_spin.setToolTip(
            "Length relative to maximum extent of crystal (1 = max extent)"
        )
        render_layout.addWidget(QLabel("Length:"))
        render_layout.addWidget(self._length_spin)

        render_group.setLayout(render_layout)
        main_layout.addWidget(render_group)

        # Color and transparency - horizontal
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QHBoxLayout()

        self._color_button = QToolButton()
        self._color = QColor(255, 0, 0)
        self._color_button.setIcon(_colored_icon(self._color))
        self._color_button.setMinimumSize(60, 30)
        self._color_button.clicked.connect(self._pick_color)
        appearance_layout.addWidget(QLabel("Color:"))
        appearance_layout.addWidget(self._color_button)

        self._alpha_slider = QSlider(Qt.Horizontal)
        self._alpha_slider.setRange(0, 255)
        self._alpha_slider.setValue(255)
        self._alpha_label = QLabel("255")
        self._alpha_slider.valueChanged.connect(lambda v: self._alpha_label.setText(str(v)))
        appearance_layout.addWidget(QLabel("Opacity:"))
        appearance_layout.addWidget(self._alpha_slider)
        appearance_layout.addWidget(self._alpha_label)

        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)

        # Add/Update button
        add_layout = QHBoxLayout()
        self._add_button = QPushButton("Add Direction")
        self._add_button.setDefault(True)
        self._add_button.clicked.connect(self._add_or_update_direction)
        self._cancel_edit_btn = QPushButton("Cancel Edit")
        self._cancel_edit_btn.clicked.connect(self._cancel_edit)
        self._cancel_edit_btn.setVisible(False)
        add_layout.addWidget(self._add_button)
        add_layout.addWidget(self._cancel_edit_btn)
        add_layout.addStretch()
        main_layout.addLayout(add_layout)

        # List of directions
        list_label = QLabel("Directions:")
        list_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(list_label)

        self._direction_list = QListWidget()
        self._direction_list.setMaximumHeight(120)
        self._direction_list.itemClicked.connect(self._load_item_for_editing)
        main_layout.addWidget(self._direction_list)

        # List management buttons
        btn_layout = QHBoxLayout()
        self._remove_btn = QPushButton("Remove Selected")
        self._remove_btn.clicked.connect(self._remove_selected)
        self._clear_btn = QPushButton("Clear All")
        self._clear_btn.clicked.connect(self._clear_all)
        btn_layout.addWidget(self._remove_btn)
        btn_layout.addWidget(self._clear_btn)
        main_layout.addLayout(btn_layout)

        # Close
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_layout.addWidget(close_btn)
        main_layout.addLayout(close_layout)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("color: gray; font-style: italic;")
        main_layout.addWidget(self._status_label)

    def set_point_cloud_extent(self, max_extent):
        """Set the max extent of the point cloud. Length=1 maps to this extent."""
        if max_extent is not None and max_extent > 0:
            self._max_extent = max_extent

    def set_crystallography(self, crystallography):
        self._crystallography = crystallography
        if crystallography and crystallography.cell:
            cell = crystallography.cell
            self._cell_info_label.setText(
                f"a = {cell.a:.4f}   b = {cell.b:.4f}   c = {cell.c:.4f}\n"
                f"\u03b1 = {cell.alpha:.3f}\u00b0   \u03b2 = {cell.beta:.3f}\u00b0   \u03b3 = {cell.gamma:.3f}\u00b0"
            )
            self._cell_info_label.setStyleSheet("color: black;")
            self._fractional_radio.setEnabled(True)
            self._fractional_radio.setToolTip("")
        else:
            self._cell_info_label.setText("No lattice parameters set")
            self._cell_info_label.setStyleSheet("color: #b26500; font-style: italic;")
            self._fractional_radio.setEnabled(False)
            self._fractional_radio.setToolTip(
                "Set lattice parameters first to enable fractional mode"
            )
            if self._fractional_radio.isChecked():
                self._cartesian_radio.setChecked(True)

    def _pick_color(self):
        color = QColorDialog.getColor(
            self._color, self, "Select Direction Color", QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self._color = color
            self._color_button.setIcon(_colored_icon(self._color))

    def _build_direction_dict(self):
        return {
            "vector": (self._u_spin.value(), self._v_spin.value(), self._w_spin.value()),
            "origin": (self._ox_spin.value(), self._oy_spin.value(), self._oz_spin.value()),
            "fractional": self._fractional_radio.isChecked(),
            "style": self._style_combo.currentText().lower(),
            "thickness": self._thickness_spin.value(),
            "length": self._length_spin.value() * self._max_extent,
            "color": (self._color.redF(), self._color.greenF(), self._color.blueF()),
            "alpha": self._alpha_slider.value() / 255.0,
        }

    def _make_list_label(self, direction):
        mode = "frac" if direction["fractional"] else "cart"
        v = direction["vector"]
        return f"[{v[0]:.1f} {v[1]:.1f} {v[2]:.1f}] ({mode}) {direction['style']}"

    def _add_or_update_direction(self):
        direction = self._build_direction_dict()

        if self._editing_index is not None:
            # Update existing
            idx = self._editing_index
            self._directions[idx] = direction
            item = self._direction_list.item(idx)
            color = QColor.fromRgbF(*direction["color"])
            item.setIcon(_colored_icon(color, size=(16, 16)))
            item.setText(self._make_list_label(direction))
            self._cancel_edit()
            self._status_label.setText(f"Updated direction at index {idx}")
        else:
            # Add new
            self._directions.append(direction)
            color = QColor.fromRgbF(*direction["color"])
            icon = _colored_icon(color, size=(16, 16))
            item = QListWidgetItem(icon, self._make_list_label(direction))
            item.setData(Qt.UserRole, len(self._directions) - 1)
            self._direction_list.addItem(item)
            v = direction["vector"]
            self._status_label.setText(f"Added direction [{v[0]:.1f} {v[1]:.1f} {v[2]:.1f}]")

        self.directionsChanged.emit(list(self._directions))

    def _load_item_for_editing(self, item):
        row = self._direction_list.row(item)
        if row < 0 or row >= len(self._directions):
            return
        self._editing_index = row
        d = self._directions[row]

        # Populate fields
        v = d["vector"]
        self._u_spin.setValue(v[0])
        self._v_spin.setValue(v[1])
        self._w_spin.setValue(v[2])

        o = d["origin"]
        self._ox_spin.setValue(o[0])
        self._oy_spin.setValue(o[1])
        self._oz_spin.setValue(o[2])

        if d["fractional"]:
            self._fractional_radio.setChecked(True)
        else:
            self._cartesian_radio.setChecked(True)

        style = d["style"].capitalize()
        idx = self._style_combo.findText(style)
        if idx >= 0:
            self._style_combo.setCurrentIndex(idx)

        self._thickness_spin.setValue(d["thickness"])
        self._length_spin.setValue(
            d["length"] / self._max_extent if self._max_extent > 0 else d["length"]
        )

        self._color = QColor.fromRgbF(*d["color"])
        self._color_button.setIcon(_colored_icon(self._color))
        self._alpha_slider.setValue(int(d["alpha"] * 255))

        self._add_button.setText("Update Direction")
        self._cancel_edit_btn.setVisible(True)
        self._status_label.setText(f"Editing direction {row}")

    def _cancel_edit(self):
        self._editing_index = None
        self._add_button.setText("Add Direction")
        self._cancel_edit_btn.setVisible(False)
        self._status_label.setText("")

    def _remove_selected(self):
        row = self._direction_list.currentRow()
        if row < 0:
            self._status_label.setText("No direction selected")
            return
        if self._editing_index == row:
            self._cancel_edit()
        elif self._editing_index is not None and self._editing_index > row:
            self._editing_index -= 1
        self._direction_list.takeItem(row)
        self._directions.pop(row)
        for i in range(self._direction_list.count()):
            self._direction_list.item(i).setData(Qt.UserRole, i)
        self.directionsChanged.emit(list(self._directions))
        self._status_label.setText("Direction removed")

    def _clear_all(self):
        self._cancel_edit()
        self._directions.clear()
        self._direction_list.clear()
        self.directionsCleared.emit()
        self._status_label.setText("All directions cleared")
