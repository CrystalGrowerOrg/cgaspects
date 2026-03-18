from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class ThreadMonitorDialog(QDialog):
    """Shows QThreadPool instances, their active thread counts, and allows cancellation."""

    def __init__(self, thread_pools: dict, worker_sources: dict | None = None, parent=None):
        """
        Parameters
        ----------
        thread_pools : dict[str, QThreadPool]
            Mapping of display name → pool instance.
        worker_sources : dict[str, callable] | None
            Optional mapping of display name → callable returning the current
            CancellableRunnable (or None if no worker is running).
        """
        super().__init__(parent)
        self.setWindowTitle("Active Threads")
        self.setMinimumWidth(460)
        self._pools = thread_pools
        self._worker_sources = worker_sources or {}
        self._setup_ui()
        self._refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Pool", "Active", "Max Threads", ""])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        layout.addWidget(self.table)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        kill_all_btn = QPushButton("Kill All")
        kill_all_btn.setToolTip(
            "Clear queued tasks and request cancellation of all running workers"
        )
        kill_all_btn.clicked.connect(self._kill_all)
        btn_row.addWidget(kill_all_btn)
        btn_row.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_row.addWidget(refresh_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _refresh(self):
        self.table.setRowCount(0)
        for name, pool in self._pools.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(str(pool.activeThreadCount())))
            self.table.setItem(row, 2, QTableWidgetItem(str(pool.maxThreadCount())))
            kill_btn = QPushButton("Kill")
            kill_btn.setToolTip(
                f"Clear queued tasks and cancel the running worker for '{name}'"
            )
            kill_btn.clicked.connect(lambda checked, p=pool, n=name: self._kill_pool(p, n))
            self.table.setCellWidget(row, 3, kill_btn)
        self.table.resizeColumnsToContents()

    def _get_worker(self, name):
        src = self._worker_sources.get(name)
        return src() if src is not None else None

    def _kill_pool(self, pool, name):
        pool.clear()
        worker = self._get_worker(name)
        if worker is not None:
            worker.cancel()
            msg = f"Cancel requested for '{name}' — worker will stop at next checkpoint."
        else:
            msg = f"Queued tasks cleared for '{name}'. No active worker to cancel."
        self.status_label.setText(msg)
        self._refresh()

    def _kill_all(self):
        cancelled_any = False
        for name, pool in self._pools.items():
            pool.clear()
            worker = self._get_worker(name)
            if worker is not None:
                worker.cancel()
                cancelled_any = True
        if cancelled_any:
            msg = "Cancel requested for all pools. Workers stop at next checkpoint."
        else:
            msg = "Queued tasks cleared for all pools. No active workers to cancel."
        self.status_label.setText(msg)
        self._refresh()
