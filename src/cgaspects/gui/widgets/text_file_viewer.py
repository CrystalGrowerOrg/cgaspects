"""Text File Viewer Widget for displaying log files and other text content."""

import logging
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger("CA:TextFileViewer")


class TextFileViewer(QWidget):
    """Widget for viewing text files with automatic refresh capability."""

    def __init__(self, file_path=None, parent=None, auto_refresh=False, refresh_interval=10000):
        """
        Initialize the TextFileViewer.

        Args:
            file_path: Path to the text file to display
            parent: Parent widget
            auto_refresh: Enable automatic refresh of file contents (default: False)
            refresh_interval: Refresh interval in milliseconds (default: 2000ms)
        """
        super().__init__(parent, Qt.Window)  # Make it a standalone window
        self.file_path = None
        self.auto_refresh = auto_refresh
        self.refresh_interval = refresh_interval
        self.auto_scroll = True

        # Set window properties
        self.setWindowTitle("Text File Viewer")
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Don't delete on close

        self.setup_ui()
        self.setup_refresh_timer()

        if file_path:
            self.set_file(file_path)

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Header with file path and controls
        header_layout = QHBoxLayout()

        self.file_label = QLabel("No file loaded")
        self.file_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.file_label)

        header_layout.addStretch()

        # Auto-refresh toggle button
        self.auto_refresh_button = QPushButton("Auto-refresh: OFF")
        self.auto_refresh_button.setCheckable(True)
        self.auto_refresh_button.setChecked(self.auto_refresh)
        self.auto_refresh_button.clicked.connect(self.toggle_auto_refresh)
        if self.auto_refresh:
            self.auto_refresh_button.setText("Auto-refresh: ON")
        header_layout.addWidget(self.auto_refresh_button)

        # Auto-scroll toggle button
        self.auto_scroll_button = QPushButton("Auto-scroll: ON")
        self.auto_scroll_button.setCheckable(True)
        self.auto_scroll_button.setChecked(True)
        self.auto_scroll_button.clicked.connect(self.toggle_auto_scroll)
        header_layout.addWidget(self.auto_scroll_button)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_content)
        header_layout.addWidget(self.refresh_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_display)
        header_layout.addWidget(self.clear_button)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        header_layout.addWidget(self.close_button)

        layout.addLayout(header_layout)

        # Text display area
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        # Set monospace font for better log readability
        font = QFont("Arial")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.text_edit.setFont(font)

        layout.addWidget(self.text_edit)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def setup_refresh_timer(self):
        """Set up the automatic refresh timer."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_content)

        if self.auto_refresh:
            self.refresh_timer.start(self.refresh_interval)

    def set_file(self, file_path):
        """
        Set the file to be displayed.

        Args:
            file_path: Path to the text file (can be str or Path object)
        """
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            self.file_label.setText(f"File not found: {self.file_path.name}")
            self.status_label.setText("Error: File does not exist")
            logger.warning(f"File does not exist: {self.file_path}")
            return

        if not self.file_path.is_file():
            self.file_label.setText(f"Not a file: {self.file_path.name}")
            self.status_label.setText("Error: Path is not a file")
            logger.warning(f"Path is not a file: {self.file_path}")
            return

        self.file_label.setText(f"File: {self.file_path.name}")
        self.setWindowTitle(f"Text File Viewer - {self.file_path.name}")
        self.refresh_content()

    def refresh_content(self):
        """Refresh the content from the file."""
        if not self.file_path or not self.file_path.exists():
            return

        try:
            with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            # Store current scroll position
            scrollbar = self.text_edit.verticalScrollBar()
            was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

            self.text_edit.setPlainText(content)

            # Auto-scroll to bottom if enabled and was already at bottom
            if self.auto_scroll and was_at_bottom:
                self.scroll_to_bottom()

            file_size = self.file_path.stat().st_size
            lines = content.count("\n") + 1
            self.status_label.setText(
                f"Loaded: {file_size} bytes, {lines} lines | "
                f"Last modified: {self.get_modification_time()}"
            )
            logger.debug(f"Refreshed content from {self.file_path}")

        except Exception as e:
            self.status_label.setText(f"Error reading file: {e}")
            logger.error(f"Error reading file {self.file_path}: {e}")

    def get_modification_time(self):
        """Get the file's last modification time as a formatted string."""
        if not self.file_path or not self.file_path.exists():
            return "Unknown"

        from datetime import datetime

        mtime = self.file_path.stat().st_mtime
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def toggle_auto_refresh(self, checked):
        """Toggle auto-refresh functionality."""
        self.auto_refresh = checked
        self.auto_refresh_button.setText(f"Auto-refresh: {'ON' if checked else 'OFF'}")

        if checked:
            self.refresh_timer.start(self.refresh_interval)
            self.status_label.setText(
                f"Auto-refresh enabled (every {self.refresh_interval / 1000:.1f}s)"
            )
        else:
            self.refresh_timer.stop()
            self.status_label.setText("Auto-refresh disabled")

    def toggle_auto_scroll(self, checked):
        """Toggle auto-scroll functionality."""
        self.auto_scroll = checked
        self.auto_scroll_button.setText(f"Auto-scroll: {'ON' if checked else 'OFF'}")

        if checked:
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scroll the text view to the bottom."""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def clear_display(self):
        """Clear the file contents after user confirmation."""
        if not self.file_path or not self.file_path.exists():
            self.text_edit.clear()
            self.status_label.setText("Display cleared")
            return

        # Confirm with user before clearing the file
        reply = QMessageBox.question(
            self,
            "Clear File Contents",
            f"Are you sure you want to clear the contents of:\n\n{self.file_path}\n\n"
            "This will permanently delete all content in the file.\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                # Clear the file by opening in write mode
                with open(self.file_path, "w") as f:
                    pass

                # Update the display
                self.text_edit.clear()
                self.status_label.setText("File contents cleared successfully")
                logger.info(f"Cleared contents of {self.file_path}")

                QMessageBox.information(
                    self,
                    "File Cleared",
                    f"The file has been cleared successfully:\n{self.file_path}",
                )
            except Exception as e:
                self.status_label.setText(f"Error clearing file: {e}")
                logger.error(f"Error clearing file {self.file_path}: {e}")
                QMessageBox.warning(
                    self,
                    "Error Clearing File",
                    f"Could not clear the file:\n{self.file_path}\n\nError: {e}",
                )

    def set_auto_refresh(self, enabled, interval=None):
        """
        Enable or disable automatic refresh.

        Args:
            enabled: True to enable auto-refresh, False to disable
            interval: Optional refresh interval in milliseconds
        """
        self.auto_refresh = enabled

        if interval:
            self.refresh_interval = interval

        if enabled:
            self.refresh_timer.start(self.refresh_interval)
        else:
            self.refresh_timer.stop()

    def closeEvent(self, event):
        """Handle widget close event."""
        self.refresh_timer.stop()
        super().closeEvent(event)
