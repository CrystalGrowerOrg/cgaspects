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
from pathlib import Path

from CrystalAspects.GUI.gui_commands import GUICommands
from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.data.aspect_ratios import AspectRatio


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowIcon(QtGui.QIcon('icon.png'))
        apply_stylesheet(app, theme='dark_cyan.xml')
        self.setupUi(self)
        self.statusBar().showMessage('CrystalGrower Data Processor v1.0')

        self.commands = GUICommands()
        self.growth = GrowthRate()
        
        self.checked_directions = []
        self.checkboxnames = []
        self.checkboxes = []
        self.growthrates = False
        self.aspectratio = False
        self.growthmod = False
        self.screwdislocations = []
        self.folder_path = ''

        self.plot = True

        self.progressBar.setValue(0)
        # Welcome msg
        print('############################################')
        print('####        CrystalAspects v1.00        ####')
        print('############################################')

        '''###################################################
        ############      Keyboard Shortcuts      ############
        ###################################################'''

        self.openKS = QShortcut(QKeySequence('Ctrl+O'), self)
        self.openKS.activated.connect(self.read_folder)
        self.open_outKS = QShortcut(QKeySequence('Ctrl+Shift+O'), self)
        # self.open_outKS.activated.connect(self.output_folder_button)
        self.closeKS = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.closeKS.activated.connect(QApplication.instance().quit)
        self.resetKS = QShortcut(QKeySequence('Ctrl+R'), self)
        self.resetKS.activated.connect(self.reset_button_function)
        self.applyKS = QShortcut(QKeySequence('Ctrl+A'), self)
        # self.applyKS.activated.connect(self.apply_clicked)


        self.aspectRatio_checkBox.stateChanged.connect(self.aspect_ratio_checked)
        self.reset_button.clicked.connect(self.reset_button_function)
        self.plot_checkBox.setEnabled(True)


        self.setWindowIcon(QtGui.QIcon('icon.png'))

        apply_stylesheet(app, theme='dark_cyan.xml')

        # Open Folder
        try:
            self.simFolder_Button.clicked.connect(lambda: self.read_folder(1))
        except IndexError:
            pass

        self.growthRate_checkBox.stateChanged.connect(self.growth_rate_check)
        self.plot_checkBox.stateChanged.connect(self.plot_check)

        self.run_calc_button.clicked.connect(self.run_calc)
        self.outFolder_Button.clicked.connect(self.output_folder_button)
        # self.count_checkBox.stateChanged.connect(self.count_check)
        # self.aspect_range_checkBox.stateChanged.connect(self.range_check)
        # self.tabWidget.currentChanged.connect(self.tabChanged)


    def read_folder(self, mode):

        self.mode = mode
        find = Find()

        self.folder_path = Path(QtWidgets.QFileDialog.getExistingDirectory(None, 'Select CrystalGrower Output Folder'))
        checkboxes = []
        check_box_names = []

        su_sat, size_files, directions, g_mods, folders = find.find_info(self.folder_path)
        
        if size_files:
            print(bool(size_files))
            self.growthrates = True
            self.growthRate_checkBox.setChecked(True)

        num_directions = len(directions)
        print(directions)

        # Setting contents if its in normal mode (no screw dislocation)
        if self.mode == 1:

            # Deletes current directions
            for chk_box in self.facet_gBox.findChildren(QtWidgets.QCheckBox):
                chk_box.deleteLater()

            for i in range(num_directions):
                chk_box_name = directions[i]
                self.chk_box_direction = QtWidgets.QCheckBox(self.facet_gBox)
                check_box_names.append(chk_box_name)
                checkboxes.append(self.chk_box_direction)
                
                self.chk_box_direction.setEnabled(True)
                self.chk_box_direction.stateChanged.connect(self.check_facet)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(self.chk_box_direction.sizePolicy().hasHeightForWidth())
                self.chk_box_direction.setSizePolicy(sizePolicy)
                font = QtGui.QFont()
                font.setFamily("Arial")
                font.setPointSize(10)
                self.chk_box_direction.setFont(font)
                self.chk_box_direction.setText(chk_box_name)

                self.verticalLayout_2.addWidget(self.chk_box_direction)

            self.checkboxnames = check_box_names
            self.checkboxes = checkboxes
            print(self.checkboxnames)

        '''Creating CrystalAspects folder'''
        find.create_aspects_folder(self.folder_path)

    def check_facet(self, state):
        if state == Qt.Checked:
            chk_box = self.sender()
            print(chk_box)
            for box in self.checkboxes:
                if chk_box == box:
                    print('here')
                    # print(box)
                    checked_facet = self.checkboxnames[self.checkboxes.index(box)]
                    if checked_facet not in self.checked_directions:
                        self.checked_directions.append(checked_facet)


                    # Turns on and off the second aspect ratio fields
                    if len(self.checked_directions) >= 3 and self.aspectRatio_checkBox.isChecked():
                        if self.mode == 1:
                            self.short_facet.setEnabled(True)
                            if self.aspect_range_checkBox.isChecked():
                                self.ms_range_input.setEnabled(True)
                                self.ms_plusminus_label.setEnabled(True)
                                self.ms_spinBox.setEnabled(True)
                                self.ms_percent_label.setEnabled(True)
                    
                    print(self.checked_directions)

        else:
            chk_box = self.sender()
            for box in self.checkboxes:
                if chk_box == box:
                    checked_facet = self.checkboxnames[self.checkboxes.index(box)]

                    try:
                        self.checked_directions.remove(checked_facet)
                        print(self.checked_directions)

                    except NameError:
                        print(self.checked_directions)

                    # Turns on and off the second aspect ratio fields
                    if len(self.checked_directions) < 3:
                        if self.mode == 1:
                            self.short_facet.setEnabled(False)
                            # self.short_facet_label.setEnabled(False)
                            self.ms_range_input.clear()
                            self.ms_spinBox.setValue(0)
                            self.ms_range_input.setEnabled(False)
                            self.ms_plusminus_label.setEnabled(False)
                            self.ms_spinBox.setEnabled(False)
                            self.ms_percent_label.setEnabled(False)

        # Adds directions (updates) to the drop down lists
        if self.mode == 1:
            self.long_facet.clear()
            self.medium_facet.clear()
            self.short_facet.clear()
            for item in self.checked_directions:
                self.long_facet.addItem(item)
                self.medium_facet.addItem(item)
                self.short_facet.addItem(item)


    def aspect_ratio_checked(self, state):

        if self.mode == 1:
            print('Clicked', state)
            if state == Qt.Checked:
                self.aspectratio = True
                self.long_facet.setEnabled(True)
                self.medium_facet.setEnabled(True)
                self.aspect_range_checkBox.setEnabled(True)
                self.count_checkBox.setEnabled(True)
                self.ratio_label1.setEnabled(True)

                if len(self.checked_directions) >= 3:
                    self.short_facet.setEnabled(True)
                    self.ratio_label2.setEnabled(True)

            else:                
                # Clear
                self.long_facet.setEnabled(False)
                self.medium_facet.setEnabled(False)
                self.short_facet.setEnabled(False)
                self.lm_range_input.clear()
                self.ms_range_input.clear()
                self.lm_spinBox.setValue(0)
                self.ms_spinBox.setValue(0)
                self.aspect_range_checkBox.setChecked(False)
                self.aspect_range_checkBox.setEnabled(False)
                self.ratio_label1.setEnabled(False)
                self.ratio_label2.setEnabled(False)
                self.count_checkBox.setChecked(False)
                self.count_checkBox.setEnabled(False)

    def reset_button_function(self):

        self.checked_directions = []
        self.checkboxnames = []
        self.checkboxes = []

        # Initialise Progressbar
        self.progressBar.setValue(0)

        if self.mode == 1:
            # Unchecks selected facets
            for chkBox in self.facet_gBox.findChildren(QtWidgets.QCheckBox):
                chkBox.setChecked(False)
                chkBox.deleteLater()
            # Unchecks Checkboxes and clears the fields
            self.growthRate_checkBox.setChecked(False)
            self.aspectRatio_checkBox.setChecked(False)
            self.plot_checkBox.setChecked(False)
            self.long_facet.setEnabled(False)
            self.medium_facet.setEnabled(False)
            self.short_facet.setEnabled(False)
            self.lm_range_input.clear()
            self.ms_range_input.clear()
            self.lm_spinBox.setValue(0)
            self.ms_spinBox.setValue(0)
            self.lm_range_input.setEnabled(False)
            self.lm_plusminus_label.setEnabled(False)
            self.lm_spinBox.setEnabled(False)
            self.lm_percent_label.setEnabled(False)
            self.ms_range_input.setEnabled(False)
            self.ms_plusminus_label.setEnabled(False)
            self.ms_spinBox.setEnabled(False)
            self.ms_percent_label.setEnabled(False)
            self.aspect_range_checkBox.setChecked(False)
            self.output_textBox.clear()

    def growth_rate_check(self, state):
        if state == Qt.Checked:
            self.growthrates = True
            print('calc_growth [yes(1) or no(0)]= ', self.growthrates)
        else:
            self.growthrates = False
            print('calc_growth [yes(1) or no(0)]= ', self.growthrates)

    def plot_check(self, state):
        if state == Qt.Checked:
            self.plot = True
            print(f'Plot: {self.plot}')
        else:
            self.plot = False
            print(f'Plot: {self.plot}')

    def run_calc(self):
        if self.growthrates:
            growth = GrowthRate()
            growth.run_calc_growth(self.folder_path,
                                   directions=self.checked_directions,
                                   plotting=self.plot)
        if self.aspectratio:
            aspect_ratio = AspectRatio()
            print('Aspect Ratio Selected')

            long = self.long_facet.currentText()
            medium = self.medium_facet.currentText()
            short = self.short_facet.currentText()
            print(short)

            selected_directions = [short, medium, long]
            print(selected_directions)

            find = Find()
            _, _, selected_directions, _, folders = find.find_info(self.folder_path)
            print(folders)
            ar_df = find.build_AR_CDA(folderpath=self.folder_path,
                                      folders=folders,
                                      directions=self.checked_directions,
                                      selected=selected_directions)

            aspect_ratio.defining_equation(directions=self.checked_directions,
                                           ar_df=ar_df)


    def output_folder_button(self):
        try:
            dir_path = os.path.realpath(self.folder_path / "CrystalAspects")
            if sys.platform == "win32":
                os.startfile(dir_path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, dir_path])
            self.statusBar().showMessage('Taking you to the CrystalAspects folder.')
        except NameError:
            try:
                dir_path = os.path.realpath(self.folder_path / "CrystalAspects")
                if sys.platform == "win32":
                    os.startfile(dir_path)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, dir_path])
                self.statusBar().showMessage('Taking you to the CrystalAspects folder.')
            except NameError:        
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Please select CrystalGrower output folder first!")
                msg.setInformativeText('An output folder is created only once you have selected a CrystalGrower output folder.')
                msg.setWindowTitle("Error: Folder not found!")
                msg.exec_()


# Override sys excepthook to prevent app abortion upon any error
# (Reverts to old PyQt4 behaviour of 
# simply printing the traceback to stdout/stderr)



def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

    

if __name__ == "__main__":

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
    

