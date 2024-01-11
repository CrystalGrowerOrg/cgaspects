
import logging
import os
import sys
from collections import namedtuple
from pathlib import Path
from typing import List
from natsort import natsorted
from PySide6 import QtWidgets
from PySide6.QtCore import (
    QObject,
    QThreadPool,
    Signal,
)
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMenu, QMessageBox
from PySide6.QtCore import Qt
from qt_material import apply_stylesheet

from crystalaspects.analysis.aspect_ratios import AspectRatio
from crystalaspects.analysis.growth_rates import GrowthRate
from crystalaspects.visualisation.plot_data import Plotting
from crystalaspects.analysis.gui_threads import WorkerXYZ
from crystalaspects.analysis.shape_analysis import CrystalShape
from crystalaspects.fileio.logging import setup_logging
from crystalaspects.fileio.opendir import open_directory
from crystalaspects.fileio.find_data import read_crystals, find_info
from crystalaspects.gui.utils.crystal_slider import create_slider
from crystalaspects.gui.dialogs.settings import SettingsDialog
from crystalaspects.gui.openGL import VisualisationWidget

# Project Module imports
from crystalaspects.gui.load_ui import Ui_MainWindow
from crystalaspects.visualisation.plot_dialog import PlottingDialog

log_dict = {"basic": "DEBUG", "console": "INFO"}
setup_logging(**log_dict)
logger = logging.getLogger("CA:GUI")
logger.critical("LOGGING AT %s", log_dict)


class GUIWorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals:
    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    progress
        int indicating % progress
    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    location = Signal(object)
    progress = Signal(int)
    message = Signal(str)


class MainWindow(QMainWindow, Ui_MainWindow):
    status_timeout = 1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        print(QtWidgets.QStyleFactory.keys())
        self.apply_style(theme_main="dark", theme_colour="teal")

        self.setupUi(self)
        self.update_statusbar("CrystalAspects v1.0")

        self.threadpool = QThreadPool()

        self.welcome_message()
        self.setup_keyboard_shortcuts()
        self.setup_button_connections()
        self.setup_menubar()

        self.worker_signals = GUIWorkerSignals()
        self.aspectratio = AspectRatio(signals=self.worker_signals)
        self.growthrate = GrowthRate(signals=self.worker_signals)
        self.worker_signals.location.connect(self.set_output_folder)
        self.worker_signals.result.connect(self.set_results)
        # Other self variables
        self.sim_num: int | None = None
        self.input_folder: Path | None = None
        self.output_folder: Path | None = None
        self.xyz_files: List[Path] = []
        self.selected_directions: list = []
        self.plotting_csv: Path | None = None

        self.xyz_id_frame.hide()
        self.movie_controls_frame.hide()

        self.settings_dialog = SettingsDialog(self)
        self.openglwidget = VisualisationWidget()
        self.gl_vLayout.addWidget(self.openglwidget)
        self.settings_toolButton.clicked.connect(self.show_settings())

    def setup_menubar(self):
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create two menus
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        crystalaspects_menu = QMenu("CrystalAspects", self)
        crystalclear_menu = QMenu("CrystalClear", self)
        Calculations_menu = QMenu("Calculations", self)

        # Add menus to the menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(crystalaspects_menu)
        menu_bar.addMenu(crystalclear_menu)

        # Create actions for the File menu
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        import_action = QAction("Import", self)
        exit_action = QAction("Exit", self)

        # Add actions to the File menu
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(import_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Connect actions from the File menu
        import_action.triggered.connect(self.import_xyz)

        # Create actions for the Edit menu
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)

        # Add actions to the Edit menu
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)

        # Create actions to the crystalaspects menu
        aspect_ratio_action = QAction("Aspect Ratio", self)
        growth_rate_action = QAction("Growth Rates", self)
        plotting_action = QAction("Plotting", self)
        particle_swarm_action = QAction("Particle Swarm Analysis", self)
        # docking_calc_action = QAction("Docking Calculation", self)

        # Add actions and Submenu to crystalaspects menu
        calculate_menu = crystalaspects_menu.addMenu("Calculate")
        calculate_menu.addAction(aspect_ratio_action)
        calculate_menu.addAction(growth_rate_action)
        crystalaspects_menu.addAction(particle_swarm_action)
        crystalaspects_menu.addAction(plotting_action)
        # crystalaspects_menu.addAction(docking_calc_action)

        # Connect the crystalaspects actions
        aspect_ratio_action.triggered.connect(self.calculate_aspect_ratio)
        growth_rate_action.triggered.connect(self.calculate_growth_rates)
        particle_swarm_action.triggered.connect(self.particle_swarm_analysis)
        plotting_action.triggered.connect(self.replotting_called)
        exit_action.triggered.connect(self.close_application)
        # docking_calc_action.triggered.connect(self.docking_calc)

        # Create the CrystalClear actions
        generate_structure_action = QAction("Generate Structure", self)
        generate_net_action = QAction("Generate Net", self)
        solvent_screen_action = QAction("Solvent Screening", self)

        # Add action and Submenu to CrystalClear menu
        crystalclear_menu.addAction(generate_structure_action)
        crystalclear_menu.addAction(generate_net_action)
        crystalclear_menu.addAction(solvent_screen_action)

        # Connect the CrystalClear actions
        generate_structure_action.triggered.connect(self.generate_structure_file)
        generate_net_action.triggered.connect(self.generate_net_file)
        solvent_screen_action.triggered.connect(self.solvent_screening)

    def apply_style(self, theme_main, theme_colour, density=-1):
        extra = {
            # Font
            "font_family": "Roboto",
            # Density Scale
            "density_scale": str(density),
        }

        apply_stylesheet(
            self,
            f"{theme_main}_{theme_colour}.xml",
            invert_secondary=False,
            extra=extra,
        )

    def setup_button_connections(self):
        # Visualisation Buttons
        self.select_summary_slider_button.clicked.connect(
            lambda: self.read_summary_vis()
        )
        self.play_button.clicked.connect(self.play_movie)
        self.import_pushButton.clicked.connect(
            lambda: self.import_and_visualise_xyz(folder=None)
        )
        self.view_results_pushButton.clicked.connect(
            lambda: open_directory(path=self.output_folder)
        )

        self.aspect_ratio_pushButton.clicked.connect(self.calculate_aspect_ratio)
        self.growth_rate_pushButton.clicked.connect(self.calculate_growth_rates)

        self.plot_browse_toolButton.clicked.connect(self.browse_plot_csv)
        self.plot_lineEdit.textChanged.connect(self.set_plotting)
        self.plot_pushButton.clicked.connect(self.replotting_called)

    def setup_keyboard_shortcuts(self):
        # Close Application with Ctrl+Q or Cmd+Q
        # close_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        # close_shortcut.activated.connect(self.close_application)
        # mac_close_shortcut = QShortcut(QKeySequence(Qt.MetaModifier | Qt.Key_Q), self)
        # mac_close_shortcut.activated.connect(self.close_application)

        # Import XYZ file with Ctrl+I
        import_xyz_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        import_xyz_shortcut.activated.connect(
            lambda: self.import_and_visualise_xyz(folder=None)
        )
        # Import XYZ file with Ctrl+F
        browse_for_batch = QShortcut(QKeySequence("Ctrl+F"), self)
        browse_for_batch.activated.connect(self.browse)
        # Display XYZ file(s) with Ctrl+D
        set_xyz = QShortcut(QKeySequence("Ctrl+D"), self)
        set_xyz.activated.connect(self.set_visualiser)
        # Open results folder with Ctrl+O
        self.view_results = QShortcut(QKeySequence("Ctrl+O"), self)
        self.view_results.activated.connect(
            lambda: open_directory(path=self.output_folder)
            if self.output_folder
            else None
        )
    
    def show_settings(self):
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.activateWindow()

    def welcome_message(self):
        self.log_message(
            "############################################", log_level="info", gui=False
        )
        self.log_message(
            "####        CrystalAspects v1.00        ####", log_level="info", gui=False
        )
        self.log_message(
            "############################################", log_level="info", gui=False
        )
        self.log_message(
            "     The CrystalGrower Data Analysis Program",
            log_level="info",
            gui=False,
        )

    def log_message(self, message, log_level, gui=False):
        message = str(message)
        log_level_method = getattr(logger, log_level.lower(), logger.debug)

        if gui or log_level in ["info", "warning"]:
            # Update the status bar with the message
            self.update_statusbar(message)

        # Log the message with given level
        log_level_method(message)

    def set_output_folder(self, value):
        self.output_folder = Path(value)
        self.view_results_pushButton.setEnabled(True)

    def import_and_visualise_xyz(self, folder=None):
        imported = self.import_xyz(folder=folder)
        if imported:
            self.set_visualiser()

    def set_visualiser(self):
        n_xyz = len(self.xyz_files)
        if n_xyz == 0:
            self.log_message(f"{n_xyz} XYZ files found to set to self!", "warning")
        if n_xyz > 0:
            self.init_opengl(self.xyz_files)

            # Shape analysis to determine xyz, or xyz movie
            result = self.movie_or_single_frame(0)

            # Adjust the slider range based on the number of XYZ files in the list
            self.xyz_spinBox.setRange(0, len(self.xyz_files) - 1)
            self.xyz_spinBox.setValue(0)

            self.init_crystal(result)

            self.select_summary_slider_button.setEnabled(True)
            self.log_message(f"{len(self.xyz_files)} XYZ files set to self!", "info")
            self.update_XYZ_info(self.openglwidget.xyz)
            self.xyz_id_frame.show()
            self.set_batch_type()

    def import_xyz(self, folder=None):
        """Import XYZ file(s) by first opening the folder
        and then opening them via an OpenGL widget"""
        self.log_message("Reading Images...", "info")
        # Initialize or clear the list of XYZ files
        self.xyz_files = []
        # Read the .XYZ files from the selected folder
        folder, xyz_files = read_crystals(folder)

        # Check for valid data
        if (folder, xyz_files) == (None, None):
            self.log_message(
                "Error: No valid XYZ files found in the directory.", "error"
            )
            return False

        self.xyz_files = (
            xyz_files  # Assuming you want to update self.xyz_files with the new list
        )
        self.input_folder = folder
        self.batch_lineEdit.setText(str(self.input_folder))
        self.log_message(f"Initial XYZ list: {xyz_files}", "debug")

        if folder:
            self.xyz_files = natsorted(xyz_files)

        return True

    def movie_or_single_frame(self, index):
        folder = self.input_folder
        if 0 <= index < len(self.xyz_files):
            file_name = self.xyz_files[index]
            full_file_path = os.path.join(folder, file_name)
            results = namedtuple("CrystalXYZ", ("xyz", "xyz_movie"))
            xyz, xyz_movie, progress = CrystalShape.read_XYZ(full_file_path)
            result = results(xyz=xyz, xyz_movie=xyz_movie)

            return result

    def update_XYZ_info(self, xyz):
        worker_xyz = WorkerXYZ(xyz)
        worker_xyz.signals.result.connect(self.insert_info)
        worker_xyz.signals.message.connect(self.update_statusbar)
        self.threadpool.start(worker_xyz)

    def update_movie(self, frame):
        if frame != self.frame:
            self.update_frame(frame)
            self.frame_spinBox.setValue(frame)
            self.frame_slider.setValue(frame)

    def play_movie(self, frames):
        for frame in range(frames):
            self.update_frame(frame)
            self.current_frame_comboBox.setCurrentIndex(frame)
            self.current_frame_spinBox.setValue(frame)
            self.frame_slider.setValue(frame)

    def close_application(self):
        self.log_message("Closing Application", "info")
        self.close()

    def browse(self):
        try:
            # Attempt to get the directory from the file dialog
            folder = QFileDialog.getExistingDirectory(
                self,
                "Select Folder",
                "./",
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
            )

            # Check if the folder selection was canceled or empty and handle appropriately
            if folder:
                self.batch_lineEdit.clear()
                self.batch_lineEdit.setText(str(folder))
            else:
                # Handle the case where no folder was selected
                self.log_message(
                    "Folder selection was canceled or no folder was selected.", "warning"
                )

        # Note: Bare Exception
        except Exception as e:
            self.log_message(f"An error occurred: {e}", "error")

    def set_batch_type(self):
        folder = Path(self.batch_lineEdit.text())
        self.aspect_ratio_pushButton.setEnabled(False)
        self.growth_rate_pushButton.setEnabled(False)
        try:
            if folder.is_dir():
                self.input_folder = folder
                information = find_info(folder)
                if information.directions and information.size_files:
                    self.growth_rate_pushButton.setEnabled(True)
                    self.growthrate.set_folder(folder=folder)
                    self.growthrate.set_information(information=information)
                if information.directions:
                    self.aspect_ratio_pushButton.setEnabled(True)
                    self.aspectratio.set_folder(folder=folder)
                    self.aspectratio.set_information(information=information)
                if not (information.directions or information.size_files):
                    self.log_message(information, "error")
                    raise FileNotFoundError(
                        "No suitable CG output file found in the selected directory."
                    )
                self.input_folder = Path(folder)

            else:
                raise NotADirectoryError(f"{folder} is not a valid directory.")

        except (FileNotFoundError, NotADirectoryError) as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                f"An error occurred: {e}\nPlease make sure the folder you have selected "
                "contains CrystalGrower output from the simulation(s)."
            )
            msg.setWindowTitle("Error! No CrystalGrower files detected.")
            msg.exec()
            return (None, None)

    def calculate_aspect_ratio(self):
        self.aspectratio.calculate_aspect_ratio()

    def calculate_growth_rates(self):
        self.growthrate.calculate_growth_rates()

    def browse_plot_csv(self):
        try:
            # Attempt to get the directory from the file dialog
            plotting_csv = QFileDialog.getOpenFileName(
                self, "Select CSV File", "./", "CSV Files (*.csv);;All Files (*)"
            )[0]

            # Check if the folder selection was canceled or empty and handle appropriately
            if plotting_csv:
                plotting_csv = Path(plotting_csv)
                if plotting_csv.is_file():
                    self.plot_lineEdit.setText(str(plotting_csv))
            else:
                # Handle the case where no folder was selected
                self.log_message(
                    "File selection was canceled or no file was selected.", "error"
                )

        # Note: Bare Exception
        except Exception as e:
            self.log_message(f"An error occurred: {e}", "error")

    def set_plotting(self, value):
        if Path(value).is_file():
            self.plotting_csv = Path(value)
            self.plot_pushButton.setEnabled(True)
            self.log_message(f"Plotting CSV set to {self.plotting_csv}", "info")
        else:
            self.plot_pushButton.setEnabled(False)
            self.plotting_csv = None
            self.log_message(f"Plotting CSV set to None", "debug")

    def set_results(self, value):
        self.plot_lineEdit.setText(str(value.csv))
        self.log_message(f"Accepting incoming result to GUI {value}", "debug")
        if value.selected:
            self.selected_directions = value.selected
            self.log_message(
                f"Selected Directions set to: {self.selected_directions}", "debug"
            )
        if value.folder:
            self.output_folder = value.folder
            self.log_message(f"Output folder updated: [{self.output_folder}]", "debug")

    def replotting_called(self):
        if self.plotting_csv:
            self.log_message(f"Plotting file: {self.plotting_csv}", "info")

            PlottingDialogs = PlottingDialog()
            PlottingDialogs.plotting_info(csv=self.plotting_csv)
            PlottingDialogs.show()

    def particle_swarm_analysis(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Particle Swarm Analysis")
        msg_box.setText("Particle Swarm Analysis is coming soon!")
        msg_box.exec()

    def generate_structure_file(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("CrystalClear is coming soon!")
        msg_box.exec()

    def generate_net_file(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("CrystalClear is coming soon!")
        msg_box.exec()

    def solvent_screening(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("CrystalClear is coming soon!")
        msg_box.exec()

    def docking_calc(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Docking for growth modifier and impurities is coming soon!")
        msg_box.exec()

    def read_summary_vis(self):
        self.log_message("Reading Summary file...", "info")
        create_slider.read_summary(self)

    def slider_change(self, var, slider_list, dspinbox_list, summ_df, crystals):
        slider = self.sender()
        i = 0
        for name in slider_list:
            if name == slider:
                slider_value = name.value()
                self.log_message(slider_value, log_level="debug")
                dspinbox_list[i].setValue(slider_value / 100)
            i += 1
        value_list = []
        filter_df = summ_df
        for i in range(var):
            value = slider_list[i].value() / 100
            self.log_message(f"looking for: {value}", log_level="debug")
            filter_df = filter_df[(summ_df.iloc[:, i] == value)]
            value_list.append(value)
        self.log_message(f"Combination: {value_list}", "debug")
        self.log_message(filter_df, "debug")
        for row in filter_df.index:
            XYZ_file = crystals[row]
            self.output_textBox_3.append(f"Row Number: {row}")
            self.update_XYZ(XYZ_file)

    def dspinbox_change(self, var, dspinbox_list, slider_list):
        dspinbox = self.sender()
        i = 0
        for name in dspinbox_list:
            if name == dspinbox:
                dspinbox_value = name.value()
                self.log_message(dspinbox_value, "debug")
                slider_list[i].setValue(int(dspinbox_value * 100))
            i += 1
        value_list = []
        for i in range(var):
            value = dspinbox_list[i].value()
            value_list.append(value)
        self.log_message(value_list, "debug")

    def update_xyz_slider(self, value):
        if self.sim_num != value:
            self.fname_comboBox.setCurrentIndex(value)
            self.xyz_spinBox.setValue(value)
            self.update_XYZ_info(self.openglwidget.xyz)

    # Utility function to clear a layout of all its widgets
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def insert_info(self, result):
        self.log_message("Inserting data to GUI!", log_level="debug", gui=True)
        aspect1 = result.aspect1
        aspect2 = result.aspect2
        shape_class = "Unassigned"

        if aspect1 >= 2 / 3:
            if aspect2 >= 2 / 3:
                shape_class = "Block"
            else:
                shape_class = "Needle"
        if aspect1 < 2 / 3:
            if aspect2 < 2 / 3:
                shape_class = "Lath"
            else:
                shape_class = "Plate"

        alignment = Qt.AlignRight
        self.lineEdit_sm.setText(f"{aspect1:.2f}")
        self.lineEdit_sm.setAlignment(alignment)

        self.lineEdit_ml.setText(f"{aspect2:.2f}")
        self.lineEdit_ml.setAlignment(alignment)

        self.lineEdit_shape.setText(f"{shape_class:>8s}")
        self.lineEdit_shape.setAlignment(alignment)

        self.lineEdit_sa.setText(f"{result.sa:.2f}")
        self.lineEdit_sa.setAlignment(alignment)

        self.lineEdit_vol.setText(f"{result.vol:.2f}")
        self.lineEdit_vol.setAlignment(alignment)

        self.lineEdit_savol.setText(f"{result.sa_vol:.2f}")
        self.lineEdit_savol.setAlignment(alignment)

    def init_opengl(self, xyz_file_list):
        self.xyz_file_list = [str(path) for path in xyz_file_list]
        tot_sims = "Unassigned"

        # Clear all lists
        self.colour_list = []
        self.settings_dialog.ui.colourmode_comboBox.clear()
        self.settings_dialog.ui.colour_comboBox.clear()
        self.settings_dialog.ui.pointtype_comboBox.clear()
        self.settings_dialog.ui.bgcolour_comboBox.clear()

        # self.run_xyz_movie(xyz_file_list[0])
        tot_sims = len(self.xyz_file_list)

        self.colour_list = [
            "Viridis",
            "Plasma",
            "Inferno",
            "Magma",
            "Cividis",
            "Twilight",
            "Twilight Shifted",
            "HSV",
        ]

        self.settings_dialog.ui.colourmode_comboBox.addItems(
            [
                "Atom/Molecule Type",
                "Atom/Molecule Number",
                "Layer",
                "Single Colour",
                "Site Number",
                "Particle Energy",
            ]
        )
        self.settings_dialog.ui.pointtype_comboBox.addItems(["Points", "Spheres"])
        self.settings_dialog.ui.colourmode_comboBox.setCurrentIndex(2)
        self.settings_dialog.ui.colour_comboBox.addItems(self.colour_list)
        self.settings_dialog.ui.bgcolour_comboBox.addItems(
            ["Black", "White"]
        )
        self.settings_dialog.ui.bgcolour_comboBox.setCurrentIndex(0)

        self.settings_dialog.ui.colour_comboBox.currentIndexChanged.connect(
            self.openglwidget.updateSelectedColormap
        )
        self.settings_dialog.ui.bgcolour_comboBox.currentIndexChanged.connect(
            self.openglwidget.updateBackgroundColor
        )
        self.settings_dialog.ui.colourmode_comboBox.currentIndexChanged.connect(
            self.openglwidget.updateColorType
        )

        self.fname_comboBox.addItems(self.xyz_file_list)
        self.openglwidget.pass_XYZ_list(xyz_file_list)
        self.fname_comboBox.currentIndexChanged.connect(
            self.openglwidget.get_XYZ_from_list
        )
        self.fname_comboBox.currentIndexChanged.connect(self.update_xyz_slider)
        self.saveframe_toolButton.clicked.connect(self.openglwidget.saveRenderDialog)
        self.settings_dialog.ui.point_slider.setMinimum(1)
        self.settings_dialog.ui.point_slider.setMaximum(50)
        self.settings_dialog.ui.point_slider.setValue(10)
        self.settings_dialog.ui.point_slider.valueChanged.connect(
            self.openglwidget.updatePointSize
        )

        self.xyz_spinBox.setMinimum(0)
        self.xyz_spinBox.setMaximum(tot_sims - 1)
        self.xyz_spinBox.valueChanged.connect(self.openglwidget.get_XYZ_from_list)
        self.xyz_spinBox.valueChanged.connect(self.update_xyz_slider)

    def init_crystal(self, result):
        self.movie_controls_frame.hide()
        logger.debug("INIT CRYSTAL %s", result)
        self.xyz, self.movie = result
        self.openglwidget.pass_XYZ(self.xyz)

        if self.movie:
            self.movie_controls_frame.show()
            self.frame = 0
            self.frame_list = self.movie.keys()
            logger.debug("Frames: %s", self.frame_list)
            
            self.frame_spinBox.setMinimum(0)
            self.frame_spinBox.setMaximum(len(self.frame_list))
            self.frame_slider.setMinimum(0)
            self.frame_slider.setMaximum(len(self.frame_list))
            self.frame_spinBox.valueChanged.connect(self.update_movie)
            self.frame_slider.valueChanged.connect(self.update_movie)
            self.play_button.clicked.connect(lambda: self.play_movie(self.frame_list))

        try:
            self.openglwidget.initGeometry()
        except AttributeError as e:
            logger.warning("Initialising XYZ: No Crystal Data Found! %s", e)

    def update_frame(self, frame):
        self.xyz = self.movie[frame]
        self.update_XYZ()

    def update_XYZ(self):
        self.openglwidget.pass_XYZ(self.xyz)
        try:
            self.openglwidget.initGeometry()
        except AttributeError:
            logger.warning("Updating XYZ: No Crystal Data Found!")

    def close_opengl_widget(self):
        if self.current_viewer:
            # Remove the OpenGL widget from its parent layout
            self.viewer_container_layout.removeWidget(self.current_viewer)

            # Delete the widget from memory
            self.current_viewer.deleteLater()
            self.current_viewer = None  # Reset the active viewer

    def update_statusbar(self, status):
        self.statusBar().showMessage(status, self.status_timeout)

    def thread_finished(self):
        self.log_message("THREAD COMPLETED!", "info")


def set_default_opengl_version(major, minor):
    from PySide6.QtGui import QSurfaceFormat

    format = QSurfaceFormat()
    format.setVersion(major, minor)
    format.setProfile(QSurfaceFormat.CoreProfile)
    format.setOption(QSurfaceFormat.DebugContext)
    # format.setDepthBufferSize(24)
    # format.setStencilBufferSize(8)
    QSurfaceFormat.setDefaultFormat(format)


def main():
    set_default_opengl_version(3, 3)
    # Setting taskbar icon permissions - windows
    appid = "CNM.CrystalGrower.CrystalAspects.v1.0"
    import ctypes

    if hasattr(ctypes, "windll"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    # ############# Runs the application ############## #
    # sys.argv += ['--style', 'Material.Light']
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
