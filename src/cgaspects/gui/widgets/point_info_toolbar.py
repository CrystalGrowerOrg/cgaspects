"""Collapsible side panel for displaying point information and managing selections."""

import logging
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)

logger = logging.getLogger("CA:PointInfoToolbar")


class PointInfoToolbar(QWidget):
    """A collapsible side panel that displays point information and selection controls."""

    deleteSelectedRequested = Signal()  # Emitted when delete button is clicked
    clearSelectionRequested = Signal()  # Emitted when clear selection is clicked
    exportXYZRequested = Signal()  # Emitted when export XYZ is requested

    EXPANDED_WIDTH = 200
    COLLAPSED_WIDTH = 28

    def __init__(self, parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._hovered_point_index = None
        self._hovered_point_data = None
        self._selected_count = 0

        self._setup_ui()

    def _setup_ui(self):
        """Set up the side panel UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Toggle button strip (always visible)
        self._toggle_strip = QFrame()
        self._toggle_strip.setFixedWidth(self.COLLAPSED_WIDTH)
        self._toggle_strip.setFrameShape(QFrame.StyledPanel)
        toggle_layout = QVBoxLayout(self._toggle_strip)
        toggle_layout.setContentsMargins(2, 4, 2, 4)
        toggle_layout.setSpacing(4)

        # Toggle button
        self._toggle_btn = QPushButton("◀")
        self._toggle_btn.setFixedSize(24, 24)
        self._toggle_btn.setFlat(True)
        self._toggle_btn.clicked.connect(self._toggle_collapsed)
        self._toggle_btn.setToolTip("Collapse/Expand panel")
        toggle_layout.addWidget(self._toggle_btn)

        # Selection count in collapsed view
        self._collapsed_count = QLabel("0")
        self._collapsed_count.setAlignment(Qt.AlignCenter)
        self._collapsed_count.setStyleSheet("font-weight: bold; font-size: 11px;")
        self._collapsed_count.setToolTip("Selected points")
        toggle_layout.addWidget(self._collapsed_count)

        toggle_layout.addStretch()

        main_layout.addWidget(self._toggle_strip)

        # Content panel (collapsible)
        self._content = QFrame()
        self._content.setFixedWidth(self.EXPANDED_WIDTH - self.COLLAPSED_WIDTH)
        self._content.setFrameShape(QFrame.StyledPanel)
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(8)

        # Title
        title_label = QLabel("Point Info")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        content_layout.addWidget(title_label)

        # Hover info section
        hover_title = QLabel("Hovered:")
        hover_title.setStyleSheet("font-weight: bold; font-size: 10px;")
        content_layout.addWidget(hover_title)

        self._hover_info_label = QLabel("Hover over points")
        self._hover_info_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        self._hover_info_label.setWordWrap(True)
        content_layout.addWidget(self._hover_info_label)

        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(separator1)

        # Selection section
        self._selection_label = QLabel("Selected: 0")
        self._selection_label.setStyleSheet("font-weight: bold; font-size: 10px;")
        content_layout.addWidget(self._selection_label)

        self._selected_list_label = QLabel("")
        self._selected_list_label.setStyleSheet("font-family: monospace; font-size: 9px;")
        self._selected_list_label.setWordWrap(True)
        content_layout.addWidget(self._selected_list_label)

        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(separator2)

        # Buttons (vertical layout)
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setEnabled(False)
        self._clear_btn.clicked.connect(self.clearSelectionRequested.emit)
        content_layout.addWidget(self._clear_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self.deleteSelectedRequested.emit)
        content_layout.addWidget(self._delete_btn)

        self._export_btn = QPushButton("Export XYZ")
        self._export_btn.setToolTip("Export point cloud to XYZ file")
        self._export_btn.clicked.connect(self.exportXYZRequested.emit)
        content_layout.addWidget(self._export_btn)

        content_layout.addStretch()

        # Help text
        help_label = QLabel("Click: select\nCtrl+Click: toggle\nShift+Click: range")
        help_label.setStyleSheet("font-size: 9px;")
        content_layout.addWidget(help_label)

        main_layout.addWidget(self._content)

        # Set size policies
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(self.EXPANDED_WIDTH)

    def _toggle_collapsed(self):
        """Toggle the collapsed state of the panel."""
        self._collapsed = not self._collapsed
        self._content.setVisible(not self._collapsed)
        self._toggle_btn.setText("◀" if self._collapsed else "▶")
        self.setFixedWidth(self.COLLAPSED_WIDTH if self._collapsed else self.EXPANDED_WIDTH)

    def set_collapsed(self, collapsed: bool):
        """Set the collapsed state."""
        self._collapsed = collapsed
        self._content.setVisible(not collapsed)
        self._toggle_btn.setText("◀" if collapsed else "▶")
        self.setFixedWidth(self.COLLAPSED_WIDTH if collapsed else self.EXPANDED_WIDTH)

    def is_collapsed(self) -> bool:
        """Return whether the panel is collapsed."""
        return self._collapsed

    def update_hover_info(self, point_index: int | None, point_data: dict | None):
        """Update the hover information display."""
        self._hovered_point_index = point_index
        self._hovered_point_data = point_data

        if point_index is None or point_data is None:
            self._hover_info_label.setText("Hover over points")
            return

        info_lines = [f"#{point_index}"]

        if "position" in point_data:
            pos = point_data["position"]
            info_lines.append(f"({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")

        if "type" in point_data:
            info_lines.append(f"Type: {point_data['type']}")

        if "number" in point_data:
            info_lines.append(f"Number: {int(point_data['number'])}")

        if "layer" in point_data:
            info_lines.append(f"Layer: {int(point_data['layer'])}")

        if "site" in point_data and point_data["site"] is not None:
            info_lines.append(f"Site: {int(point_data['site'])}")

        if "energy" in point_data and point_data["energy"] is not None:
            info_lines.append(f"Energy: {point_data['energy']:.4f}")

        self._hover_info_label.setText("\n".join(info_lines))

    def update_selection_info(self, selected_indices: set):
        """Update the selection information display."""
        self._selected_count = len(selected_indices)
        self._selection_label.setText(f"Selected: {self._selected_count}")
        self._collapsed_count.setText(str(self._selected_count))

        if self._selected_count == 0:
            self._selected_list_label.setText("")
            self._clear_btn.setEnabled(False)
            self._delete_btn.setEnabled(False)
        else:
            # Show list of selected indices (compact format)
            sorted_indices = sorted(selected_indices)
            if len(sorted_indices) <= 10:
                indices_str = ", ".join(str(i) for i in sorted_indices)
            else:
                first_5 = ", ".join(str(i) for i in sorted_indices[:5])
                indices_str = f"{first_5}, ..."

            self._selected_list_label.setText(indices_str)
            self._clear_btn.setEnabled(True)
            self._delete_btn.setEnabled(True)

    def get_selected_count(self) -> int:
        """Return the number of selected points."""
        return self._selected_count
