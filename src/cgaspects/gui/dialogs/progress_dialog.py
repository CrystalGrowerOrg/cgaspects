from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QVBoxLayout,
)

from ..utils.circular_progress import PyCircularProgress


class CircularProgress(QDialog):
    def __init__(self, calc_type="Aspect Ratio"):
        super().__init__()

        # Initialise Window
        self.setWindowTitle(f"{calc_type} Calculation Progress")

        # Create the main layout for all your widgets
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Create a widget for the main layout
        self.circular_progress = PyCircularProgress(value=0)
        self.circular_progress.setFixedSize(250, 250)

        # # Create a label for displaying the options
        self.options_label = QLabel("Calculating...\nWith Selected Options: ")
        self.options_label.setAlignment(Qt.AlignCenter)
        # Add widgets to the layout with padding
        layout.addSpacing(50)
        layout.addWidget(self.options_label)
        layout.addSpacing(50)
        layout.addWidget(self.circular_progress)
        layout.addSpacing(50)

    def set_value(self, value):
        self.circular_progress.set_value(value)

    def update_options(self, options: namedtuple):
        # Format the options into a bullet-point style string
        options_text = f"""Calculating...
With Selected Options:
• Aspect Ratios
  PCA/OBA: {'Enabled' if options.selected_ar else 'Disabled'}
  CDA:     {'Enabled' if options.selected_cda else 'Disabled'}
• Checked Directions: {', '.join(options.checked_directions) or 'None'}
• Selected Directions: {', '.join(options.selected_directions) or 'None'}
• Plotting: {'Enabled' if options.plotting else 'Disabled'}"""

        self.options_label.setText(options_text)

    def update_text(self, text):
        self.options_label.setText(text)
