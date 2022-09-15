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
        print('####        CrystalAspects v1.00        ####')
        print('############################################')

        ######################################################
        ############      Keyboard Shortcuts      ############
        ######################################################

        self.openKS = QShortcut(QKeySequence('Ctrl+O'), self)
        self.openKS.activated.connect(self.readFolder)
        self.open_outKS = QShortcut(QKeySequence('Ctrl+Shift+O'), self)
        self.open_outKS.activated.connect(self.output_folder_button)
        self.closeKS = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.closeKS.activated.connect(QApplication.instance().quit)
        self.resetKS = QShortcut(QKeySequence('Ctrl+R'), self)
        self.resetKS.activated.connect(self.reset_button_function)
        self.applyKS = QShortcut(QKeySequence('Ctrl+A'), self)
        self.applyKS.activated.connect(self.apply_clicked)

        self.setWindowIcon(QtGui.QIcon('icon.png'))

        apply_stylesheet(app, theme='dark_cyan.xml')

        # Open Folder
        try:
            self.simFolder_Button.clicked.connect(self.read_folder)
        except IndexError:
            pass

        # Create a list to store directions being selected
        checked_facets = []

        # Unlock options
        self.aspectRatio_checkBox.stateChanged.connect(self.aspect_ratio_checked)
        self.aspectRatio_checkBox_2.stateChanged.connect(self.aspect_ratio_checked)

        # Collect Variable values
        self.growthRate_checkBox.stateChanged.connect(self.growth_rate_check)
        self.growthRate_checkBox_2.stateChanged.connect(self.growth_rate_check)
        self.plot_checkBox.stateChanged.connect(self.plot_check)
        self.plot_checkBox_2.stateChanged.connect(self.plot_check)
        self.count_checkBox.stateChanged.connect(self.count_check)
        self.aspect_range_checkBox.stateChanged.connect(self.range_check)
        self.tabWidget.currentChanged.connect(self.tabChanged)


        


        # Find current tab and sets search_mode
        
        #self.tabWidget.setCurrentIndex(0)
        search_mode = self.tabWidget.currentIndex() + 1
        

        # Setting post-selection buttons
        self.apply_button.clicked.connect(self.apply_clicked)
        self.apply_button_2.clicked.connect(self.apply_clicked)
        self.outFolder_Button.clicked.connect(self.output_folder_button)
        self.reset_button.clicked.connect(self.reset_button_function)
        self.reset_button_2.clicked.connect(self.reset_button_function)

        #Initialize progressBar
        self.progressBar.setValue(0)

        ######################################################
        ############       Map/Slider Mode        ############
        ######################################################
        
        self.select_summary_map_button.clicked.connect(self.maps_read_summary)
        self.select_summary_slider_button.clicked.connect(self.slider_summary)
        self.generate_map_button.clicked.connect(self.maps_map_function)

        ######################################################
        ############        3D Data Mode          ############
        ######################################################

        #self.select_XYZ_3d_button.clicked.connect(self.read_XYZ1)
        #self.select_sim_3d_button.clicked.connect(self.read_XYZ2)
        self.start_3dcalc_button.clicked.connect(lambda: self.SAVAR_calc('start'))
        self.stop_3dcalc_button.clicked.connect(lambda: self.SAVAR_calc('stop'))


        




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
    

