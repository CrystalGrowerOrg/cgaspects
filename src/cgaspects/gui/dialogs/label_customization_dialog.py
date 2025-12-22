"""Dialog for customizing plot labels with LaTeX support."""
import logging
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, Signal

logger = logging.getLogger("CA:LabelCustomizationDialog")


class LabelCustomizationDialog(QDialog):
    """Dialog for customizing plot labels with LaTeX support.

    Allows users to set custom labels for:
    - Plot title
    - X-axis label
    - Y-axis label
    - Colorbar label

    All labels support LaTeX formatting using raw strings (r"...").
    """

    # Signal emitted when Apply button is clicked
    labels_applied = Signal(dict)

    def __init__(self, current_labels=None, parent=None):
        """Initialize the dialog.

        Args:
            current_labels: Dictionary with keys 'title', 'xlabel', 'ylabel', 'cbar_label'
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Customize Plot Labels")
        self.setMinimumWidth(500)

        # Store current labels
        if current_labels is None:
            current_labels = {}

        self.current_labels = {
            'title': current_labels.get('title', ''),
            'xlabel': current_labels.get('xlabel', ''),
            'ylabel': current_labels.get('ylabel', ''),
            'cbar_label': current_labels.get('cbar_label', ''),
        }

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        """Create dialog widgets."""
        # Create line edits for each label
        self.title_edit = QLineEdit(self.current_labels['title'])
        self.title_edit.setPlaceholderText(r'e.g., r"My Plot Title"')

        self.xlabel_edit = QLineEdit(self.current_labels['xlabel'])
        self.xlabel_edit.setPlaceholderText(r'e.g., r"$\Delta G$ (kcal/mol)"')

        self.ylabel_edit = QLineEdit(self.current_labels['ylabel'])
        self.ylabel_edit.setPlaceholderText(r'e.g., r"Energy ($k_BT$)"')

        self.cbar_label_edit = QLineEdit(self.current_labels['cbar_label'])
        self.cbar_label_edit.setPlaceholderText(r'e.g., r"$\Delta G_{Cryst}$ (kcal/mol)"')

        # Create reset button for each field
        self.title_reset_btn = QPushButton("Reset")
        self.xlabel_reset_btn = QPushButton("Reset")
        self.ylabel_reset_btn = QPushButton("Reset")
        self.cbar_reset_btn = QPushButton("Reset")

        # Connect reset buttons
        self.title_reset_btn.clicked.connect(lambda: self.title_edit.clear())
        self.xlabel_reset_btn.clicked.connect(lambda: self.xlabel_edit.clear())
        self.ylabel_reset_btn.clicked.connect(lambda: self.ylabel_edit.clear())
        self.cbar_reset_btn.clicked.connect(lambda: self.cbar_label_edit.clear())

        # Create dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Connect Apply button to emit signal without closing
        apply_button = self.button_box.button(QDialogButtonBox.Apply)
        if apply_button:
            apply_button.clicked.connect(self.apply_labels)

    def create_layout(self):
        """Create dialog layout."""
        main_layout = QVBoxLayout()

        # Create info label
        info_label = QLabel(
            "Customize plot labels. You can use LaTeX formatting (e.g., $\\alpha$, ^2, _n).\n"
            "Leave fields empty to use default labels."
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        # Create form layout for labels
        form_group = QGroupBox("Labels")
        form_layout = QFormLayout()

        # Title row
        title_row = QHBoxLayout()
        title_row.addWidget(self.title_edit, 1)
        title_row.addWidget(self.title_reset_btn)
        form_layout.addRow("Title:", title_row)

        # X-label row
        xlabel_row = QHBoxLayout()
        xlabel_row.addWidget(self.xlabel_edit, 1)
        xlabel_row.addWidget(self.xlabel_reset_btn)
        form_layout.addRow("X-axis Label:", xlabel_row)

        # Y-label row
        ylabel_row = QHBoxLayout()
        ylabel_row.addWidget(self.ylabel_edit, 1)
        ylabel_row.addWidget(self.ylabel_reset_btn)
        form_layout.addRow("Y-axis Label:", ylabel_row)

        # Colorbar label row
        cbar_row = QHBoxLayout()
        cbar_row.addWidget(self.cbar_label_edit, 1)
        cbar_row.addWidget(self.cbar_reset_btn)
        form_layout.addRow("Colorbar Label:", cbar_row)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # Add examples section
        examples_label = QLabel(
            "<b>LaTeX Examples:</b><br>"
            "Greek letters: $\\alpha$, $\\beta$, $\\Delta$<br>"
            "Superscript: $x^2$, $E^{-kt}$<br>"
            "Subscript: $G_{cryst}$, $k_B T$<br>"
            "Combined: $\\Delta G_{Cryst}$ (kcal/mol)"
        )
        examples_label.setWordWrap(True)
        main_layout.addWidget(examples_label)

        # Add button box
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def get_labels(self):
        """Get the custom labels.

        Returns:
            Dictionary with keys 'title', 'xlabel', 'ylabel', 'cbar_label'.
            Empty strings mean use default labels.
        """
        return {
            'title': self.title_edit.text().strip(),
            'xlabel': self.xlabel_edit.text().strip(),
            'ylabel': self.ylabel_edit.text().strip(),
            'cbar_label': self.cbar_label_edit.text().strip(),
        }

    def apply_labels(self):
        """Apply the current labels without closing the dialog.

        Emits the labels_applied signal with the current label values.
        """
        labels = self.get_labels()
        self.labels_applied.emit(labels)
        logger.debug(f"Applied labels: {labels}")
