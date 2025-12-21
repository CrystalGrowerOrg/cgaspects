"""
Time-series widget for site analysis mode.

This widget provides controls for navigating through time-series data
in site analysis plots, including:
- Dropdown to select time parameter (supersaturation/time/iterations)
- Horizontal scroll bar for navigation
- Play/pause button for animation
"""

import logging
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpacerItem,
    QSizePolicy,
    QWidget,
)

logger = logging.getLogger("CA:TimeSeriesWidget")


class TimeSeriesWidget(QWidget):
    """Widget for controlling time-series navigation in site analysis plots."""

    # Signal emitted when the time point changes (emits the index)
    time_point_changed = Signal(int)
    # Signal emitted when the plotting mode changes
    plotting_mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.time_data = None
        self.current_index = 0
        self.is_playing = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._advance_time)

        self._create_widgets()
        self._create_layout()
        self._connect_signals()

    def _create_widgets(self):
        """Create the widgets for the time-series control."""
        # Plotting mode label and dropdown
        self.mode_label = QLabel("Plot Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Total Events",
            "Total Population",
            "Events per Step",
            "Population per Step"
        ])
        self.mode_combo.setToolTip("Select what data to plot")

        # Label
        self.label = QLabel("Time Parameter:")

        # Dropdown for selecting time parameter
        self.parameter_combo = QComboBox()
        self.parameter_combo.addItems(["Supersaturation", "Time", "Iterations"])
        self.parameter_combo.setToolTip("Select which parameter to use for time-series navigation")

        # Horizontal slider for time navigation
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(100)  # Will be updated based on data
        self.time_slider.setValue(0)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.setTickInterval(10)
        self.time_slider.setToolTip("Navigate through time points")

        # Label to show current value
        self.value_label = QLabel("0 / 0")
        self.value_label.setMinimumWidth(100)
        self.value_label.setAlignment(Qt.AlignCenter)

        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.setCheckable(True)
        self.play_button.setToolTip("Play/Pause time-series animation")
        self.play_button.setMaximumWidth(80)

    def _create_layout(self):
        """Create the layout for the widget."""
        layout = QHBoxLayout()
        layout.addWidget(self.mode_label)
        layout.addWidget(self.mode_combo)
        layout.addWidget(self.label)
        layout.addWidget(self.parameter_combo)
        layout.addWidget(self.time_slider)
        layout.addWidget(self.value_label)
        layout.addWidget(self.play_button)
        # Add horizontal spacer on the right to prevent jumping when widgets are hidden
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _connect_signals(self):
        """Connect widget signals to slots."""
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.parameter_combo.currentIndexChanged.connect(self._on_parameter_changed)
        self.time_slider.valueChanged.connect(self._on_slider_changed)
        self.play_button.clicked.connect(self._on_play_clicked)

    def set_time_data(self, supersaturation, time, iterations):
        """
        Set the time-series data.

        Args:
            supersaturation: numpy array of supersaturation values
            time: numpy array of time values
            iterations: numpy array of iteration values
        """
        self.time_data = {
            "supersaturation": supersaturation,
            "time": time,
            "iterations": iterations,
        }

        # Update slider range based on data length
        self._update_slider_range()
        self._update_value_label()

    def _update_slider_range(self):
        """Update the slider range based on the selected parameter."""
        if self.time_data is None:
            return

        param_name = self._get_current_parameter_name()
        data = self.time_data.get(param_name)

        if data is not None and len(data) > 0:
            self.time_slider.setMaximum(len(data) - 1)
            # Update tick interval based on data length
            tick_interval = max(1, len(data) // 10)
            self.time_slider.setTickInterval(tick_interval)
        else:
            self.time_slider.setMaximum(0)

    def _get_current_parameter_name(self):
        """Get the current parameter name from the combo box."""
        return self.parameter_combo.currentText().lower()

    def _on_mode_changed(self, index):
        """Handle plotting mode change."""
        mode = self.mode_combo.currentText()
        logger.debug(f"Plotting mode changed to: {mode}")

        # Show/hide slider based on mode
        is_per_step = "per Step" in mode
        self.label.setVisible(is_per_step)
        self.parameter_combo.setVisible(is_per_step)
        self.time_slider.setVisible(is_per_step)
        self.value_label.setVisible(is_per_step)
        self.play_button.setVisible(is_per_step)

        # Emit signal
        self.plotting_mode_changed.emit(mode)

    def _on_parameter_changed(self, index):
        """Handle parameter selection change."""
        logger.debug(f"Parameter changed to: {self.parameter_combo.currentText()}")
        self._update_slider_range()
        self._update_value_label()
        # Emit signal with current index
        self.time_point_changed.emit(self.current_index)

    def _on_slider_changed(self, value):
        """Handle slider value change."""
        self.current_index = value
        self._update_value_label()
        logger.debug(f"Time point changed to index: {value}")
        # Emit signal
        self.time_point_changed.emit(value)

    def _update_value_label(self):
        """Update the value label with current time point information."""
        if self.time_data is None:
            self.value_label.setText("0 / 0")
            return

        param_name = self._get_current_parameter_name()
        data = self.time_data.get(param_name)

        if data is not None and len(data) > 0:
            current_value = data[self.current_index]
            total_points = len(data)
            self.value_label.setText(f"{current_value:.2f} ({self.current_index + 1}/{total_points})")
        else:
            self.value_label.setText("0 / 0")

    def _on_play_clicked(self, checked):
        """Handle play/pause button click."""
        if checked:
            self.play_button.setText("Pause")
            self.is_playing = True
            self.timer.start(500)  # Update every 500ms
            logger.debug("Started time-series animation")
        else:
            self.play_button.setText("Play")
            self.is_playing = False
            self.timer.stop()
            logger.debug("Paused time-series animation")

    def _advance_time(self):
        """Advance to the next time point (for animation)."""
        if self.time_data is None:
            return

        param_name = self._get_current_parameter_name()
        data = self.time_data.get(param_name)

        if data is None or len(data) == 0:
            return

        # Advance to next time point
        next_index = self.current_index + 1

        # Loop back to start if at the end
        if next_index >= len(data):
            next_index = 0

        self.time_slider.setValue(next_index)

    def get_current_time_point(self):
        """
        Get the current time point value and index.

        Returns:
            tuple: (parameter_name, current_value, current_index)
        """
        if self.time_data is None:
            return None, None, 0

        param_name = self._get_current_parameter_name()
        data = self.time_data.get(param_name)

        if data is None or len(data) == 0:
            return param_name, None, 0

        return param_name, data[self.current_index], self.current_index

    def get_plotting_mode(self):
        """
        Get the current plotting mode.

        Returns:
            str: One of "Total Events", "Total Population", "Events per Step", "Population per Step"
        """
        return self.mode_combo.currentText()

    def reset(self):
        """Reset the widget to initial state."""
        self.time_slider.setValue(0)
        self.current_index = 0
        if self.is_playing:
            self.play_button.click()  # Stop animation
