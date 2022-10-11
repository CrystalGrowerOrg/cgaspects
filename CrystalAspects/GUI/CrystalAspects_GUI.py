# PyQT5 imports
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QShortcut,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from qt_material import apply_stylesheet

# General imports
import os, sys, subprocess
import pandas as pd
from collections import namedtuple
from pathlib import Path
import logging

# Project Module imports

from CrystalAspects.GUI.load_GUI import Ui_MainWindow
from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.tools.visualiser import Visualiser
from CrystalAspects.tools.crystal_slider import create_slider
from CrystalAspects.visualisation.plot_data import Plotting
from CrystalAspects.visualisation.replotting import Replotting

basedir = os.path.dirname(__file__)

logging.basicConfig(
    level=logging.DEBUG,
    filename="CrystalAspects.log",
    filemode="w",
    format="%(asctime)s-%(levelname)s: %(message)s",
)

logger = logging.getLogger("CrystalAspects_Logger")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        apply_stylesheet(app, theme="dark_cyan.xml")

        self.setupUi(self)
        self.statusBar().showMessage("CrystalGrower Data Processor v1.0")

        self.growth = GrowthRate()
        
        apply_stylesheet(app, theme="dark_cyan.xml")

        self.welcome_message()
        self.key_shortcuts()
        self.connect_buttons()
        self.init_parameters()

    def init_parameters(self):

        self.checked_directions = []
        self.checkboxnames = []
        self.checkboxes = []
        self.growthrates = False
        self.aspectratio = False
        self.growthmod = False
        self.cda = False
        self.pca = False
        self.sa_vol = False
        self.screwdislocations = []
        self.folder_path = ""
        self.folders = []
        self.mode = 1
        self.plot = False
        self.xyz = None
        self.xyz_list = []

        self.summary_csv = None
        self.replot_info = None
        self.replot_folder = None
        self.AR_csv = None
        self.SAVAR_csv = None
        self.GrowthRate_csv = None

        self.progressBar.setValue(0)

    def key_shortcuts(self):

        self.openKS = QShortcut(QKeySequence("Ctrl+O"), self)
        self.openKS.activated.connect(self.read_folder)
        self.open_outKS = QShortcut(QKeySequence("Ctrl+Shift+O"), self)
        # self.open_outKS.activated.connect(self.output_folder_button)
        self.closeKS = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.closeKS.activated.connect(QApplication.instance().quit)
        self.resetKS = QShortcut(QKeySequence("Ctrl+R"), self)
        self.resetKS.activated.connect(self.reset_button_function)
        self.applyKS = QShortcut(QKeySequence("Ctrl+A"), self)
        # self.applyKS.activated.connect(self.apply_clicked)
    
    def welcome_message(self):
        print("############################################")
        print("####        CrystalAspects v1.00        ####")
        print("############################################")

    def connect_buttons(self):
        
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # Open Folder
        try:
            self.simFolder_Button.clicked.connect(lambda: self.read_folder(self.mode))
        except IndexError:
            pass

        self.growthRate_checkBox.stateChanged.connect(self.growth_rate_check)
        self.plot_checkBox.stateChanged.connect(self.plot_check)
        self.run_calc_button.clicked.connect(self.run_calc)
        self.AR_browse_button.clicked.connect(self.replot_AR_read)
        self.GrowthRate_browse_button.clicked.connect(self.replot_GrowthRate_read)

        self.plot_AR_button.clicked.connect(lambda: self.call_replot(1))
        self.plot_GrowthRate_button.clicked.connect(lambda: self.call_replot(2))
        self.select_summary_slider_button.clicked.connect(self.read_summary_vis)

        # Checkboxes
        self.aspectRatio_checkBox.stateChanged.connect(self.aspect_ratio_checked)
        self.pca_checkBox.stateChanged.connect(self.pca_checked)
        self.cda_checkBox.stateChanged.connect(self.cda_checked)
        self.sa_vol_checkBox.stateChanged.connect(self.sa_vol_checked)
        self.reset_button.clicked.connect(self.reset_button_function)
        self.plot_checkBox.setEnabled(True)
        self.outFolder_Button.clicked.connect(self.output_folder_button)
        # self.count_checkBox.stateChanged.connect(self.count_check)
        # self.aspect_range_checkBox.stateChanged.connect(self.range_check)

    def read_summary_vis(self):
        create_slider.read_summary(self)

    def read_folder(self, mode):
        find = Find()

        if self.mode == 2:
            slider = create_slider()
            self.folder_path, self.xyz_list = slider.read_crystals()
            find.create_aspects_folder(self.folder_path)
            Visualiser.initGUI(self, self.xyz_list)
            self.select_summary_slider_button.setEnabled(True)
            
        if self.mode == 1:

            self.folder_path = Path(
                QtWidgets.QFileDialog.getExistingDirectory(
                    None, "Select CrystalGrower Output Folder"
                )
            )
            checkboxes = []
            check_box_names = []

            file_info = find.find_info(self.folder_path)

            self.summary_file = file_info.summary_file

            self.folders = file_info.folders

            if file_info.size_files:
                self.growthrates = True
                self.growthRate_checkBox.setChecked(True)

            if self.growthrates is False:
                self.growthRate_checkBox.setEnabled(False)

            num_directions = len(file_info.directions)
            print("Number of Directions:", num_directions)

            # Deletes current directions
            for chk_box in self.facet_gBox.findChildren(QtWidgets.QCheckBox):
                chk_box.deleteLater()

            for i in range(num_directions):
                chk_box_name = file_info.directions[i]
                self.chk_box_direction = QtWidgets.QCheckBox(self.facet_gBox)
                check_box_names.append(chk_box_name)
                checkboxes.append(self.chk_box_direction)

                self.chk_box_direction.setEnabled(True)
                self.chk_box_direction.stateChanged.connect(self.check_facet)
                sizePolicy = QtWidgets.QSizePolicy(
                    QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
                )
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(
                    self.chk_box_direction.sizePolicy().hasHeightForWidth()
                )
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

            """Creating CrystalAspects folder"""
            logger.debug(
                "Filepath [%s] read and CrystalAspects folder created at: %s",
                str(self.folder_path)
            )

    def check_facet(self, state):
        if state == Qt.Checked:
            chk_box = self.sender()
            print(chk_box)
            for box in self.checkboxes:
                if chk_box == box:
                    # print(box)
                    checked_facet = self.checkboxnames[self.checkboxes.index(box)]
                    if checked_facet not in self.checked_directions:
                        self.checked_directions.append(checked_facet)

                    # Turns on and off the second aspect ratio fields
                    if (
                        len(self.checked_directions) >= 3
                        and self.aspectRatio_checkBox.isChecked()
                    ):
                        if self.mode == 1:
                            self.short_facet.setEnabled(True)
                            if self.aspect_range_checkBox.isChecked():
                                self.ms_range_input.setEnabled(True)
                                self.ms_plusminus_label.setEnabled(True)
                                self.ms_spinBox.setEnabled(True)
                                self.ms_percent_label.setEnabled(True)

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

        if state == Qt.Checked:
            self.aspectratio = True
            self.pca_checkBox.setEnabled(True)
            self.cda_checkBox.setEnabled(True)

            if self.cda:
                self.long_facet.setEnabled(True)
                self.medium_facet.setEnabled(True)
                self.aspect_range_checkBox.setEnabled(True)
                # self.count_checkBox.setEnabled(True)
                self.ratio_label1.setEnabled(True)

                if len(self.checked_directions) >= 3:
                    self.short_facet.setEnabled(True)
                    self.ratio_label2.setEnabled(True)

        else:
            # Clear
            self.pca_checkBox.setEnabled(False)
            self.cda_checkBox.setEnabled(False)
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

        self.init_parameters()

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
            self.cda_checkBox.setChecked(False)
            self.pca_checkBox.setChecked(False)
            self.sa_vol_checkBox.setChecked(False)
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

        self.summary_cs_label.setEnabled(False)
        self.summaryfile_lineEdit.setEnabled(False)
        self.summaryfile_browse_button.setEnabled(False)
        self.plot_AR_button.setEnabled(False)
        self.plot_GrowthRate_button.setEnabled(False)
        self.plot_SAVAR_button.setEnabled(False)
        self.plot_SA_button.setEnabled(False)
        self.plot_vol_button.setEnabled(False)

    def input_directions(self, directions):
        check_box_names = []
        checkboxes = []

        num_directions = len(directions)
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
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(1)
            sizePolicy.setHeightForWidth(
                self.chk_box_direction.sizePolicy().hasHeightForWidth()
            )
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

    def growth_rate_check(self, state):
        if state == Qt.Checked:
            self.growthrates = True
            print(f"Growth Rates: {self.growthrates}")
        else:
            self.growthrates = False
            print(f"Growth Rates: {self.growthrates}")

    def pca_checked(self, state):
        if state == Qt.Checked:
            self.pca = True
            print(f"PCA: {self.pca}")
        else:
            self.pca = False
            print(f"PCA: {self.pca}")

    def sa_vol_checked(self, state):
        if state == Qt.Checked:
            self.sa_vol = True
            print(f"SA:V {self.sa_vol}")
        else:
            self.sa_vol = False
            print(f"SA:V {self.sa_vol}")

    def cda_checked(self, state):
        if state == Qt.Checked:
            self.cda = True
            print(f"PCA: {self.cda}")

            self.long_facet.setEnabled(True)
            self.medium_facet.setEnabled(True)
            self.aspect_range_checkBox.setEnabled(True)
            # self.count_checkBox.setEnabled(True)
            self.ratio_label1.setEnabled(True)

            if len(self.checked_directions) >= 3:
                self.short_facet.setEnabled(True)
                self.ratio_label2.setEnabled(True)
        else:
            self.cda = False
            print("CDA is not checked")
            print(f"CDA: {self.cda}")

            self.long_facet.setEnabled(False)
            self.medium_facet.setEnabled(False)
            self.aspect_range_checkBox.setEnabled(False)
            self.count_checkBox.setEnabled(False)
            self.ratio_label1.setEnabled(False)
            self.short_facet.setEnabled(False)
            self.ratio_label2.setEnabled(False)

    def plot_check(self, state):
        if state == Qt.Checked:
            self.plot = True
            print(f"Plot: {self.plot}")
        else:
            self.plot = False
            print(f"Plot: {self.plot}")

    def replot_AR_read(self):
        input_path = self.ar_lineEdit.text()

        if input_path != "":
            input_path = Path(input_path)

            if input_path.exists() and input_path.suffix == ".csv":
                self.AR_csv = input_path
                self.plot_AR_button.setEnabled(True)

        else:
            input_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                None, "Select Aspect Ratio .csv"
            )
            input_path = Path(input_path)
            if input_path.exists() and input_path.suffix == ".csv":
                self.AR_csv = input_path
                self.plot_AR_button.setEnabled(True)

        self.ar_lineEdit.setText(str(input_path))

        self.reread_info(input_path)

    def replot_GrowthRate_read(self):
        input_path = self.GrowthRate_lineEdit.text()

        if input_path != "":
            input_path = Path(input_path)

            if input_path.exists() and input_path.suffix == ".csv":
                self.GrowthRate_csv = input_path
                self.plot_GrowthRate_button.setEnabled(True)

        else:
            input_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                None, "Select Growth Rate .csv"
            )
            input_path = Path(input_path)
            if input_path.exists() and input_path.suffix == ".csv":
                self.GrowthRate_csv = input_path
                self.plot_GrowthRate_button.setEnabled(True)

        self.GrowthRate_lineEdit.setText(str(input_path))

    def replot_summary_read(self):

        find = Find()

        input_path = self.summaryfile_lineEdit.text()

        if input_path != "":
            input_path = Path(input_path)

            if input_path.exists() and input_path.suffix == ".csv":
                self.summary_csv = input_path

        else:
            input_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                None, "Select Growth Rate .csv"
            )
            input_path = Path(input_path)
            if input_path.exists() and input_path.suffix == ".csv":
                self.summary_csv = input_path

        self.summaryfile_lineEdit.setText(str(input_path))

        find.summary_compare(
            summary_csv=input_path,
            savefolder=self.replot_folder,
            aspect_csv=self.AR_csv,
        )

        self.AR_csv = f"{self.replot_folder}/aspectratio_energy.csv"

        self.replot_info._replace(Energies=True)

    def reread_info(self, csv):

        find = Find()
        replot_info = namedtuple(
            "PresentData", "Directions, PCA, CDA, Equations, Energies, SAVol"
        )

        self.replot_folder = find.create_aspects_folder(self.folder_path)
        df = pd.read_csv(csv)

        directions = []
        energies = False
        pca = False
        cda = False
        equations = False
        savar = False

        for col in df.columns:
            if col.startswith(" ") or col.startswith("-"):
                directions.append(col)
            if col.startswith("interactions") or col.startswith("tile"):
                energies = True
            if col.startswith("S:M"):
                pca = True
            if col.startswith("S/M"):
                cda = True
            if col.startswith("CDA_Equations"):
                equations = True
            if col.startswith("SA"):
                savar = True

        self.input_directions(directions=directions)

        if energies is False:
            self.summary_cs_label.setEnabled(True)
            self.summaryfile_lineEdit.setEnabled(True)
            self.summaryfile_browse_button.setEnabled(True)

        self.replot_info = replot_info(
            Directions=directions,
            PCA=pca,
            CDA=cda,
            Equations=equations,
            Energies=energies,
            SAVol=savar,
        )

    def call_replot(self, replot_mode):
        replot = Replotting()

        if replot_mode == 1:
            replot.replot_AR(
                csv=self.AR_csv, info=self.replot_info, selected=self.checked_directions
            )

        if replot_mode == 2:
            replot.replot_GrowthRate(
                csv=self.GrowthRate_csv, selected=self.checked_directions
            )

    def run_calc(self):

        logger.info(
            "Calculation started with:\n\
            PCA: %s\n\
            CDA: %s\n\
            Growth Rates: %s\n\
            Plotting: %s\n",
            self.pca,
            self.cda,
            self.growthrates,
            self.plot,
        )

        logger.info("All Selected Directions: %s\n", self.checked_directions)

        find = Find()
        save_folder = find.create_aspects_folder(self.folder_path)
        plotting = Plotting()

        if self.growthrates:
            growth = GrowthRate()
            growth.run_calc_growth(
                self.folder_path,
                directions=self.checked_directions,
                plotting=self.plot,
                savefolder=save_folder,
            )

        if self.sa_vol and self.pca is False:
            aspect_ratio = AspectRatio()
            savar_df = aspect_ratio.savar_calc(
                subfolder=self.folder_path, savefolder=save_folder
            )
            savar_df_final = find.summary_compare(
                summary_csv=self.summary_file,
                aspect_df=savar_df,
                savefolder=save_folder,
            )
            if self.plot:
                plotting.SAVAR_plot(df=savar_df_final, folderpath=save_folder)

        if self.pca and self.sa_vol:
            aspect_ratio = AspectRatio()
            pca_df = aspect_ratio.shape_all(
                subfolder=self.folder_path, savefolder=save_folder
            )
            plot_df = find.summary_compare(
                summary_csv=self.summary_file, aspect_df=pca_df, savefolder=save_folder
            )
            if self.plot:
                plotting.SAVAR_plot(df=plot_df, folderpath=save_folder)
                plotting.build_PCAZingg(df=plot_df, folderpath=save_folder)

        if self.aspectratio:
            aspect_ratio = AspectRatio()

            if self.cda:

                long = self.long_facet.currentText()
                medium = self.medium_facet.currentText()
                short = self.short_facet.currentText()

                selected_directions = [short, medium, long]

                logger.info(
                    "Selected Directions (for CDA): %s, %s, %s\n", short, medium, long
                )

                cda_df = aspect_ratio.build_AR_CDA(
                    folderpath=self.folder_path,
                    folders=self.folders,
                    directions=self.checked_directions,
                    selected=selected_directions,
                    savefolder=save_folder,
                )

                zn_df = aspect_ratio.defining_equation(
                    directions=selected_directions, ar_df=cda_df, filepath=save_folder
                )
                zn_df_final = find.summary_compare(
                    summary_csv=self.summary_file,
                    aspect_df=zn_df,
                    savefolder=save_folder,
                )

                if self.plot:
                    plotting.CDA_Plot(df=zn_df_final, folderpath=save_folder)
                    plotting.build_zingg_seperated_i(
                        df=zn_df_final, folderpath=save_folder
                    )
                    plotting.Aspect_Extended_Plot(
                        df=zn_df_final,
                        selected=selected_directions,
                        folderpath=save_folder,
                    )

            if self.pca and self.sa_vol:
                aspect_ratio.PCA_shape_percentage(pca_df=pca_df, folderpath=save_folder)

            if self.pca and self.sa_vol is False:
                pca_df = aspect_ratio.build_AR_PCA(
                    subfolder=self.folder_path, savefolder=save_folder
                )

                aspect_ratio.PCA_shape_percentage(pca_df=pca_df, folderpath=save_folder)
                if self.plot:
                    plotting.build_PCAZingg(df=pca_df, folderpath=save_folder)

            if self.pca and self.cda:
                pca_cda_df = aspect_ratio.Zingg_CDA_shape_percentage(
                    pca_df=pca_df, cda_df=zn_df, folderpath=save_folder
                )
                if self.plot:
                    plotting.PCA_CDA_Plot(df=pca_cda_df, folderpath=save_folder)
                    plotting.build_PCAZingg(df=pca_df, folderpath=save_folder)

    def output_folder_button(self):
        try:
            dir_path = os.path.realpath(self.folder_path / "CrystalAspects")
            if sys.platform == "win32":
                os.startfile(dir_path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, dir_path])
            self.statusBar().showMessage("Taking you to the CrystalAspects folder.")
        except NameError:
            try:
                dir_path = os.path.realpath(self.folder_path / "CrystalAspects")
                if sys.platform == "win32":
                    os.startfile(dir_path)
                else:
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, dir_path])
                self.statusBar().showMessage("Taking you to the CrystalAspects folder.")
            except NameError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Please select CrystalGrower output folder first!")
                msg.setInformativeText(
                    "An output folder is created only once you have selected a CrystalGrower output folder."
                )
                msg.setWindowTitle("Error: Folder not found!")
                msg.exec_()

    def slider_change(self, var, slider_list, dspinbox_list, summ_df, crystals):
        slider = self.sender()
        i = 0
        for name in slider_list:
            if name == slider:
                slider_value = name.value()
                print(slider_value)
                dspinbox_list[i].setValue(slider_value / 100)
            i += 1
        value_list = []
        filter_df = summ_df
        for i in range(var):
            value = slider_list[i].value() / 100
            print(f'locking for: {value}')
            filter_df = filter_df[(summ_df.iloc[:, i] == value)]
            value_list.append(value)
        print('Combination: ', value_list)
        print(filter_df)
        for row in filter_df.index:
            XYZ_vals = crystals[row]
            self.output_textBox_3.append(f'Row Number: {row}')
            Visualiser.update_XYZ(self, XYZ_vals)

    def dspinbox_change(self, var, dspinbox_list, slider_list):
        dspinbox = self.sender()
        i = 0
        for name in dspinbox_list:
            if name == dspinbox:
                dspinbox_value = name.value()
                print(dspinbox_value)
                slider_list[i].setValue(int(dspinbox_value * 100))
            i += 1
        value_list = []
        for i in range(var):
            value = dspinbox_list[i].value()
            value_list.append(value)
        print(value_list)

    def tabChanged(self):
        self.mode = self.tabWidget.currentIndex() + 1
        if self.mode == 1:
            print('Normal Mode selected')
            self.simFolder_Button.setText('Open Simulations Folder')
            self.progressBar.show()
        if self.mode == 2:
            print('3D Data mode selected')
            self.simFolder_Button.setText('XYZ/Simulations Folder')
            self.output_textBox_3.setText('Please open the folder containing the XYZ file(s) to start using the Visualiser/Sliders')



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

        appid = "CNM.CrystalGrower.DataProcessor.v1.0"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except:
        pass

    # ############# Runs the application ############## #
    QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'icon.png')))
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())
