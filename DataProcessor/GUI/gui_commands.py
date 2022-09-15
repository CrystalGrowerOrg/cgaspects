import numpy as np
import pandas as pd
import os
from natsort import natsorted
import re
from pathlib import Path
from DataProcessor.tools.shape_analysis import CrystalShape as cs
from DataProcessor.data.calc_data import Calculate as calc

from PyQt5 import QtWidgets, QtGui, QtCore, QtOpenGL 

from PyQt5.QtWidgets import QApplication, QComboBox, QMainWindow, QMessageBox, QShortcut, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class GUICommands:

    def __init__(self):
        self.method = 0

    def read_folder(self, mode):
        
        folder_path = Path(QtWidgets.QFileDialog.getExistingDirectory(None, 'Select CrystalGrower Output Folder'))
        checkboxes = []
        checkBoxNames = []

        # Setting contents if its in normal mode (no screw dislocation)
        if mode == 1:
            # Deletes current facets
            for chkBox in self.facet_gBox.findChildren(QtWidgets.QCheckBox):
                chkBox.deleteLater()

            

            

            for i in range(numFacets):
                chkBoxName = facets[i]
                checkBoxNames.append(chkBoxName)

                self.chkBoxName = QtWidgets.QCheckBox(self.facet_gBox)
                checkboxes.append(self.chkBoxName)
                # print(checkboxes)

                self.chkBoxName.setEnabled(True)
                self.chkBoxName.stateChanged.connect(self.checkFacet)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(self.chkBoxName.sizePolicy().hasHeightForWidth())
                self.chkBoxName.setSizePolicy(sizePolicy)
                font = QtGui.QFont()
                font.setFamily("Arial")
                font.setPointSize(10)
                self.chkBoxName.setFont(font)
                self.chkBoxName.setText(chkBoxName)
                self.verticalLayout_2.addWidget(self.chkBoxName)

        return folder_path

