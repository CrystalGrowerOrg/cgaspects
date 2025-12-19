"""
Dialog for entering lattice parameters to convert Cartesian axes to fractional coordinates.
"""
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QTabWidget,
    QWidget,
    QFileDialog,
    QMessageBox,
)

from ...gui.utils.crystallography import Cell, Crystallography

logger = logging.getLogger("CA:LatticeDialog")


class LatticeParametersDialog(QDialog):
    """Dialog for entering lattice parameters either manually or from a CrystalGrower file."""

    parametersAccepted = Signal(Cell)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lattice Parameters")
        self.setModal(True)
        self.resize(500, 300)

        self.cell = None
        self.setupUI()

    def setupUI(self):
        """Setup the user interface."""
        layout = QVBoxLayout()

        # Create tab widget for manual entry vs file import
        self.tab_widget = QTabWidget()

        # Manual entry tab
        manual_widget = QWidget()
        manual_layout = QFormLayout()

        self.a_edit = QLineEdit()
        self.a_edit.setPlaceholderText("e.g., 3.6295")
        self.b_edit = QLineEdit()
        self.b_edit.setPlaceholderText("e.g., 9.8128")
        self.c_edit = QLineEdit()
        self.c_edit.setPlaceholderText("e.g., 18.4269")
        self.alpha_edit = QLineEdit()
        self.alpha_edit.setPlaceholderText("e.g., 90.000")
        self.beta_edit = QLineEdit()
        self.beta_edit.setPlaceholderText("e.g., 90.000")
        self.gamma_edit = QLineEdit()
        self.gamma_edit.setPlaceholderText("e.g., 118.042")

        manual_layout.addRow("a (Å):", self.a_edit)
        manual_layout.addRow("b (Å):", self.b_edit)
        manual_layout.addRow("c (Å):", self.c_edit)
        manual_layout.addRow("α (°):", self.alpha_edit)
        manual_layout.addRow("β (°):", self.beta_edit)
        manual_layout.addRow("γ (°):", self.gamma_edit)

        manual_widget.setLayout(manual_layout)
        self.tab_widget.addTab(manual_widget, "Manual Entry")

        # File import tab
        file_widget = QWidget()
        file_layout = QVBoxLayout()

        file_info_label = QLabel(
            "Select a CrystalGrower structure file.\n"
            "Lattice parameters will be extracted from the 'Non primitive data' section."
        )
        file_info_label.setWordWrap(True)

        file_button_layout = QHBoxLayout()
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Path to CrystalGrower structure file...")
        self.file_path_edit.setReadOnly(True)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_file)

        file_button_layout.addWidget(self.file_path_edit)
        file_button_layout.addWidget(self.browse_button)

        self.file_info_display = QLabel("")
        self.file_info_display.setWordWrap(True)

        file_layout.addWidget(file_info_label)
        file_layout.addLayout(file_button_layout)
        file_layout.addWidget(self.file_info_display)
        file_layout.addStretch()

        file_widget.setLayout(file_layout)
        self.tab_widget.addTab(file_widget, "From File")

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_parameters)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def browse_file(self):
        """Open file dialog to select CrystalGrower structure file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CrystalGrower Structure File",
            "",
            "All Files (*)"
        )

        if file_path:
            self.file_path_edit.setText(file_path)
            self.parse_structure_file(file_path)

    def parse_structure_file(self, file_path: str):
        """
        Parse CrystalGrower structure file to extract lattice parameters.

        The file format has a section starting with 'Non primitive data' followed by
        lattice parameters:
          a   b   c
         alpha beta gamma
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            # Find the "Non primitive data" section
            non_primitive_index = None
            for i, line in enumerate(lines):
                if "Non primitive data" in line:
                    non_primitive_index = i
                    break

            if non_primitive_index is None:
                raise ValueError("Could not find 'Non primitive data' section in file")

            # The next line should contain a, b, c
            abc_line = lines[non_primitive_index + 1].strip()
            a, b, c = map(float, abc_line.split())

            # The line after that should contain alpha, beta, gamma
            angles_line = lines[non_primitive_index + 2].strip()
            alpha, beta, gamma = map(float, angles_line.split())

            # Update the manual entry fields
            self.a_edit.setText(str(a))
            self.b_edit.setText(str(b))
            self.c_edit.setText(str(c))
            self.alpha_edit.setText(str(alpha))
            self.beta_edit.setText(str(beta))
            self.gamma_edit.setText(str(gamma))

            # Display info
            info_text = (
                f"Lattice parameters extracted:\n"
                f"a = {a:.4f} Å, b = {b:.4f} Å, c = {c:.4f} Å\n"
                f"α = {alpha:.3f}°, β = {beta:.3f}°, γ = {gamma:.3f}°"
            )
            self.file_info_display.setText(info_text)
            self.file_info_display.setStyleSheet("color: green;")

            logger.info(f"Parsed lattice parameters from {file_path}")

        except Exception as e:
            error_msg = f"Error parsing file: {str(e)}"
            self.file_info_display.setText(error_msg)
            self.file_info_display.setStyleSheet("color: red;")
            logger.error(error_msg)
            QMessageBox.warning(self, "Parse Error", error_msg)

    def accept_parameters(self):
        """Validate and accept the entered parameters."""
        try:
            a = float(self.a_edit.text())
            b = float(self.b_edit.text())
            c = float(self.c_edit.text())
            alpha = float(self.alpha_edit.text())
            beta = float(self.beta_edit.text())
            gamma = float(self.gamma_edit.text())

            # Basic validation
            if any(val <= 0 for val in [a, b, c]):
                raise ValueError("Lattice parameters a, b, c must be positive")

            if not all(0 < angle < 180 for angle in [alpha, beta, gamma]):
                raise ValueError("Angles must be between 0 and 180 degrees")

            # Create Cell object
            self.cell = Cell(a=a, b=b, c=c, alpha=alpha, beta=beta, gamma=gamma)

            # Emit signal and accept dialog
            self.parametersAccepted.emit(self.cell)
            self.accept()

            logger.info(f"Lattice parameters accepted: {self.cell}")

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Input",
                f"Please enter valid numerical values for all parameters.\n\nError: {str(e)}"
            )

    def get_cell(self) -> Optional[Cell]:
        """Return the cell object if parameters were accepted."""
        return self.cell
