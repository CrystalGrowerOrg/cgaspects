import logging
from typing import Optional

from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QColor, QFont, QKeySequence, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QKeySequenceEdit,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..shortcuts_manager import ActionRecord, ShortcutsManager

logger = logging.getLogger("CA:KeyboardShortcutsDialog")

COL_CATEGORY = 0
COL_ACTION = 1
COL_SHORTCUT = 2


class KeyboardShortcutsDialog(QDialog):
    """View and customise keyboard shortcuts. Persists to ~/.cgaspects/shortcuts.json."""

    def __init__(self, manager: ShortcutsManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(False)
        self.resize(700, 600)

        self._manager = manager
        self._pending: dict[str, str] = {}
        self._editing_obj_name: Optional[str] = None

        self._setup_ui()
        self._populate_table()
        self._populate_viewport_shortcuts()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(8)

        # Filter bar
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Type to filter actions…")
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.textChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._search_edit)
        root.addLayout(filter_row)

        # Configurable shortcuts table
        edit_group = QGroupBox("Configurable Shortcuts")
        edit_layout = QVBoxLayout(edit_group)

        self._model = QStandardItemModel(0, 3)
        self._model.setHorizontalHeaderLabels(["Category", "Action", "Shortcut"])

        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy.setFilterKeyColumn(-1)

        self._table = QTableView()
        self._table.setModel(self._proxy)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(COL_CATEGORY, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(COL_ACTION, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(COL_SHORTCUT, QHeaderView.ResizeToContents)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.doubleClicked.connect(self._on_row_double_clicked)
        edit_layout.addWidget(self._table)

        # Inline edit controls
        edit_ctrl_row = QHBoxLayout()
        self._hint_label = QLabel("Double-click a row to edit its shortcut")
        self._hint_label.setStyleSheet("color: #888; font-style: italic;")
        edit_ctrl_row.addWidget(self._hint_label, stretch=1)

        self._key_edit = QKeySequenceEdit()
        self._key_edit.setVisible(False)
        edit_ctrl_row.addWidget(self._key_edit)

        self._set_btn = QPushButton("Set")
        self._set_btn.setVisible(False)
        self._set_btn.clicked.connect(self._on_accept_shortcut)
        edit_ctrl_row.addWidget(self._set_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setVisible(False)
        self._clear_btn.clicked.connect(self._on_clear_shortcut)
        edit_ctrl_row.addWidget(self._clear_btn)

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setVisible(False)
        self._cancel_btn.clicked.connect(self._on_cancel_edit)
        edit_ctrl_row.addWidget(self._cancel_btn)

        edit_layout.addLayout(edit_ctrl_row)
        root.addWidget(edit_group, stretch=3)

        # Viewport / navigation shortcuts (read-only)
        viewport_group = QGroupBox("Viewport / Navigation Shortcuts  (read-only)")
        viewport_layout = QVBoxLayout(viewport_group)
        self._viewport_tree = QTreeWidget()
        self._viewport_tree.setColumnCount(2)
        self._viewport_tree.setHeaderLabels(["Key / Combo", "Action"])
        self._viewport_tree.setAlternatingRowColors(True)
        self._viewport_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._viewport_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._viewport_tree.setRootIsDecorated(True)
        self._viewport_tree.setEditTriggers(QAbstractItemView.NoEditTriggers)
        viewport_layout.addWidget(self._viewport_tree)
        root.addWidget(viewport_group, stretch=2)

        # Bottom buttons
        btn_row = QHBoxLayout()
        self._reset_btn = QPushButton("Reset All to Defaults")
        self._reset_btn.setToolTip("Restore all shortcuts to their factory defaults")
        self._reset_btn.clicked.connect(self._on_reset_all)
        btn_row.addWidget(self._reset_btn)
        btn_row.addStretch()

        self._save_btn = QPushButton("Save")
        self._save_btn.setDefault(True)
        self._save_btn.setToolTip("Apply and save shortcut changes")
        self._save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(self._save_btn)

        self._close_btn = QPushButton("Close")
        self._close_btn.clicked.connect(self.close)
        btn_row.addWidget(self._close_btn)

        root.addLayout(btn_row)

    def _populate_table(self) -> None:
        self._model.removeRows(0, self._model.rowCount())
        for rec in self._manager.get_records():
            current_sc = rec.action.shortcut().toString(QKeySequence.NativeText)

            cat_item = QStandardItem(rec.menu_path)
            cat_item.setEditable(False)

            name_item = QStandardItem(rec.display_name)
            name_item.setEditable(False)
            name_item.setData(rec.object_name, Qt.UserRole)

            sc_item = QStandardItem(current_sc)
            sc_item.setEditable(False)
            if not current_sc:
                sc_item.setForeground(QColor("#aaaaaa"))

            self._model.appendRow([cat_item, name_item, sc_item])

    def _populate_viewport_shortcuts(self) -> None:
        # Import here to avoid a circular import at module level
        from ..visualisation.openGL import VisualisationWidget

        self._viewport_tree.clear()
        bold = QFont()
        bold.setBold(True)

        for category, entries in VisualisationWidget.VIEWPORT_SHORTCUTS.items():
            header = QTreeWidgetItem([category, ""])
            header.setFont(0, bold)
            header.setFlags(Qt.ItemIsEnabled)
            self._viewport_tree.addTopLevelItem(header)
            for key_str, description in entries:
                child = QTreeWidgetItem([key_str, description])
                child.setFlags(Qt.ItemIsEnabled)
                header.addChild(child)

        self._viewport_tree.expandAll()

    # ------------------------------------------------------------------
    # Edit workflow
    # ------------------------------------------------------------------

    def _on_row_double_clicked(self, proxy_index) -> None:
        src_index = self._proxy.mapToSource(proxy_index)
        name_item = self._model.item(src_index.row(), COL_ACTION)
        if name_item is None:
            return

        obj_name = name_item.data(Qt.UserRole)
        current_sc = self._pending.get(obj_name, self._manager.get_current_shortcut(obj_name))

        self._editing_obj_name = obj_name
        self._hint_label.setText(f"Editing: {name_item.text()}")

        self._key_edit.setKeySequence(QKeySequence(current_sc))
        self._key_edit.setVisible(True)
        self._set_btn.setVisible(True)
        self._clear_btn.setVisible(True)
        self._cancel_btn.setVisible(True)
        self._key_edit.setFocus()

    def _on_accept_shortcut(self) -> None:
        if self._editing_obj_name is None:
            return
        new_sc = self._key_edit.keySequence().toString(QKeySequence.NativeText)

        conflict = self._find_conflict(new_sc, self._editing_obj_name)
        if conflict and new_sc:
            reply = QMessageBox.question(
                self,
                "Shortcut Conflict",
                f'"{new_sc}" is already used by "{conflict.display_name}".\n'
                "Reassign it? The other action will lose its shortcut.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return
            self._pending[conflict.object_name] = ""
            self._refresh_row(conflict.object_name, "")

        self._pending[self._editing_obj_name] = new_sc
        self._refresh_row(self._editing_obj_name, new_sc)
        self._exit_edit_mode()

    def _on_clear_shortcut(self) -> None:
        if self._editing_obj_name is None:
            return
        self._pending[self._editing_obj_name] = ""
        self._refresh_row(self._editing_obj_name, "")
        self._exit_edit_mode()

    def _on_cancel_edit(self) -> None:
        self._exit_edit_mode()

    def _exit_edit_mode(self) -> None:
        self._editing_obj_name = None
        self._hint_label.setText("Double-click a row to edit its shortcut")
        self._key_edit.setVisible(False)
        self._set_btn.setVisible(False)
        self._clear_btn.setVisible(False)
        self._cancel_btn.setVisible(False)

    def _refresh_row(self, obj_name: str, new_sc: str) -> None:
        for row in range(self._model.rowCount()):
            name_item = self._model.item(row, COL_ACTION)
            if name_item and name_item.data(Qt.UserRole) == obj_name:
                sc_item = self._model.item(row, COL_SHORTCUT)
                sc_item.setText(new_sc)
                sc_item.setForeground(QColor("#aaaaaa") if not new_sc else QColor())
                break

    def _find_conflict(self, shortcut_str: str, exclude_obj_name: str) -> Optional[ActionRecord]:
        if not shortcut_str:
            return None
        canonical = QKeySequence(shortcut_str).toString(QKeySequence.NativeText)
        for rec in self._manager.get_records():
            if rec.object_name == exclude_obj_name:
                continue
            pending = self._pending.get(rec.object_name)
            effective = pending if pending is not None else rec.action.shortcut().toString(QKeySequence.NativeText)
            if effective == canonical:
                return rec
        return None

    def _on_filter_changed(self, text: str) -> None:
        self._proxy.setFilterFixedString(text)

    # ------------------------------------------------------------------
    # Save / Reset
    # ------------------------------------------------------------------

    def _on_save(self) -> None:
        overrides: dict[str, str] = {}
        for rec in self._manager.get_records():
            if rec.object_name in self._pending:
                overrides[rec.object_name] = self._pending[rec.object_name]
            else:
                overrides[rec.object_name] = rec.action.shortcut().toString(QKeySequence.NativeText)
        self._manager.save_overrides(overrides)
        self._pending.clear()
        self._populate_table()

    def _on_reset_all(self) -> None:
        reply = QMessageBox.question(
            self,
            "Reset Shortcuts",
            "Reset all keyboard shortcuts to factory defaults?\n"
            "This will also clear any saved customisations.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._manager.reset_to_defaults()
            self._pending.clear()
            self._populate_table()
