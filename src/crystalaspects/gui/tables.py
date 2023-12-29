from pathlib import Path

import numpy as np
import pandas as pd

# PyQt imports
from PySide6.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QMainWindow,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TableDialog(QDialog):
    """Displaying the dataframe as a QTable as a
    pop up"""

    def __init__(self):
        super().__init__()
        print("Creating table window")

    def DisplayData(self, df):
        self.data = df
        df = df.iloc[:, 0:]
        self.table = QTableWidget()
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)

        # Create a scroll area and set the table widget as its widget
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.table)

        for row in df.iterrows():
            values = row[1]
            for col_index, value in enumerate(values):
                if isinstance(value, (float, int)):
                    value = QTableWidgetItem("{:,.2f}".format(value))
                tableItem = QTableWidgetItem(str(value))
                self.table.setItem(row[0], col_index, tableItem)
