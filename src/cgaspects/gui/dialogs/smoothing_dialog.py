"""Dialog for configuring smoothing, interpolation, and extrapolation for growth rate data."""

import logging
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QScrollArea,
    QWidget,
    QGridLayout,
)
from PySide6.QtCore import Qt

logger = logging.getLogger("CA:SmoothingDialog")


class SeriesSmoothingWidget(QWidget):
    """Widget for configuring smoothing/interpolation/extrapolation for a single data series."""

    def __init__(self, series_name, parent=None):
        super().__init__(parent)
        self.series_name = series_name
        self._create_ui()
        self._connect_signals()

    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Series name label
        name_label = QLabel(f"<b>{self.series_name}</b>")
        layout.addWidget(name_label)

        # Enable checkbox
        self.enabled_checkbox = QCheckBox("Enable processing for this series")
        self.enabled_checkbox.setChecked(False)
        layout.addWidget(self.enabled_checkbox)

        # Container for settings (disabled by default)
        self.settings_widget = QWidget()
        settings_layout = QGridLayout(self.settings_widget)
        settings_layout.setContentsMargins(20, 0, 0, 0)

        row = 0

        # Smoothing section
        smoothing_label = QLabel("Smoothing:")
        smoothing_label.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(smoothing_label, row, 0, 1, 2)
        row += 1

        settings_layout.addWidget(QLabel("Method:"), row, 0)
        self.smoothing_method = QComboBox()
        self.smoothing_method.addItems([
            "None",
            "Moving Average",
            "Savitzky-Golay",
            "Gaussian",
            "LOWESS"
        ])
        settings_layout.addWidget(self.smoothing_method, row, 1)
        row += 1

        settings_layout.addWidget(QLabel("Window Size:"), row, 0)
        self.window_size = QSpinBox()
        self.window_size.setRange(3, 51)
        self.window_size.setValue(5)
        self.window_size.setSingleStep(2)  # Keep it odd
        self.window_size.setToolTip("Window size for smoothing (must be odd for some methods)")
        settings_layout.addWidget(self.window_size, row, 1)
        row += 1

        settings_layout.addWidget(QLabel("Polynomial Order:"), row, 0)
        self.poly_order = QSpinBox()
        self.poly_order.setRange(1, 5)
        self.poly_order.setValue(2)
        self.poly_order.setToolTip("Polynomial order for Savitzky-Golay filter")
        settings_layout.addWidget(self.poly_order, row, 1)
        row += 1

        # Interpolation section
        interp_label = QLabel("Interpolation:")
        interp_label.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(interp_label, row, 0, 1, 2)
        row += 1

        settings_layout.addWidget(QLabel("Method:"), row, 0)
        self.interp_method = QComboBox()
        self.interp_method.addItems([
            "None",
            "Linear",
            "Cubic Spline",
            "Polynomial",
            "Pchip"
        ])
        settings_layout.addWidget(self.interp_method, row, 1)
        row += 1

        settings_layout.addWidget(QLabel("Points:"), row, 0)
        self.interp_points = QSpinBox()
        self.interp_points.setRange(10, 1000)
        self.interp_points.setValue(100)
        self.interp_points.setToolTip("Number of interpolated points")
        settings_layout.addWidget(self.interp_points, row, 1)
        row += 1

        # Extrapolation section
        extrap_label = QLabel("Extrapolation:")
        extrap_label.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(extrap_label, row, 0, 1, 2)
        row += 1

        self.extrap_enabled = QCheckBox("Enable Extrapolation")
        self.extrap_enabled.setChecked(False)
        settings_layout.addWidget(self.extrap_enabled, row, 0, 1, 2)
        row += 1

        settings_layout.addWidget(QLabel("Method:"), row, 0)
        self.extrap_method = QComboBox()
        self.extrap_method.addItems([
            "Linear",
            "Polynomial",
            "Exponential"
        ])
        settings_layout.addWidget(self.extrap_method, row, 1)
        row += 1

        settings_layout.addWidget(QLabel("Extend by (%):"), row, 0)
        self.extrap_percent = QDoubleSpinBox()
        self.extrap_percent.setRange(1.0, 100.0)
        self.extrap_percent.setValue(20.0)
        self.extrap_percent.setSuffix("%")
        self.extrap_percent.setToolTip("Percentage of data range to extend on each side")
        settings_layout.addWidget(self.extrap_percent, row, 1)
        row += 1

        settings_layout.addWidget(QLabel("Polynomial Order:"), row, 0)
        self.extrap_poly_order = QSpinBox()
        self.extrap_poly_order.setRange(1, 5)
        self.extrap_poly_order.setValue(2)
        self.extrap_poly_order.setToolTip("Polynomial order for polynomial extrapolation")
        settings_layout.addWidget(self.extrap_poly_order, row, 1)
        row += 1

        layout.addWidget(self.settings_widget)
        self.settings_widget.setEnabled(False)

    def _connect_signals(self):
        """Connect signals for enabling/disabling controls."""
        self.enabled_checkbox.toggled.connect(self.settings_widget.setEnabled)
        self.smoothing_method.currentTextChanged.connect(self._update_smoothing_controls)
        self.interp_method.currentTextChanged.connect(self._update_interp_controls)
        self.extrap_enabled.toggled.connect(self._update_extrap_controls)
        self.extrap_method.currentTextChanged.connect(self._update_extrap_controls)

    def _update_smoothing_controls(self):
        """Enable/disable smoothing controls based on selected method."""
        method = self.smoothing_method.currentText()
        self.window_size.setEnabled(method != "None")
        self.poly_order.setEnabled(method == "Savitzky-Golay")

    def _update_interp_controls(self):
        """Enable/disable interpolation controls based on selected method."""
        method = self.interp_method.currentText()
        self.interp_points.setEnabled(method != "None")

    def _update_extrap_controls(self):
        """Enable/disable extrapolation controls based on settings."""
        enabled = self.extrap_enabled.isChecked()
        self.extrap_method.setEnabled(enabled)
        self.extrap_percent.setEnabled(enabled)
        method = self.extrap_method.currentText()
        self.extrap_poly_order.setEnabled(enabled and method == "Polynomial")

    def is_enabled(self):
        """Check if processing is enabled for this series."""
        return self.enabled_checkbox.isChecked()

    def get_config(self):
        """Get the current configuration as a dictionary."""
        if not self.is_enabled():
            return None

        config = {
            "smoothing": {
                "method": self.smoothing_method.currentText(),
                "window_size": self.window_size.value(),
                "poly_order": self.poly_order.value(),
            },
            "interpolation": {
                "method": self.interp_method.currentText(),
                "points": self.interp_points.value(),
            },
            "extrapolation": {
                "enabled": self.extrap_enabled.isChecked(),
                "method": self.extrap_method.currentText(),
                "percent": self.extrap_percent.value(),
                "poly_order": self.extrap_poly_order.value(),
            }
        }
        return config

    def set_config(self, config):
        """Set configuration from a dictionary."""
        if config is None:
            self.enabled_checkbox.setChecked(False)
            return

        self.enabled_checkbox.setChecked(True)

        if "smoothing" in config:
            s = config["smoothing"]
            idx = self.smoothing_method.findText(s.get("method", "None"))
            if idx >= 0:
                self.smoothing_method.setCurrentIndex(idx)
            self.window_size.setValue(s.get("window_size", 5))
            self.poly_order.setValue(s.get("poly_order", 2))

        if "interpolation" in config:
            i = config["interpolation"]
            idx = self.interp_method.findText(i.get("method", "None"))
            if idx >= 0:
                self.interp_method.setCurrentIndex(idx)
            self.interp_points.setValue(i.get("points", 100))

        if "extrapolation" in config:
            e = config["extrapolation"]
            self.extrap_enabled.setChecked(e.get("enabled", False))
            idx = self.extrap_method.findText(e.get("method", "Linear"))
            if idx >= 0:
                self.extrap_method.setCurrentIndex(idx)
            self.extrap_percent.setValue(e.get("percent", 20.0))
            self.extrap_poly_order.setValue(e.get("poly_order", 2))


class SmoothingDialog(QDialog):
    """Dialog for configuring smoothing, interpolation, and extrapolation for multiple data series."""

    def __init__(self, series_names, existing_configs=None, parent=None):
        """
        Initialize the smoothing dialog.

        Args:
            series_names: List of series names (column names)
            existing_configs: Dict mapping series names to their existing configurations
            parent: Parent widget
        """
        super().__init__(parent)
        self.series_names = series_names
        self.existing_configs = existing_configs or {}
        self.series_widgets = {}

        self.setWindowTitle("Data Smoothing & Extrapolation")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)

        self._create_ui()
        self._load_configs()

    def _create_ui(self):
        """Create the user interface."""
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            "Configure smoothing, interpolation, and extrapolation for each data series.\n"
            "Enable processing for individual series and adjust parameters as needed."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Legend display options
        legend_group = QGroupBox("Legend Display")
        legend_layout = QVBoxLayout(legend_group)

        self.legend_mode = QComboBox()
        self.legend_mode.addItems([
            "Show Both Original and Processed",
            "Show Processed Only",
            "Show Original Only"
        ])
        self.legend_mode.setCurrentIndex(0)
        legend_layout.addWidget(QLabel("Display Mode:"))
        legend_layout.addWidget(self.legend_mode)

        layout.addWidget(legend_group)

        # Scroll area for series widgets
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Create a widget for each series
        for series_name in self.series_names:
            series_widget = SeriesSmoothingWidget(series_name)
            self.series_widgets[series_name] = series_widget

            # Add separator
            group = QGroupBox()
            group_layout = QVBoxLayout(group)
            group_layout.addWidget(series_widget)
            scroll_layout.addWidget(group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()

        self.apply_all_button = QPushButton("Apply Same Settings to All")
        self.apply_all_button.setToolTip("Apply the settings from the first enabled series to all series")
        self.apply_all_button.clicked.connect(self._apply_to_all)
        button_layout.addWidget(self.apply_all_button)

        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_configs(self):
        """Load existing configurations into the widgets."""
        for series_name, widget in self.series_widgets.items():
            if series_name in self.existing_configs:
                widget.set_config(self.existing_configs[series_name])

    def _apply_to_all(self):
        """Apply settings from first enabled series to all series."""
        # Find the first enabled series
        template_config = None
        for series_name in self.series_names:
            widget = self.series_widgets[series_name]
            if widget.is_enabled():
                template_config = widget.get_config()
                break

        if template_config is None:
            # If no series is enabled, just enable all with default settings
            for widget in self.series_widgets.values():
                widget.enabled_checkbox.setChecked(True)
        else:
            # Apply template to all series
            for widget in self.series_widgets.values():
                widget.set_config(template_config)

    def get_configs(self):
        """
        Get all series configurations.

        Returns:
            Tuple of (series_configs_dict, legend_mode_str)
            where series_configs_dict maps series names to their configs
        """
        configs = {}
        for series_name, widget in self.series_widgets.items():
            config = widget.get_config()
            if config is not None:
                configs[series_name] = config

        legend_mode = self.legend_mode.currentText()
        return configs, legend_mode
