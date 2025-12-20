"""Dialog for site highlighting settings."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)


def create_colored_icon(color, size=(50, 50)):
    """Create a colored icon for the color button."""
    pixmap = QPixmap(*size)
    pixmap.fill(color)
    return QIcon(pixmap)


class SiteHighlightDialog(QDialog):
    """Dialog for highlighting sites in the visualization."""

    highlightsChanged = Signal(list)  # Emits list of (site_numbers, color) tuples
    clearHighlights = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Site Highlighting")
        self.setModal(False)  # Non-modal so user can interact with main window

        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Create multiple highlight groups with different colors.\n"
            "Supports: single (5), comma-separated (1,2,3), ranges (10-20), or mixed (1,5-10,15)"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Background color selection
        bg_color_layout = QHBoxLayout()
        bg_color_label = QLabel("Background Color:")
        self.bg_color_button = QToolButton()
        self.background_color = QColor(200, 200, 200)  # Default light gray
        self.bg_color_button.setIcon(create_colored_icon(self.background_color))
        self.bg_color_button.clicked.connect(self.select_background_color)
        self.bg_color_button.setMinimumSize(60, 30)
        bg_color_layout.addWidget(bg_color_label)
        bg_color_layout.addWidget(self.bg_color_button)
        bg_color_layout.addStretch()
        layout.addLayout(bg_color_layout)

        # Add highlight group section
        add_group_label = QLabel("Add Highlight Group:")
        add_group_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(add_group_label)

        # Color selection
        color_layout = QHBoxLayout()
        color_label = QLabel("Highlight Color:")
        self.color_button = QToolButton()
        self.highlight_color = QColor(255, 0, 0)  # Default red
        self.color_button.setIcon(create_colored_icon(self.highlight_color))
        self.color_button.clicked.connect(self.select_color)
        self.color_button.setMinimumSize(60, 30)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # Site number input
        site_layout = QHBoxLayout()
        site_label = QLabel("Site Numbers:")
        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("e.g., 1,2,3 or 10-20")
        self.site_input.returnPressed.connect(self.add_highlight_group)  # Allow Enter key
        site_layout.addWidget(site_label)
        site_layout.addWidget(self.site_input)
        layout.addLayout(site_layout)

        # Add button
        add_button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Highlight Group")
        self.add_button.clicked.connect(self.add_highlight_group)
        self.add_button.setDefault(True)
        add_button_layout.addWidget(self.add_button)
        add_button_layout.addStretch()
        layout.addLayout(add_button_layout)

        # List of highlight groups
        groups_label = QLabel("Highlight Groups:")
        groups_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(groups_label)

        self.highlight_list = QListWidget()
        self.highlight_list.setMaximumHeight(150)
        layout.addWidget(self.highlight_list)

        # Buttons for managing groups
        list_button_layout = QHBoxLayout()
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_group)
        self.apply_button = QPushButton("Apply All")
        self.apply_button.clicked.connect(self.apply_all_highlights)
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all_highlights)

        list_button_layout.addWidget(self.remove_button)
        list_button_layout.addWidget(self.apply_button)
        list_button_layout.addWidget(self.clear_button)
        layout.addLayout(list_button_layout)

        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        close_layout.addWidget(self.close_button)
        layout.addLayout(close_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setMinimumWidth(500)

        # Store highlight groups as list of (site_numbers, color) tuples
        self.highlight_groups = []

    def select_color(self):
        """Open color dialog to select highlight color."""
        color = QColorDialog.getColor(self.highlight_color, self, "Select Highlight Color")
        if color.isValid():
            self.highlight_color = color
            self.color_button.setIcon(create_colored_icon(self.highlight_color))

    def select_background_color(self):
        """Open color dialog to select background color."""
        color = QColorDialog.getColor(self.background_color, self, "Select Background Color")
        if color.isValid():
            self.background_color = color
            self.bg_color_button.setIcon(create_colored_icon(self.background_color))
            # Apply changes immediately
            self.apply_all_highlights()

    def parse_site_numbers(self, text):
        """Parse site numbers from text input.

        Supports:
        - Single numbers: "5"
        - Comma-separated: "1,2,3"
        - Ranges: "10-20"
        - Mixed: "1,2,5-10,15"

        Returns:
            list: List of site numbers
        """
        site_numbers = []
        if not text.strip():
            return site_numbers

        parts = text.split(',')
        for part in parts:
            part = part.strip()
            if '-' in part:
                # Range
                try:
                    start, end = part.split('-')
                    start = int(start.strip())
                    end = int(end.strip())
                    site_numbers.extend(range(start, end + 1))
                except ValueError:
                    pass  # Skip invalid ranges
            else:
                # Single number
                try:
                    site_numbers.append(int(part))
                except ValueError:
                    pass  # Skip invalid numbers

        return site_numbers

    def add_highlight_group(self):
        """Add a new highlight group to the list."""
        text = self.site_input.text()
        site_numbers = self.parse_site_numbers(text)

        if not site_numbers:
            self.status_label.setText("No valid site numbers entered")
            return

        # Store the group
        self.highlight_groups.append((site_numbers, self.highlight_color))

        # Create display item with colored icon
        color_swatch = create_colored_icon(self.highlight_color, size=(16, 16))
        sites_str = text if len(text) < 40 else text[:37] + "..."
        item = QListWidgetItem(color_swatch, f"{sites_str} ({len(site_numbers)} sites)")
        item.setData(Qt.UserRole, len(self.highlight_groups) - 1)  # Store index
        self.highlight_list.addItem(item)

        # Clear input
        self.site_input.clear()

        # Apply the highlights
        self.apply_all_highlights()
        self.status_label.setText(f"Added group with {len(site_numbers)} site(s)")

    def remove_selected_group(self):
        """Remove the selected highlight group."""
        current_item = self.highlight_list.currentItem()
        if current_item is None:
            self.status_label.setText("No group selected")
            return

        index = current_item.data(Qt.UserRole)
        row = self.highlight_list.currentRow()

        # Remove from list and data
        self.highlight_list.takeItem(row)
        self.highlight_groups.pop(index)

        # Update indices in remaining items
        for i in range(self.highlight_list.count()):
            item = self.highlight_list.item(i)
            old_index = item.data(Qt.UserRole)
            if old_index > index:
                item.setData(Qt.UserRole, old_index - 1)

        # Reapply all highlights
        self.apply_all_highlights()
        self.status_label.setText("Group removed")

    def apply_all_highlights(self):
        """Apply all highlight groups."""
        # Emit all groups along with background color
        self.highlightsChanged.emit(self.highlight_groups + [("background", self.background_color)])
        total_sites = sum(len(sites) for sites, _ in self.highlight_groups)
        self.status_label.setText(f"Applied {len(self.highlight_groups)} group(s) with {total_sites} total sites")

    def clear_all_highlights(self):
        """Clear all site highlights."""
        self.highlight_groups.clear()
        self.highlight_list.clear()
        self.clearHighlights.emit()
        self.site_input.clear()
        self.status_label.setText("All highlights cleared")
