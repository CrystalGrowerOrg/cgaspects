"""Dialog for filtering dataframe data in plots."""

import logging
from typing import Dict, List, Optional

import pandas as pd
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("CA:DataFilterDialog")


class FilterRow(QWidget):
    """A single row representing a filter condition."""

    def __init__(self, columns: List[str], parent=None):
        super().__init__(parent)
        self.columns = columns

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Column selection
        self.column_combo = QComboBox()
        self.column_combo.addItems(self.columns)

        # Operator selection
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(
            ["==", "!=", ">", ">=", "<", "<=", "contains", "not contains"]
        )

        # Value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value...")

        # Remove button
        self.remove_button = QPushButton("Remove")
        self.remove_button.setMaximumWidth(80)

        layout.addWidget(self.column_combo, stretch=2)
        layout.addWidget(self.operator_combo, stretch=1)
        layout.addWidget(self.value_input, stretch=2)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def get_filter(self) -> Dict[str, str]:
        """Get the filter configuration as a dictionary."""
        return {
            "column": self.column_combo.currentText(),
            "operator": self.operator_combo.currentText(),
            "value": self.value_input.text(),
        }

    def set_filter(self, column: str, operator: str, value: str):
        """Set the filter configuration."""
        index = self.column_combo.findText(column)
        if index >= 0:
            self.column_combo.setCurrentIndex(index)

        index = self.operator_combo.findText(operator)
        if index >= 0:
            self.operator_combo.setCurrentIndex(index)

        self.value_input.setText(value)


class DataFilterDialog(QDialog):
    """Dialog for creating and managing data filters."""

    # Signal emitted when Apply button is clicked (now includes interaction filters)
    filters_applied = Signal(list, dict)  # (data_filters, interaction_filters)

    def __init__(
        self,
        df: Optional[pd.DataFrame] = None,
        current_filters: Optional[List[Dict]] = None,
        parent=None,
        site_analysis_data: Optional[dict] = None,
        current_interaction_filters: Optional[dict] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Data Filter")
        self.setModal(True)
        self.resize(800, 600)

        self.df = df
        self.site_analysis_data = site_analysis_data
        self.is_site_analysis = site_analysis_data is not None
        self.filter_rows: List[FilterRow] = []
        self.interaction_filter_widget = None

        # Set up columns based on data type
        if self.is_site_analysis:
            # For site analysis, provide filterable columns from site data
            self.columns = [
                "energy",
                "occupation",
                "coordination",
                "total_events",
                "total_population",
                "tile_type",
            ]
        elif df is not None:
            self.columns = list(df.columns)
        else:
            self.columns = []

        self.create_widgets()
        self.create_layout()

        # Load existing filters if provided
        if current_filters:
            for filter_config in current_filters:
                self.add_filter_row(filter_config)
        else:
            # Start with one empty filter row
            self.add_filter_row()

        # Load existing interaction filters if provided
        if self.interaction_filter_widget and current_interaction_filters:
            # Set the checkboxes based on current_interaction_filters
            for interaction_id, freqs in current_interaction_filters.items():
                for freq in freqs:
                    key = (interaction_id, freq)
                    if key in self.interaction_filter_widget.checkboxes:
                        self.interaction_filter_widget.checkboxes[key].setChecked(True)

    def create_widgets(self):
        """Create dialog widgets."""
        # Info label
        info_text = "Add filters to show only specific data points. Multiple filters are combined with AND logic."
        if self.is_site_analysis:
            info_text += "\n\nFor Site Analysis: Use 'Data Filters' tab for general site properties, 'Interaction Filters' tab for interaction patterns."
        self.info_label = QLabel(info_text)
        self.info_label.setWordWrap(True)

        # Tab widget for site analysis mode (data filters + interaction filters)
        if self.is_site_analysis:
            self.tab_widget = QTabWidget()
        else:
            self.tab_widget = None

        # Add filter button
        self.add_filter_button = QPushButton("Add Filter")
        self.add_filter_button.clicked.connect(lambda: self.add_filter_row())

        # Clear all button
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_filters)

        # Scroll area for filter rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)

        # Container for filter rows
        self.filter_container = QWidget()
        self.filter_layout = QVBoxLayout(self.filter_container)
        self.filter_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.filter_container)

        # Interaction filter widget for site analysis mode
        if self.is_site_analysis:
            from cgaspects.gui.widgets.interaction_filter_widget import InteractionFilterWidget

            self.interaction_filter_widget = InteractionFilterWidget()
            if self.site_analysis_data:
                logger.debug(f"Setting interaction data for {len(self.site_analysis_data)} file prefixes")
                self.interaction_filter_widget.set_interaction_data(self.site_analysis_data)
            else:
                logger.warning("No site_analysis_data available for interaction filter widget")

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Connect Apply button to emit signal without closing
        apply_button = self.button_box.button(QDialogButtonBox.Apply)
        if apply_button:
            apply_button.clicked.connect(self.apply_filters_and_emit)

    def create_layout(self):
        """Create dialog layout."""
        main_layout = QVBoxLayout()

        # Top section
        main_layout.addWidget(self.info_label)

        if self.is_site_analysis and self.tab_widget:
            # Create Data Filters tab
            data_filter_tab = QWidget()
            data_filter_layout = QVBoxLayout(data_filter_tab)

            # Button row for data filters
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.add_filter_button)
            button_layout.addWidget(self.clear_all_button)
            button_layout.addStretch()
            data_filter_layout.addLayout(button_layout)

            # Filter rows area
            data_filter_layout.addWidget(self.scroll_area)

            self.tab_widget.addTab(data_filter_tab, "Data Filters")

            # Create Interaction Filters tab
            if self.interaction_filter_widget:
                self.tab_widget.addTab(self.interaction_filter_widget, "Interaction Filters")

            main_layout.addWidget(self.tab_widget)
        else:
            # Standard layout for non-site-analysis mode
            # Button row
            button_layout = QHBoxLayout()
            button_layout.addWidget(self.add_filter_button)
            button_layout.addWidget(self.clear_all_button)
            button_layout.addStretch()
            main_layout.addLayout(button_layout)

            # Filter rows area
            main_layout.addWidget(self.scroll_area)

        # Status
        main_layout.addWidget(self.status_label)

        # Buttons
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def add_filter_row(self, filter_config: Optional[Dict] = None):
        """Add a new filter row."""
        filter_row = FilterRow(self.columns, self)
        filter_row.remove_button.clicked.connect(lambda: self.remove_filter_row(filter_row))

        # Set values if config provided
        if filter_config:
            filter_row.set_filter(
                filter_config.get("column", ""),
                filter_config.get("operator", "=="),
                filter_config.get("value", ""),
            )

        self.filter_rows.append(filter_row)
        self.filter_layout.addWidget(filter_row)

    def remove_filter_row(self, filter_row: FilterRow):
        """Remove a filter row."""
        if filter_row in self.filter_rows:
            self.filter_rows.remove(filter_row)
            self.filter_layout.removeWidget(filter_row)
            filter_row.deleteLater()

    def clear_all_filters(self):
        """Clear all filter rows."""
        for filter_row in self.filter_rows[:]:  # Copy list to avoid modification during iteration
            self.remove_filter_row(filter_row)
        # Add one empty row
        self.add_filter_row()

    def get_filters(self) -> List[Dict[str, str]]:
        """Get all data filter configurations."""
        filters = []
        for filter_row in self.filter_rows:
            filter_config = filter_row.get_filter()
            # Only include filters with non-empty values
            if filter_config["value"].strip():
                filters.append(filter_config)
        return filters

    def get_interaction_filters(self) -> dict:
        """Get interaction filter configurations (for site analysis mode)."""
        if self.interaction_filter_widget:
            filters = self.interaction_filter_widget.get_selected_filters()
            logger.debug(f"Retrieved interaction filters: {filters}")
            return filters
        logger.debug("No interaction filter widget available")
        return {}

    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all filters to a dataframe and return the filtered result."""
        filters = self.get_filters()

        if not filters:
            return df

        filtered_df = df.copy()

        for filter_config in filters:
            column = filter_config["column"]
            operator = filter_config["operator"]
            value_str = filter_config["value"]

            if column not in filtered_df.columns:
                logger.warning(f"Column '{column}' not found in dataframe")
                continue

            try:
                # Try to convert value to numeric if the column is numeric
                if pd.api.types.is_numeric_dtype(filtered_df[column]):
                    value = pd.to_numeric(value_str)
                else:
                    value = value_str

                # Apply the filter based on operator
                if operator == "==":
                    mask = filtered_df[column] == value
                elif operator == "!=":
                    mask = filtered_df[column] != value
                elif operator == ">":
                    mask = filtered_df[column] > value
                elif operator == ">=":
                    mask = filtered_df[column] >= value
                elif operator == "<":
                    mask = filtered_df[column] < value
                elif operator == "<=":
                    mask = filtered_df[column] <= value
                elif operator == "contains":
                    mask = filtered_df[column].astype(str).str.contains(str(value), case=False)
                elif operator == "not contains":
                    mask = ~filtered_df[column].astype(str).str.contains(str(value), case=False)
                else:
                    logger.warning(f"Unknown operator: {operator}")
                    continue

                filtered_df = filtered_df[mask]

            except Exception as e:
                logger.error(f"Error applying filter {filter_config}: {e}")
                continue

        return filtered_df

    def validate_and_update_status(self) -> bool:
        """Validate filters and update status label.

        Returns:
            True if validation succeeded, False otherwise
        """
        filters = self.get_filters()

        if not filters:
            self.status_label.setText("No filters defined. Click OK to show all data.")
            return True
        else:
            # Test the filters
            try:
                # Skip DataFrame validation for Site Analysis mode
                if self.is_site_analysis or self.df is None:
                    self.status_label.setText(
                        f"{len(filters)} filter(s) will be applied to site data."
                    )
                    logger.info(f"Site analysis filter validation: {len(filters)} filters defined")
                    return True

                filtered_df = self.apply_filters(self.df)
                original_count = len(self.df)
                filtered_count = len(filtered_df)
                self.status_label.setText(
                    f"Filters will show {filtered_count} of {original_count} data points."
                )
                logger.info(f"Filter validation: {filtered_count}/{original_count} rows pass filters")
                return True
            except Exception as e:
                self.status_label.setText(f"Error validating filters: {e}")
                logger.error(f"Filter validation error: {e}")
                return False

    def apply_filters_and_emit(self):
        """Apply filters and emit signal without closing the dialog."""
        if self.validate_and_update_status():
            data_filters = self.get_filters()
            interaction_filters = self.get_interaction_filters()
            self.filters_applied.emit(data_filters, interaction_filters)
            logger.debug(f"Applied data filters: {data_filters}, interaction filters: {interaction_filters}")

    def accept(self):
        """Validate and accept the dialog."""
        if not self.validate_and_update_status():
            return

        # Emit filters before closing
        data_filters = self.get_filters()
        interaction_filters = self.get_interaction_filters()
        self.filters_applied.emit(data_filters, interaction_filters)
        logger.debug(f"Accepted with data filters: {data_filters}, interaction filters: {interaction_filters}")

        super().accept()
