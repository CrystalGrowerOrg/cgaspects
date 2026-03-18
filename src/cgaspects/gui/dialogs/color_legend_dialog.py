from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class _GradientWidget(QWidget):
    """Paints a horizontal colormap gradient with min/max labels."""

    def __init__(self, rows, min_val, max_val, parent=None):
        super().__init__(parent)
        self._rows = rows  # list of (value, (r, g, b))
        self._min_val = min_val
        self._max_val = max_val
        self.setMinimumHeight(60)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        strip_top = 4
        strip_height = 30
        strip_left = 4
        strip_right = self.width() - 4
        strip_width = strip_right - strip_left

        if strip_width <= 0 or not self._rows:
            return

        # Build gradient from the (value, rgb) rows sorted by value
        sorted_rows = sorted(self._rows, key=lambda r: r[0] if r[0] is not None else 0)
        val_range = self._max_val - self._min_val if self._max_val != self._min_val else 1.0

        gradient = QLinearGradient(strip_left, 0, strip_right, 0)
        for val, (r, g, b) in sorted_rows:
            pos = (val - self._min_val) / val_range if val is not None else 0.0
            pos = max(0.0, min(1.0, pos))
            gradient.setColorAt(pos, QColor.fromRgbF(r, g, b))

        painter.fillRect(strip_left, strip_top, strip_width, strip_height, gradient)
        painter.setPen(Qt.black)
        painter.drawRect(strip_left, strip_top, strip_width - 1, strip_height - 1)

        # Min / max labels
        label_y = strip_top + strip_height + 16
        painter.drawText(strip_left, label_y, _fmt(self._min_val))
        max_text = _fmt(self._max_val)
        fm = painter.fontMetrics()
        painter.drawText(strip_right - fm.horizontalAdvance(max_text), label_y, max_text)


def _fmt(val):
    """Format a numeric legend value compactly."""
    if val is None:
        return ""
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    return f"{val:.4g}"


class ColorLegendDialog(QDialog):
    """Non-modal dialog showing the current point-cloud colour legend."""

    _TABLE_THRESHOLD = 10  # switch to gradient above this many unique values

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Colour Legend")
        self.setModal(False)
        self.resize(260, 320)

        self._info = None
        self._user_mode = None  # None = auto, "table" or "gradient" = user override

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Title
        self._title_label = QLabel("—")
        font = self._title_label.font()
        font.setBold(True)
        self._title_label.setFont(font)
        layout.addWidget(self._title_label)

        # Toggle button
        self._toggle_btn = QPushButton()
        self._toggle_btn.setFixedHeight(24)
        self._toggle_btn.clicked.connect(self._on_toggle)
        layout.addWidget(self._toggle_btn)

        # Body container — holds either the table or gradient widget
        self._body_container = QWidget()
        self._body_layout = QVBoxLayout(self._body_container)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._body_container, 1)

        self._body_widget = None  # current table or gradient widget

    # ------------------------------------------------------------------
    # Public slot
    # ------------------------------------------------------------------

    def update_legend(self, info: dict):
        if info is None:
            return
        self._info = info
        self._refresh()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auto_mode(self, rows):
        if not rows or rows[0][0] is None:  # single colour
            return "table"
        return "table" if len(rows) <= self._TABLE_THRESHOLD else "gradient"

    def _effective_mode(self, rows):
        if not rows or rows[0][0] is None:  # single colour — always table
            return "table"
        return self._user_mode if self._user_mode is not None else self._auto_mode(rows)

    def _refresh(self):
        info = self._info
        rows = info["rows"]
        mode = self._effective_mode(rows)

        self._title_label.setText(info.get("color_by", ""))

        # Update toggle button label / visibility
        is_single = (not rows) or rows[0][0] is None
        self._toggle_btn.setVisible(not is_single)
        if mode == "table":
            self._toggle_btn.setText("Switch to Gradient")
        else:
            self._toggle_btn.setText("Switch to Table")

        # Replace body widget
        if self._body_widget is not None:
            self._body_layout.removeWidget(self._body_widget)
            self._body_widget.deleteLater()
            self._body_widget = None

        if mode == "gradient":
            self._body_widget = _GradientWidget(
                rows, info["min_val"], info["max_val"], parent=self._body_container
            )
        else:
            self._body_widget = self._build_table(rows)

        self._body_layout.addWidget(self._body_widget)

    def _build_table(self, rows):
        table = QTableWidget(len(rows), 2)
        table.setHorizontalHeaderLabels(["Value", "Colour"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)

        for i, (val, (r, g, b)) in enumerate(rows):
            label = "Single Colour" if val is None else _fmt(val)
            table.setItem(i, 0, QTableWidgetItem(label))

            swatch = QTableWidgetItem()
            swatch.setBackground(QColor.fromRgbF(r, g, b))
            table.setItem(i, 1, swatch)

        table.resizeColumnsToContents()
        return table

    def _on_toggle(self):
        if self._info is None:
            return
        rows = self._info["rows"]
        current = self._effective_mode(rows)
        self._user_mode = "gradient" if current == "table" else "table"
        self._refresh()
