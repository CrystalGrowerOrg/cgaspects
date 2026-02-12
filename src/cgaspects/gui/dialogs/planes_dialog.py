"""Dialog for adding crystallographic planes to the 3D visualization."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDoubleSpinBox,
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


class PlanesDialog(QDialog):
    planesChanged = Signal(list)
    planesCleared = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Planes")
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(500, 540)

        self._crystallography = None
        self._max_extent = 1.0
        self._planes = []
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
        self._fractional_radio = QRadioButton("Miller (h k l)")
        self._cartesian_radio = QRadioButton("Cartesian Normal")
        self._cartesian_radio.setChecked(True)
        self._fractional_radio.setEnabled(False)
        self._fractional_radio.setToolTip(
            "Set lattice parameters first to enable Miller index mode"
        )
        mode_layout.addWidget(self._fractional_radio)
        mode_layout.addWidget(self._cartesian_radio)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Plane input - horizontal
        input_group = QGroupBox("Plane Definition")
        input_layout = QHBoxLayout()
        self._h_spin = QDoubleSpinBox()
        self._k_spin = QDoubleSpinBox()
        self._l_spin = QDoubleSpinBox()
        for spin, label_text, default in [
            (self._h_spin, "h/nx:", 1.0),
            (self._k_spin, "k/ny:", 0.0),
            (self._l_spin, "l/nz:", 0.0),
        ]:
            spin.setRange(-100.0, 100.0)
            spin.setValue(default)
            spin.setSingleStep(1.0)
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

        # Appearance (size, color, opacity) - horizontal
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QHBoxLayout()

        self._size_spin = QDoubleSpinBox()
        self._size_spin.setRange(0.1, 5.0)
        self._size_spin.setValue(1.0)
        self._size_spin.setSingleStep(0.1)
        self._size_spin.setDecimals(1)
        self._size_spin.setToolTip(
            "Plane size relative to maximum extent of crystal (1 = max extent)"
        )
        appearance_layout.addWidget(QLabel("Size:"))
        appearance_layout.addWidget(self._size_spin)

        self._color_button = QToolButton()
        self._color = QColor(0, 120, 215)
        self._color_button.setIcon(_colored_icon(self._color))
        self._color_button.setMinimumSize(60, 30)
        self._color_button.clicked.connect(self._pick_color)
        appearance_layout.addWidget(QLabel("Color:"))
        appearance_layout.addWidget(self._color_button)

        self._alpha_slider = QSlider(Qt.Horizontal)
        self._alpha_slider.setRange(0, 255)
        self._alpha_slider.setValue(128)
        self._alpha_label = QLabel("128")
        self._alpha_slider.valueChanged.connect(lambda v: self._alpha_label.setText(str(v)))
        appearance_layout.addWidget(QLabel("Opacity:"))
        appearance_layout.addWidget(self._alpha_slider)
        appearance_layout.addWidget(self._alpha_label)

        appearance_group.setLayout(appearance_layout)
        main_layout.addWidget(appearance_group)

        # Add/Update button
        add_layout = QHBoxLayout()
        self._add_button = QPushButton("Add Plane")
        self._add_button.setDefault(True)
        self._add_button.clicked.connect(self._add_or_update_plane)
        self._cancel_edit_btn = QPushButton("Cancel Edit")
        self._cancel_edit_btn.clicked.connect(self._cancel_edit)
        self._cancel_edit_btn.setVisible(False)
        add_layout.addWidget(self._add_button)
        add_layout.addWidget(self._cancel_edit_btn)
        add_layout.addStretch()
        main_layout.addLayout(add_layout)

        # List of planes
        list_label = QLabel("Planes:")
        list_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(list_label)

        self._plane_list = QListWidget()
        self._plane_list.setMaximumHeight(120)
        self._plane_list.itemClicked.connect(self._load_item_for_editing)
        main_layout.addWidget(self._plane_list)

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
        """Set the max extent of the point cloud. Size=1 maps to this extent."""
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
                "Set lattice parameters first to enable Miller index mode"
            )
            if self._fractional_radio.isChecked():
                self._cartesian_radio.setChecked(True)

    def _pick_color(self):
        color = QColorDialog.getColor(
            self._color, self, "Select Plane Color", QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self._color = color
            self._color_button.setIcon(_colored_icon(self._color))

    def _build_plane_dict(self):
        return {
            "normal": (self._h_spin.value(), self._k_spin.value(), self._l_spin.value()),
            "origin": (self._ox_spin.value(), self._oy_spin.value(), self._oz_spin.value()),
            "fractional": self._fractional_radio.isChecked(),
            "size": self._size_spin.value() * self._max_extent,
            "color": (self._color.redF(), self._color.greenF(), self._color.blueF()),
            "alpha": self._alpha_slider.value() / 255.0,
        }

    def _make_list_label(self, plane):
        mode = "Miller" if plane["fractional"] else "cart"
        n = plane["normal"]
        return f"({n[0]:.0f} {n[1]:.0f} {n[2]:.0f}) ({mode}) size={plane['size']:.1f}"

    def _add_or_update_plane(self):
        plane = self._build_plane_dict()

        if self._editing_index is not None:
            idx = self._editing_index
            self._planes[idx] = plane
            item = self._plane_list.item(idx)
            color = QColor.fromRgbF(*plane["color"])
            item.setIcon(_colored_icon(color, size=(16, 16)))
            item.setText(self._make_list_label(plane))
            self._cancel_edit()
            self._status_label.setText(f"Updated plane at index {idx}")
        else:
            self._planes.append(plane)
            color = QColor.fromRgbF(*plane["color"])
            icon = _colored_icon(color, size=(16, 16))
            item = QListWidgetItem(icon, self._make_list_label(plane))
            item.setData(Qt.UserRole, len(self._planes) - 1)
            self._plane_list.addItem(item)
            n = plane["normal"]
            self._status_label.setText(f"Added plane ({n[0]:.0f} {n[1]:.0f} {n[2]:.0f})")

        self.planesChanged.emit(list(self._planes))

    def _load_item_for_editing(self, item):
        row = self._plane_list.row(item)
        if row < 0 or row >= len(self._planes):
            return
        self._editing_index = row
        p = self._planes[row]

        n = p["normal"]
        self._h_spin.setValue(n[0])
        self._k_spin.setValue(n[1])
        self._l_spin.setValue(n[2])

        o = p["origin"]
        self._ox_spin.setValue(o[0])
        self._oy_spin.setValue(o[1])
        self._oz_spin.setValue(o[2])

        if p["fractional"]:
            self._fractional_radio.setChecked(True)
        else:
            self._cartesian_radio.setChecked(True)

        self._size_spin.setValue(
            p["size"] / self._max_extent if self._max_extent > 0 else p["size"]
        )

        self._color = QColor.fromRgbF(*p["color"])
        self._color_button.setIcon(_colored_icon(self._color))
        self._alpha_slider.setValue(int(p["alpha"] * 255))

        self._add_button.setText("Update Plane")
        self._cancel_edit_btn.setVisible(True)
        self._status_label.setText(f"Editing plane {row}")

    def _cancel_edit(self):
        self._editing_index = None
        self._add_button.setText("Add Plane")
        self._cancel_edit_btn.setVisible(False)
        self._status_label.setText("")

    def _remove_selected(self):
        row = self._plane_list.currentRow()
        if row < 0:
            self._status_label.setText("No plane selected")
            return
        if self._editing_index == row:
            self._cancel_edit()
        elif self._editing_index is not None and self._editing_index > row:
            self._editing_index -= 1
        self._plane_list.takeItem(row)
        self._planes.pop(row)
        for i in range(self._plane_list.count()):
            self._plane_list.item(i).setData(Qt.UserRole, i)
        self.planesChanged.emit(list(self._planes))
        self._status_label.setText("Plane removed")

    def _clear_all(self):
        self._cancel_edit()
        self._planes.clear()
        self._plane_list.clear()
        self.planesCleared.emit()
        self._status_label.setText("All planes cleared")
