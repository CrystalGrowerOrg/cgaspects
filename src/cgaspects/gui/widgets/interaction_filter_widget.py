"""
Interaction frequency filter widget for site analysis mode.

This widget provides a grid of checkboxes for filtering sites based on
their interaction types and frequencies.
"""

import logging
from typing import Dict, Set, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("CA:InteractionFilterWidget")


class InteractionFilterWidget(QWidget):
    """Widget for filtering sites by interaction types and frequencies."""

    # Signal emitted when filter selection changes
    # Emits a dict: {interaction_id: set of selected frequencies (or "Any")}
    filter_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.interaction_data = {}  # {interaction_id: max_frequency}
        self.checkboxes = {}  # {(interaction_id, frequency): QCheckBox}

        self._create_widgets()
        self._create_layout()

    def _create_widgets(self):
        """Create the main widgets."""
        # Group box to contain the filter grid
        self.group_box = QGroupBox("Interaction Frequency Filter")
        self.group_box_layout = QVBoxLayout()

        # Scroll area for the checkbox grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(150)
        self.scroll_area.setMaximumHeight(300)

        # Container widget for the grid
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        self.grid_container.setLayout(self.grid_layout)

        self.scroll_area.setWidget(self.grid_container)
        self.group_box_layout.addWidget(self.scroll_area)
        self.group_box.setLayout(self.group_box_layout)

    def _create_layout(self):
        """Create the layout."""
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.group_box)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def set_interaction_data(self, site_analysis_data: dict):
        """
        Analyze site analysis data to determine available interactions and their frequencies.

        Args:
            site_analysis_data: Dictionary of site analysis data for all file prefixes
        """
        if not site_analysis_data:
            logger.warning("No site analysis data provided")
            return

        # Collect all interactions and their maximum frequencies across all sites
        interaction_freqs = {}  # {interaction_id: max_frequency}

        for _, dataset in site_analysis_data.items():
            sites_dict = dataset.get("sites", {})

            for _, site_data in sites_dict.items():
                interactions = site_data.get("interactions", {})

                for interaction_id, frequency in interactions.items():
                    interaction_id = int(interaction_id)
                    if interaction_id not in interaction_freqs:
                        interaction_freqs[interaction_id] = frequency
                    else:
                        interaction_freqs[interaction_id] = max(
                            interaction_freqs[interaction_id], frequency
                        )

        if not interaction_freqs:
            logger.info("No interaction data found in site analysis")
            self.interaction_data = {}
            self._rebuild_grid()
            return

        self.interaction_data = interaction_freqs
        logger.info(f"Found {len(interaction_freqs)} interaction types: {interaction_freqs}")
        self._rebuild_grid()

    def _rebuild_grid(self):
        """Rebuild the checkbox grid based on current interaction data."""
        # Clear existing checkboxes
        for checkbox in self.checkboxes.values():
            checkbox.deleteLater()
        self.checkboxes.clear()

        # Clear the grid layout
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.interaction_data:
            # Show a message if no interaction data
            label = QLabel(
                "No interaction data available.\nLoad count files to enable this filter."
            )
            label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(label, 0, 0)
            return

        # Sort interaction IDs for consistent ordering
        sorted_interactions = sorted(self.interaction_data.keys())

        # Create header row (interaction IDs)
        for col_idx, interaction_id in enumerate(sorted_interactions):
            header_label = QLabel(f"<b>Int. {interaction_id}</b>")
            header_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(header_label, 0, col_idx + 1)

        # Create rows for each frequency
        # First, find the maximum frequency across all interactions
        max_freq = max(self.interaction_data.values()) if self.interaction_data else 0

        row_idx = 1

        # Add "Any" row first for each interaction
        for col_idx, interaction_id in enumerate(sorted_interactions):
            checkbox = QCheckBox(f"Any ({interaction_id})")
            checkbox.setToolTip(f"Select all frequencies for interaction {interaction_id}")
            checkbox.stateChanged.connect(
                lambda state, iid=interaction_id: self._on_any_changed(iid, state)
            )
            self.grid_layout.addWidget(checkbox, row_idx, col_idx + 1)
            self.checkboxes[(interaction_id, "Any")] = checkbox

        row_idx += 1

        # Add frequency rows (1 to max_freq)
        for freq in range(1, max_freq + 1):
            # Row label
            row_label = QLabel(f"<b>Freq. {freq}</b>")
            row_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.grid_layout.addWidget(row_label, row_idx, 0)

            # Add checkbox for each interaction at this frequency
            for col_idx, interaction_id in enumerate(sorted_interactions):
                max_freq_for_interaction = self.interaction_data[interaction_id]

                if freq <= max_freq_for_interaction:
                    checkbox = QCheckBox(f"{freq}({interaction_id})")
                    checkbox.setToolTip(
                        f"Select sites with interaction {interaction_id} at frequency {freq}"
                    )
                    checkbox.stateChanged.connect(self._on_checkbox_changed)
                    self.grid_layout.addWidget(checkbox, row_idx, col_idx + 1)
                    self.checkboxes[(interaction_id, freq)] = checkbox
                else:
                    # Empty cell if this interaction doesn't have this frequency
                    spacer = QLabel("")
                    self.grid_layout.addWidget(spacer, row_idx, col_idx + 1)

            row_idx += 1

        logger.debug(
            f"Created grid with {len(sorted_interactions)} interactions and {max_freq} frequencies"
        )

    def _on_any_changed(self, interaction_id: int, state: int):
        """Handle changes to the 'Any' checkbox for an interaction.

        Args:
            interaction_id: The interaction ID
            state: Qt.CheckState value
        """
        is_checked = state == Qt.Checked
        max_freq = self.interaction_data.get(interaction_id, 0)

        # Block signals to prevent recursive updates
        for freq in range(1, max_freq + 1):
            key = (interaction_id, freq)
            if key in self.checkboxes:
                checkbox = self.checkboxes[key]
                checkbox.blockSignals(True)
                checkbox.setChecked(is_checked)
                checkbox.blockSignals(False)

        # Emit filter changed signal
        self._on_checkbox_changed()

    def _on_checkbox_changed(self):
        """Handle checkbox state changes and emit filter_changed signal."""
        selected_filters = self.get_selected_filters()
        logger.debug(f"Filter selection changed: {selected_filters}")
        self.filter_changed.emit(selected_filters)

    def get_selected_filters(self) -> Dict[int, list]:
        """
        Get the currently selected interaction filters.

        Returns:
            Dictionary mapping interaction_id to list of selected frequencies.
            If "Any" is selected, the list will contain the string "Any".
            Empty dict means no filters are active (show all sites).
        """
        filters = {}

        for (interaction_id, freq), checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                if interaction_id not in filters:
                    filters[interaction_id] = set()
                filters[interaction_id].add(freq)
                logger.info(
                    f"Checkbox checked - interaction_id: {interaction_id}, freq: {freq}, current filters: {filters}"
                )

        # Clean up: if "Any" is selected, remove specific frequencies
        for interaction_id in list(filters.keys()):
            if "Any" in filters[interaction_id]:
                filters[interaction_id] = {"Any"}

        print(filters)

        return filters

    def clear_filters(self):
        """Uncheck all filter checkboxes."""
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)

        # Emit filter changed signal
        self.filter_changed.emit({})

    def has_filters_active(self) -> bool:
        """Check if any filters are currently active."""
        return len(self.get_selected_filters()) > 0
