"""Dialog for adding crystallographic planes to the 3D visualization."""

import dataclasses
import math

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
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
    QWidget,
    QVBoxLayout,
)

from cgaspects.utils.crystal_items import DirectionData, PlaneData


def _colored_icon(color, size=(50, 50)):
    pixmap = QPixmap(*size)
    pixmap.fill(color)
    return QIcon(pixmap)


class PlanesDialog(QDialog):
    planesChanged = Signal(list)
    planesCleared = Signal()
    computePlaneFromSelection = Signal()  # Emitted when user confirms plane-from-points
    addDirectionRequested = Signal(object)  # Emits a DirectionData to add to the directions dialog
    movePlaneAlongNormalRequested = Signal(int)  # Emits the row index of the selected plane

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
        self._find_mode_active = False

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
        self._fractional_radio.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self._fractional_radio)
        mode_layout.addWidget(self._cartesian_radio)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Plane input - horizontal
        input_group = QGroupBox("Plane Definition")
        input_vbox = QVBoxLayout()
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
        self._reduce_btn = QPushButton("Reduce")
        self._reduce_btn.setToolTip(
            "Reduce Miller indices by their greatest common divisor (e.g., 2 4 2 → 1 2 1)"
        )
        self._reduce_btn.clicked.connect(self._reduce_miller_indices)
        input_layout.addWidget(self._reduce_btn)
        input_vbox.addLayout(input_layout)
        input_group.setLayout(input_vbox)
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

        for spin in (self._h_spin, self._k_spin, self._l_spin):
            spin.valueChanged.connect(self._update_color_from_miller)
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

        # Single row: [ Add Plane (¼) + Cancel Edit (¼, hidden) | Find Plane (¼) + Confirm (¼, hidden) ]
        action_layout = QHBoxLayout()

        # Left half — Add/Update button always visible, Cancel Edit appears alongside it
        add_container = QWidget()
        add_inner = QHBoxLayout(add_container)
        add_inner.setContentsMargins(0, 0, 0, 0)
        add_inner.setSpacing(action_layout.spacing())

        self._add_button = QPushButton("Add Plane")
        self._add_button.setDefault(True)
        self._add_button.clicked.connect(self._add_or_update_plane)
        self._cancel_edit_btn = QPushButton("Cancel Edit")
        self._cancel_edit_btn.clicked.connect(self._cancel_edit)
        self._cancel_edit_btn.setVisible(False)
        add_inner.addWidget(self._add_button, 1)
        add_inner.addWidget(self._cancel_edit_btn, 1)

        action_layout.addWidget(add_container, 1)  # half

        # Right half — Find/Cancel button always visible, Confirm appears alongside it
        find_container = QWidget()
        find_inner = QHBoxLayout(find_container)
        find_inner.setContentsMargins(0, 0, 0, 0)
        find_inner.setSpacing(action_layout.spacing())

        self._find_btn = QPushButton("Find Plane")
        self._find_btn.setToolTip(
            "Select 3 or more points in the 3D view using Shift+Click, then click 'Confirm'"
        )
        self._find_btn.clicked.connect(self._toggle_find_mode)
        self._confirm_plane_btn = QPushButton("Confirm")
        self._confirm_plane_btn.setToolTip("Compute plane from currently selected points")
        self._confirm_plane_btn.setVisible(False)
        self._confirm_plane_btn.clicked.connect(self._confirm_plane_from_selection)
        find_inner.addWidget(self._find_btn, 1)  # quarter of total (half of right half)
        find_inner.addWidget(self._confirm_plane_btn, 1)  # quarter of total when visible

        action_layout.addWidget(find_container, 1)  # half
        main_layout.addLayout(action_layout)

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
        self._as_direction_btn = QPushButton("Add as Direction")
        self._as_direction_btn.setToolTip("Add the selected plane's indices as a direction vector")
        self._as_direction_btn.clicked.connect(self._add_selected_as_direction)
        btn_layout.addWidget(self._remove_btn)
        btn_layout.addWidget(self._clear_btn)
        btn_layout.addWidget(self._as_direction_btn)
        main_layout.addLayout(btn_layout)

        # ------------------------------------------------------------------ #
        # Slicing controls                                                     #
        # ------------------------------------------------------------------ #
        slice_group = QGroupBox("Slicing (selected plane)")
        slice_outer = QVBoxLayout()

        # Row 1: enable + two-sided toggle
        slice_row1 = QHBoxLayout()
        self._slice_enable_check = QCheckBox("Enable slice")
        self._slice_enable_check.setToolTip(
            "Show only points within the specified distance from this plane"
        )
        self._slice_enable_check.stateChanged.connect(self._on_slice_settings_changed)
        self._slice_two_sided_check = QCheckBox("Two-sided slab")
        self._slice_two_sided_check.setChecked(True)
        self._slice_two_sided_check.setToolTip(
            "Checked: show points within ±thickness/2 of the plane.\n"
            "Unchecked: show points on the positive-normal side only (0 to thickness)."
        )
        self._slice_two_sided_check.stateChanged.connect(self._on_slice_settings_changed)
        slice_row1.addWidget(self._slice_enable_check)
        slice_row1.addWidget(self._slice_two_sided_check)
        slice_row1.addStretch()
        slice_outer.addLayout(slice_row1)

        # Row 2: thickness spinbox
        slice_row2 = QHBoxLayout()
        self._slice_thickness_label = QLabel("Thickness:")
        slice_row2.addWidget(self._slice_thickness_label)
        self._slice_thickness_spin = QDoubleSpinBox()
        self._slice_thickness_spin.setRange(0.1, 10000.0)
        self._slice_thickness_spin.setValue(5.0)
        self._slice_thickness_spin.setSingleStep(0.5)
        self._slice_thickness_spin.setDecimals(2)
        self._slice_thickness_spin.setToolTip("Slab/half-space thickness in world units")
        self._slice_thickness_spin.valueChanged.connect(self._on_slice_settings_changed)
        slice_row2.addWidget(self._slice_thickness_spin)
        slice_row2.addStretch()
        slice_outer.addLayout(slice_row2)

        # Row 3: hide/show + move along normal
        slice_row3 = QHBoxLayout()
        self._plane_visible_btn = QPushButton("Hide Plane")
        self._plane_visible_btn.setToolTip(
            "Hide or show the plane polygon (slice filter stays active)"
        )
        self._plane_visible_btn.clicked.connect(self._toggle_plane_visibility)
        self._move_normal_btn = QPushButton("Move Along Normal…")
        self._move_normal_btn.setToolTip(
            "Slide this plane along its normal between the two extremes of the crystal"
        )
        self._move_normal_btn.clicked.connect(self._request_move_along_normal)
        slice_row3.addWidget(self._plane_visible_btn)
        slice_row3.addWidget(self._move_normal_btn)
        slice_row3.addStretch()
        slice_outer.addLayout(slice_row3)

        slice_group.setLayout(slice_outer)
        main_layout.addWidget(slice_group)
        self._slice_group = slice_group
        self._set_slicing_controls_enabled(False)

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

    @staticmethod
    def _miller_to_color(h, k, ml):
        """Map |h|→R, |k|→G, |l|→B, normalised by the dominant index."""
        r, g, b = abs(h), abs(k), abs(ml)
        max_val = max(r, g, b)
        if max_val < 1e-9:
            return QColor(120, 120, 120)
        r, g, b = r / max_val, g / max_val, b / max_val
        # n(111) and equivalents: all equal - would be white; use grey instead for visibility
        if abs(r - g) < 1e-6 and abs(g - b) < 1e-6:
            return QColor(180, 180, 180)
        return QColor(int(r * 255), int(g * 255), int(b * 255))

    def _update_color_from_miller(self):
        color = self._miller_to_color(
            self._h_spin.value(), self._k_spin.value(), self._l_spin.value()
        )
        self._color = color
        self._color_button.setIcon(_colored_icon(self._color))

    def _on_mode_changed(self, fractional_checked):
        """Convert spinbox values when switching between Cartesian and Miller modes."""
        if self._crystallography is None or self._crystallography.cell is None:
            return
        h = self._h_spin.value()
        k = self._k_spin.value()
        ml = self._l_spin.value()
        vec = np.array([h, k, ml], dtype=np.float64)
        for spin in (self._h_spin, self._k_spin, self._l_spin):
            spin.blockSignals(True)
        if fractional_checked:
            # Cartesian normal → Miller indices (reciprocal space: use M^T)
            miller = self._crystallography.cart_to_miller(vec)
            max_abs = np.max(np.abs(miller))
            if max_abs > 1e-9:
                miller = miller / max_abs
            self._h_spin.setValue(float(miller[0]))
            self._k_spin.setValue(float(miller[1]))
            self._l_spin.setValue(float(miller[2]))
        else:
            # Miller indices → Cartesian normal (reciprocal space: use M^{-T})
            cart = self._crystallography.miller_to_cart_normal(vec)
            norm = np.linalg.norm(cart)
            if norm > 1e-9:
                cart = cart / norm
            self._h_spin.setValue(float(cart[0]))
            self._k_spin.setValue(float(cart[1]))
            self._l_spin.setValue(float(cart[2]))
        for spin in (self._h_spin, self._k_spin, self._l_spin):
            spin.blockSignals(False)
        self._update_color_from_miller()

    def _pick_color(self):
        color = QColorDialog.getColor(
            self._color, self, "Select Plane Color", QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self._color = color
            self._color_button.setIcon(_colored_icon(self._color))

    def _build_plane(self) -> PlaneData:
        size_relative = self._size_spin.value()
        return PlaneData(
            normal=(self._h_spin.value(), self._k_spin.value(), self._l_spin.value()),
            origin=(self._ox_spin.value(), self._oy_spin.value(), self._oz_spin.value()),
            fractional=self._fractional_radio.isChecked(),
            size=size_relative * self._max_extent,
            size_relative=size_relative,
            color=(self._color.redF(), self._color.greenF(), self._color.blueF()),
            alpha=self._alpha_slider.value() / 255.0,
        )

    @staticmethod
    def _make_list_label(plane: PlaneData) -> str:
        mode = "Miller" if plane.fractional else "cart"
        n = plane.normal
        return f"({n[0]:.0f} {n[1]:.0f} {n[2]:.0f}) ({mode}) size={plane.size_relative:.1f}x"

    def _add_or_update_plane(self):
        plane = self._build_plane()

        if self._editing_index is not None:
            idx = self._editing_index
            self._planes[idx] = plane
            item = self._plane_list.item(idx)
            color = QColor.fromRgbF(*plane.color)
            item.setIcon(_colored_icon(color, size=(16, 16)))
            item.setText(self._make_list_label(plane))
            self._cancel_edit()
            self._status_label.setText(f"Updated plane at index {idx}")
        else:
            self._planes.append(plane)
            color = QColor.fromRgbF(*plane.color)
            icon = _colored_icon(color, size=(16, 16))
            item = QListWidgetItem(icon, self._make_list_label(plane))
            item.setData(Qt.UserRole, len(self._planes) - 1)
            self._plane_list.addItem(item)
            n = plane.normal
            self._status_label.setText(f"Added plane ({n[0]:.0f} {n[1]:.0f} {n[2]:.0f})")

        self.planesChanged.emit(list(self._planes))

    def _load_item_for_editing(self, item):
        row = self._plane_list.row(item)
        if row < 0 or row >= len(self._planes):
            return
        self._editing_index = row
        p = self._planes[row]

        for spin in (self._h_spin, self._k_spin, self._l_spin):
            spin.blockSignals(True)
        self._h_spin.setValue(p.normal[0])
        self._k_spin.setValue(p.normal[1])
        self._l_spin.setValue(p.normal[2])
        for spin in (self._h_spin, self._k_spin, self._l_spin):
            spin.blockSignals(False)

        self._ox_spin.setValue(p.origin[0])
        self._oy_spin.setValue(p.origin[1])
        self._oz_spin.setValue(p.origin[2])

        for radio in (self._fractional_radio, self._cartesian_radio):
            radio.blockSignals(True)
        if p.fractional:
            self._fractional_radio.setChecked(True)
        else:
            self._cartesian_radio.setChecked(True)
        for radio in (self._fractional_radio, self._cartesian_radio):
            radio.blockSignals(False)

        # Use the stored relative size directly — no division needed
        self._size_spin.setValue(p.size_relative)

        self._color = QColor.fromRgbF(*p.color)
        self._color_button.setIcon(_colored_icon(self._color))
        self._alpha_slider.setValue(int(p.alpha * 255))

        self._add_button.setText("Update Plane")
        self._cancel_edit_btn.setVisible(True)
        self._status_label.setText(f"Editing plane {row}")
        self._load_slice_controls(p)
        self._set_slicing_controls_enabled(True)

    def _cancel_edit(self):
        self._editing_index = None
        self._add_button.setText("Add Plane")
        self._cancel_edit_btn.setVisible(False)
        self._status_label.setText("")
        self._set_slicing_controls_enabled(False)

    # ------------------------------------------------------------------ #
    # Slicing helpers                                                      #
    # ------------------------------------------------------------------ #

    def _set_slicing_controls_enabled(self, enabled: bool):
        self._slice_thickness_label.setEnabled(enabled)
        self._slice_enable_check.setEnabled(enabled)
        self._slice_two_sided_check.setEnabled(enabled)
        self._slice_thickness_spin.setEnabled(enabled)
        self._plane_visible_btn.setEnabled(enabled)
        self._move_normal_btn.setEnabled(enabled)

    def _load_slice_controls(self, plane):
        """Update slicing widgets to reflect *plane*'s current settings (no signals)."""
        for widget in (
            self._slice_enable_check,
            self._slice_two_sided_check,
            self._slice_thickness_spin,
        ):
            widget.blockSignals(True)
        self._slice_enable_check.setChecked(plane.slice_enabled)
        self._slice_two_sided_check.setChecked(plane.slice_two_sided)
        self._slice_thickness_spin.setValue(plane.slice_thickness)
        for widget in (
            self._slice_enable_check,
            self._slice_two_sided_check,
            self._slice_thickness_spin,
        ):
            widget.blockSignals(False)
        self._plane_visible_btn.setText("Hide Plane" if plane.visible else "Show Plane")

    def _on_slice_settings_changed(self):
        """Write updated slice settings back to the currently-selected plane."""
        row = self._plane_list.currentRow()
        if row < 0 or row >= len(self._planes):
            return
        p = self._planes[row]
        updated = dataclasses.replace(
            p,
            slice_enabled=self._slice_enable_check.isChecked(),
            slice_two_sided=self._slice_two_sided_check.isChecked(),
            slice_thickness=self._slice_thickness_spin.value(),
        )
        self._planes[row] = updated
        self.planesChanged.emit(list(self._planes))

    def _toggle_plane_visibility(self):
        row = self._plane_list.currentRow()
        if row < 0 or row >= len(self._planes):
            return
        p = self._planes[row]
        updated = dataclasses.replace(p, visible=not p.visible)
        self._planes[row] = updated
        self._plane_visible_btn.setText("Hide Plane" if updated.visible else "Show Plane")
        self.planesChanged.emit(list(self._planes))

    def _request_move_along_normal(self):
        row = self._plane_list.currentRow()
        if row < 0 or row >= len(self._planes):
            self._status_label.setText("No plane selected")
            return
        self.movePlaneAlongNormalRequested.emit(row)

    def update_plane_origin_from_dialog(self, row, new_origin):
        """Called by mainwindow after the move-along-normal slider is adjusted."""
        if row < 0 or row >= len(self._planes):
            return
        updated = dataclasses.replace(self._planes[row], origin=tuple(new_origin))
        self._planes[row] = updated
        item = self._plane_list.item(row)
        if item is not None:
            item.setText(self._make_list_label(updated))
        self.planesChanged.emit(list(self._planes))

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

    def _add_selected_as_direction(self):
        row = self._plane_list.currentRow()
        if row < 0:
            self._status_label.setText("No plane selected")
            return
        p = self._planes[row]
        direction = DirectionData(
            vector=p.normal,
            origin=p.origin,
            fractional=p.fractional,
            style="cylinder",
            thickness=30.0,
            length=p.size_relative,
            length_relative=p.size_relative,
            color=p.color,
            alpha=p.alpha,
        )
        self.addDirectionRequested.emit(direction)
        n = p.normal
        self._status_label.setText(f"Sent ({n[0]:.0f} {n[1]:.0f} {n[2]:.0f}) as direction")

    def add_external(self, plane: PlaneData):
        """Add a PlaneData programmatically (e.g. from the directions dialog)."""
        self._planes.append(plane)
        color = QColor.fromRgbF(*plane.color)
        icon = _colored_icon(color, size=(16, 16))
        item = QListWidgetItem(icon, self._make_list_label(plane))
        item.setData(Qt.UserRole, len(self._planes) - 1)
        self._plane_list.addItem(item)
        self.planesChanged.emit(list(self._planes))
        n = plane.normal
        self._status_label.setText(f"Added plane ({n[0]:.0f} {n[1]:.0f} {n[2]:.0f}) from direction")

    # ------------------------------------------------------------------ #
    # Find plane from selected points                                      #
    # ------------------------------------------------------------------ #

    def _toggle_find_mode(self):
        """Toggle the 'find plane from points' mode on/off."""
        if self._find_mode_active:
            self._find_mode_active = False
            self._find_btn.setText("Find Plane")
            self._confirm_plane_btn.setVisible(False)
            self._status_label.setText("")
        else:
            self._find_mode_active = True
            self._find_btn.setText("Cancel")
            self._confirm_plane_btn.setVisible(True)
            self._status_label.setText(
                "Select 3+ points in the 3D view using Shift+Click, then click 'Confirm'"
            )

    def _confirm_plane_from_selection(self):
        """Request computation of a plane from the current point selection."""
        self.computePlaneFromSelection.emit()
        self._toggle_find_mode()

    def populate_from_plane(self, normal, origin, crystallography=None):
        """Populate the plane definition fields from a computed normal and origin.

        Args:
            normal: Cartesian normal vector (numpy array)
            origin: Cartesian centroid/origin (numpy array)
            crystallography: optional Crystallography object for Miller index conversion
        """
        if crystallography is not None and crystallography.cell is not None:
            # Convert Cartesian normal to Miller indices (reciprocal space: use M^T)
            miller = crystallography.cart_to_miller(normal)
            max_abs = np.max(np.abs(miller))
            if max_abs > 0:
                miller = miller / max_abs
            self._h_spin.setValue(float(miller[0]))
            self._k_spin.setValue(float(miller[1]))
            self._l_spin.setValue(float(miller[2]))
            if self._fractional_radio.isEnabled():
                self._fractional_radio.setChecked(True)
        else:
            norm = np.linalg.norm(normal)
            n = normal / norm if norm > 0 else normal
            self._h_spin.setValue(float(n[0]))
            self._k_spin.setValue(float(n[1]))
            self._l_spin.setValue(float(n[2]))
            self._cartesian_radio.setChecked(True)

        self._ox_spin.setValue(float(origin[0]))
        self._oy_spin.setValue(float(origin[1]))
        self._oz_spin.setValue(float(origin[2]))
        self._status_label.setText(
            "Plane populated from selected points — adjust and click 'Add Plane'"
        )

    # ------------------------------------------------------------------ #
    # Reduce Miller indices                                                #
    # ------------------------------------------------------------------ #

    def _reduce_miller_indices(
        self,
        zero_tol=1e-2,  # absolute tolerance
        ratio_tol=2e-2,  # relative-to-max tolerance
        snap_tol=5e-2,  # snapping tolerance when scaling
        max_index=20,
    ):
        """
        Robust Miller index reduction with noise snapping.
        """

        # --- Get values
        h = float(self._h_spin.value())
        k = float(self._k_spin.value())
        l = float(self._l_spin.value())
        old_str = f"({h:.3g} {k:.3g} {l:.3g})"

        vec = [h, k, l]

        # --- Absolute zero snapping
        vec = [0.0 if abs(v) < zero_tol else v for v in vec]

        if all(abs(v) < 1e-12 for v in vec):
            self._status_label.setText("All indices are zero.")
            return

        # --- Relative snapping (remove small components)
        max_val = max(abs(v) for v in vec)
        vec = [0.0 if abs(v) / max_val < ratio_tol else v for v in vec]

        # Recompute max after snapping
        max_val = max(abs(v) for v in vec)
        vec = [v / max_val for v in vec]

        # --- If already near integers → snap directly
        rounded = [round(v) for v in vec]
        if all(abs(v - r) < snap_tol for v, r in zip(vec, rounded)):
            h_i, k_i, l_i = rounded
        else:
            # --- Try integer scaling
            h_i = k_i = l_i = None
            for scale in range(1, max_index + 1):
                scaled = [v * scale for v in vec]
                rounded = [round(x) for x in scaled]

                if all(abs(s - r) < snap_tol for s, r in zip(scaled, rounded)):
                    h_i, k_i, l_i = rounded
                    break

            if h_i is None:
                # Final fallback: just round normalized vector
                h_i, k_i, l_i = [round(v) for v in vec]

        # --- Final GCD reduction
        g = math.gcd(math.gcd(abs(int(h_i)), abs(int(k_i))), abs(int(l_i)))
        if g > 1:
            h_i //= g
            k_i //= g
            l_i //= g

        # --- Update UI
        self._h_spin.setValue(float(h_i))
        self._k_spin.setValue(float(k_i))
        self._l_spin.setValue(float(l_i))

        self._status_label.setText(f"Snapped {old_str} → ({h_i} {k_i} {l_i})")
