"""Dialog for customising plot axes labels and performing unit conversions."""

from __future__ import annotations

import logging
from dataclasses import replace

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from cgaspects.utils.plot_label import PlotAxisLabel
from cgaspects.utils.units import UnitConversion

logger = logging.getLogger("CA:AxesCustomizationDialog")

# All unit strings that can appear in the "Current unit" combo box
_KNOWN_UNITS: list[str] = sorted(
    {"", "Å", "pm", "nm", "µm", "mm", "cm", "m",
     "kcal/mol", "kJ/mol", "eV", "σ", "°C"}
    | set(UnitConversion.known_units())
)


class _AxisRow(QWidget):
    """A self-contained widget for editing one :class:`PlotAxisLabel`.

    Exposes a ``pending`` property that always reflects the *current* state of
    the edits, including any applied conversion.
    """

    def __init__(self, label: PlotAxisLabel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._original = label
        self._pending_conversion: UnitConversion | None = label.conversion
        # True when the user has explicitly edited a field (or when the dialog is
        # initialised with an already-customised label so Apply preserves it).
        self._user_modified: bool = label.is_user_set

        # ── Current (read-only) display ──────────────────────────────────
        self._current_display = QLabel(str(label) or "<empty>")
        self._current_display.setStyleSheet("color: gray; font-style: italic;")

        # ── Editable name / unit ─────────────────────────────────────────
        self._name_edit = QLineEdit(label.name)
        self._name_edit.setPlaceholderText("Label name (LaTeX OK, e.g. $\\Delta G$)")
        self._name_edit.textChanged.connect(self._mark_user_modified)

        self._unit_edit = QLineEdit(label.unit)
        self._unit_edit.setPlaceholderText("Unit string, e.g. kcal/mol")
        self._unit_edit.textChanged.connect(self._mark_user_modified)

        self._reset_btn = QPushButton("Reset")
        self._reset_btn.setFixedWidth(60)
        self._reset_btn.clicked.connect(self._reset)

        # ── Unit conversion ──────────────────────────────────────────────
        self._cur_unit_combo = QComboBox()
        self._cur_unit_combo.setEditable(True)
        self._cur_unit_combo.addItems(_KNOWN_UNITS)
        idx = self._cur_unit_combo.findText(label.unit)
        if idx >= 0:
            self._cur_unit_combo.setCurrentIndex(idx)
        else:
            self._cur_unit_combo.setCurrentText(label.unit)

        self._set_unit_btn = QPushButton("Set")
        self._set_unit_btn.setFixedWidth(40)
        self._set_unit_btn.clicked.connect(self._refresh_convert_to)

        self._convert_to_combo = QComboBox()
        self._apply_conv_btn = QPushButton("Apply Conversion")
        self._apply_conv_btn.clicked.connect(self._apply_conversion)

        # Build _conv_group before calling _refresh_convert_to so the
        # method can safely toggle its visibility.
        conv_row = QHBoxLayout()
        conv_row.addWidget(self._convert_to_combo, 1)
        conv_row.addWidget(self._apply_conv_btn)
        self._conv_group = QGroupBox("Convert to")
        self._conv_group.setLayout(conv_row)

        self._refresh_convert_to()

        # ── Layout ────────────────────────────────────────────────────────
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)

        form.addRow("Current:", self._current_display)

        name_row = QHBoxLayout()
        name_row.addWidget(self._name_edit, 1)
        name_row.addWidget(QLabel("Unit:"))
        name_row.addWidget(self._unit_edit)
        name_row.addWidget(self._reset_btn)
        form.addRow("Name:", name_row)

        cur_unit_row = QHBoxLayout()
        cur_unit_row.addWidget(self._cur_unit_combo, 1)
        cur_unit_row.addWidget(self._set_unit_btn)
        form.addRow("Current unit:", cur_unit_row)

        form.addRow(self._conv_group)

        self.setLayout(form)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _mark_user_modified(self) -> None:
        """Called whenever the user types in a name/unit field."""
        self._user_modified = True

    def _refresh_convert_to(self) -> None:
        """Populate the 'Convert to' combo based on the current unit field."""
        cur_unit = self._cur_unit_combo.currentText().strip()
        conversions = UnitConversion.available_for(cur_unit)
        self._convert_to_combo.clear()
        if conversions:
            self._convert_to_combo.addItems([c.to_unit for c in conversions])
            self._conv_group.setVisible(True)
            self._apply_conv_btn.setEnabled(True)
        else:
            self._conv_group.setVisible(False)

    def _apply_conversion(self) -> None:
        """Mark a pending conversion and update the unit display field."""
        from_unit = self._cur_unit_combo.currentText().strip()
        to_unit = self._convert_to_combo.currentText().strip()
        if not from_unit or not to_unit:
            return
        try:
            conv = UnitConversion.get(from_unit, to_unit)
        except KeyError as exc:
            logger.warning("Conversion not found: %s", exc)
            return
        self._pending_conversion = conv
        self._user_modified = True
        self._unit_edit.setText(to_unit)
        # Refresh so user can chain further conversions
        self._cur_unit_combo.setCurrentText(to_unit)
        self._refresh_convert_to()
        logger.debug("Pending conversion set: %s", conv)

    def _reset(self) -> None:
        """Restore fields to the original (column-derived) label values."""
        self._user_modified = False
        self._pending_conversion = None
        self._name_edit.blockSignals(True)
        self._name_edit.setText(self._original.name)
        self._name_edit.blockSignals(False)
        self._unit_edit.blockSignals(True)
        self._unit_edit.setText(self._original.unit)
        self._unit_edit.blockSignals(False)
        self._cur_unit_combo.setCurrentText(self._original.unit)
        self._refresh_convert_to()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def pending(self) -> PlotAxisLabel:
        """Return a :class:`PlotAxisLabel` reflecting the current editor state."""
        name = self._name_edit.text().strip()
        unit = self._unit_edit.text().strip()
        return PlotAxisLabel(
            name=name,
            unit=unit,
            is_user_set=self._user_modified,
            conversion=self._pending_conversion,
        )

    @property
    def is_reset(self) -> bool:
        """Return *True* if the user has not modified this row (or explicitly clicked Reset)."""
        return not self._user_modified and self._pending_conversion is None

    def refresh(self, label: PlotAxisLabel) -> None:
        """Update this row when the underlying default label changes (e.g. after a replot).

        Always updates the "Current:" read-only display.  Only overwrites the
        editable name/unit fields when the user has not modified them.
        ``_original`` (the auto-generated default used by Reset) is only updated
        for auto-generated labels.
        """
        self._current_display.setText(str(label) or "<empty>")
        if not label.is_user_set:
            self._original = label
            if not self._user_modified:
                self._name_edit.blockSignals(True)
                self._name_edit.setText(label.name)
                self._name_edit.blockSignals(False)
                self._unit_edit.blockSignals(True)
                self._unit_edit.setText(label.unit)
                self._unit_edit.blockSignals(False)
                self._cur_unit_combo.setCurrentText(label.unit)
                self._refresh_convert_to()


class AxesCustomizationDialog(QDialog):
    """Dialog for customising plot axis labels and applying unit conversions.

    Each axis (x, y, colorbar) is represented by a :class:`_AxisRow` widget
    that lets the user edit the label name and unit independently, declare the
    current unit for columns where it was unknown, and apply registered unit
    conversions.

    The *title* remains a plain string (no unit).

    Parameters
    ----------
    current_labels:
        Dict with keys ``"title"`` (str), ``"xlabel"``, ``"ylabel"``,
        ``"cbar_label"`` (each a :class:`PlotAxisLabel`).
    """

    axes_applied = Signal(dict)

    def __init__(
        self,
        current_labels: dict | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Customise Axes")
        self.setMinimumWidth(560)

        if current_labels is None:
            current_labels = {}

        self._title_str: str = current_labels.get("title", "")
        self._auto_title: str = current_labels.get("title_auto", self._title_str)
        xlabel: PlotAxisLabel = current_labels.get("xlabel", PlotAxisLabel())
        ylabel: PlotAxisLabel = current_labels.get("ylabel", PlotAxisLabel())
        cbar:   PlotAxisLabel = current_labels.get("cbar_label", PlotAxisLabel())

        self._create_widgets(xlabel, ylabel, cbar)
        self._create_layout()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _create_widgets(
        self,
        xlabel: PlotAxisLabel,
        ylabel: PlotAxisLabel,
        cbar: PlotAxisLabel,
    ) -> None:
        # Title
        self._current_title_display = QLabel(self._title_str or "<empty>")
        self._current_title_display.setStyleSheet("color: gray; font-style: italic;")

        self._title_edit = QLineEdit(self._title_str)
        self._title_edit.setPlaceholderText("Plot title (LaTeX OK)")
        self._title_reset_btn = QPushButton("Reset")
        self._title_reset_btn.setFixedWidth(60)
        self._title_reset_btn.clicked.connect(self._reset_title)

        # Axis rows
        self._xlabel_row = _AxisRow(xlabel)
        self._ylabel_row = _AxisRow(ylabel)
        self._cbar_row   = _AxisRow(cbar)

        # Dialog buttons
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        )
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        apply_btn = self._button_box.button(QDialogButtonBox.Apply)
        if apply_btn:
            apply_btn.clicked.connect(self._emit_applied)

    def _create_layout(self) -> None:
        main = QVBoxLayout()
        main.addWidget(QLabel(
            "Customise axis labels. LaTeX is supported (e.g. $\\alpha$, $\\Delta G$).\n"
            "Leave fields as-is or click Reset to use auto-generated defaults."
        ))

        # Title group
        title_group = QGroupBox("Title")
        title_form = QFormLayout()
        title_form.setContentsMargins(0, 0, 0, 0)
        title_form.addRow("Current:", self._current_title_display)
        title_edit_row = QHBoxLayout()
        title_edit_row.addWidget(self._title_edit, 1)
        title_edit_row.addWidget(self._title_reset_btn)
        title_form.addRow("Title:", title_edit_row)
        title_group.setLayout(title_form)
        main.addWidget(title_group)

        # Axis groups
        for label_text, row_widget in (
            ("X-axis",   self._xlabel_row),
            ("Y-axis",   self._ylabel_row),
            ("Colorbar", self._cbar_row),
        ):
            grp = QGroupBox(label_text)
            grp_layout = QVBoxLayout()
            grp_layout.addWidget(row_widget)
            grp.setLayout(grp_layout)
            main.addWidget(grp)

        main.addWidget(self._button_box)
        self.setLayout(main)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_title(self) -> None:
        """Restore the title edit to the auto-generated title."""
        self._title_edit.setText(self._auto_title)

    # ------------------------------------------------------------------
    # Signal payload
    # ------------------------------------------------------------------

    def _build_result(self) -> dict:
        xlabel = self._xlabel_row.pending
        ylabel = self._ylabel_row.pending
        cbar   = self._cbar_row.pending

        # If the user hit Reset, clear is_user_set so _set_labels() recomputes
        if self._xlabel_row.is_reset:
            xlabel = replace(xlabel, is_user_set=False, conversion=None)
        if self._ylabel_row.is_reset:
            ylabel = replace(ylabel, is_user_set=False, conversion=None)
        if self._cbar_row.is_reset:
            cbar = replace(cbar, is_user_set=False, conversion=None)

        return {
            "title":      self._title_edit.text().strip(),
            "xlabel":     xlabel,
            "ylabel":     ylabel,
            "cbar_label": cbar,
        }

    def _emit_applied(self) -> None:
        result = self._build_result()
        self.axes_applied.emit(result)
        logger.debug("Axes applied: %s", result)

    def accept(self) -> None:
        self._emit_applied()
        super().accept()

    def refresh_labels(self, labels: dict) -> None:
        """Called via the ``labels_updated`` signal after each replot.

        Refreshes each axis row so the "Current:" display stays in sync with
        the live plot labels.  Edit fields are only updated when the user has
        not yet customised them.
        """
        for key, row in (
            ("xlabel",     self._xlabel_row),
            ("ylabel",     self._ylabel_row),
            ("cbar_label", self._cbar_row),
        ):
            label = labels.get(key)
            if isinstance(label, PlotAxisLabel):
                row.refresh(label)

        title = labels.get("title", "")
        if title:
            self._current_title_display.setText(title)
        auto_title = labels.get("title_auto", "")
        if auto_title:
            self._auto_title = auto_title
        if title and not self._title_edit.text():
            self._title_edit.setText(title)
