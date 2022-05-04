# Project Modules 

# Project module imports
from load_GUI import Ui_MainWindow

# PyQT5 imports
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QComboBox, QMainWindow, QMessageBox, QShortcut, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from qt_material import apply_stylesheet

# General imports
import os, sys, time, subprocess
import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import defaultdict
import webbrowser
from natsort import natsorted


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(QtGui.QIcon('icon.png'))
        apply_stylesheet(app, theme='dark_cyan.xml')
        self.setupUi(self)
        self.statusBar().showMessage('CrystalGrower Data Processor v1.0')

        # Welcome msg
        print('############################################')
        print('#### CrystalGrower Data Processor v1.00 ####')
        print('############################################')
        print('   - by Nathan de Bruyn & Alvin J Walisinghe\n\n')

# Override sys excepthook to prevent app abortion upon any error
# (Reverts to old PyQt4 behaviour of 
# simply printing the traceback to stdout/stderr)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

    

if __name__ == "__main__":
    import sys

    # Override sys excepthook to prevent app abortion upon any error
    sys.excepthook = except_hook


    # Setting taskbar icon permissions - windows
    try:
        import ctypes

        appid = u'CNM.CrystalGrower.DataProcessor.v1.0'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except:
        pass

    # ############# Runs the application ############## #
    QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
    

