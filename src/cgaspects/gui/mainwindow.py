import logging
import os
import sys
from collections import defaultdict, namedtuple
from pathlib import Path
from typing import List

import pandas as pd
from natsort import natsorted
from PySide6 import QtWidgets
from PySide6.QtCore import QObject, QSignalBlocker, QThreadPool, QTimer, Signal
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QProgressBar

from ..analysis.aspect_ratios import AspectRatio
from ..analysis.growth_rates import GrowthRate
from ..analysis.gui_threads import WorkerXYZ
from ..analysis.shape_analysis import CrystalShape
from ..fileio.find_data import find_info, locate_xyz_files
from ..fileio.xyz_file import read_XYZ
from ..fileio.logging import setup_logging
from ..fileio.opendir import open_directory
from .crystal_info import CrystalInfo
from .dialogs import CrystalInfoWidget, PlottingDialog
from .dialogs.settings import SettingsDialog
from .dialogs.about import AboutCGDialog
from .load_ui import Ui_MainWindow
from .openGL import VisualisationWidget
from .widgets import (
    SimulationVariablesWidget,
    VisualizationSettingsWidget,
)
from ..utils.data_structures import xyz_tuple

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

    started = Signal()
    finished = Signal()
    sim_id = Signal(int)
    error = Signal(tuple)
    result = Signal(object)
    location = Signal(object)
    progress = Signal(int)
    message = Signal(str)


class MainWindow(QMainWindow, Ui_MainWindow):
    status_timeout = 1000
    crystalInfoChanged = Signal(CrystalInfo)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.setupUi(self)
        self.update_statusbar("CrystalAspects v1.0")

        self.threadpool = QThreadPool()

        self.welcome_message()

        # movie timer
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.next_frame)
        self.frame = 0
        self.frame_list = []
        self.playingState = False
        self.playingLoop = True
        self.playIcon = QIcon(":/material_icons/material_icons/png/play-custom.png")
        self.pauseIcon = QIcon(":/material_icons/material_icons/png/pause-custom.png")

        self.frame_slider.valueChanged.connect(self.update_movie)
        self.frame_spinBox.valueChanged.connect(self.update_movie)
        self.playPauseButton.clicked.connect(self.play_movie)

        self.worker_signals = GUIWorkerSignals()
        self.aspectratio = AspectRatio(signals=self.worker_signals)
        self.growthrate = GrowthRate(signals=self.worker_signals)
        self.worker_signals.location.connect(self.set_output_folder)
        self.worker_signals.result.connect(self.set_results)
        self.worker_signals.started.connect(self.set_progressbar)
        self.worker_signals.finished.connect(self.clear_progressbar)
        self.worker_signals.progress.connect(self.update_progressbar)
        self.worker_signals.message.connect(self.set_message)
        self.worker_signals.sim_id.connect(self.update_sim_id)
        # Other self variables
        self.sim_num: int | None = None
        self.input_folder: Path | None = None
        self.output_folder: Path | None = None
        self.xyz_files: List[Path] = []
        self.selected_directions: list = []
        self.plotting_csv: Path | None = None
        self.summ_df = None
        self.simulation_variables_widget = None
        self.plotting_dialog = None

        self.aboutDialog = None

        self.progressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)
        self.progressBar.hide()

        self.movie_controls_frame.hide()

        self.settings_dialog = SettingsDialog(self)
        self.openglwidget = VisualisationWidget()

        self.crystalInfoWidget = CrystalInfoWidget(self)
        self.crystalInfoWidget.setEnabled(False)
        self.crystalInfo_groupBox.layout().addWidget(self.crystalInfoWidget)

        self.crystal_info = CrystalInfo()
        self.crystalInfoChanged.connect(self.crystalInfoWidget.update)
        self.gl_vLayout.addWidget(self.openglwidget)

        self.xyzFilenameListWidget.currentRowChanged.connect(self.setCurrentXYZIndex)
        self.xyz_spinBox.valueChanged.connect(self.setCurrentXYZIndex)

        self.saveframe_pushButton.clicked.connect(self.openglwidget.saveRenderDialog)

        self.visualizationSettings = VisualizationSettingsWidget(parent=self)
        self.visualizationSettings.setEnabled(enabled=True)
        self.visualizationSettings.settingsChanged.connect(
            self.handleVisualizationSettingsChange
        )
        self.visualizationTab.layout().addWidget(self.visualizationSettings)
        self.fps = self.visualizationSettings.fps()

        self.setup_button_connections()
        self.setup_menubar_connections()
        self.setShowPlottingButtons(False)

    def setup_menubar_connections(self):
        self.actionImport.triggered.connect(
            lambda: self.import_and_visualise_xyz(folder=None)
        )
        self.actionImport_CSV_for_Plotting.triggered.connect(self.browse_plot_csv)
        self.actionImportCSVClipboard.triggered.connect(
            lambda x: self.set_plotting(QtWidgets.QApplication.clipboard().text())
        )

        self.actionImport_Summary_File.triggered.connect(
            lambda: self.read_summary(summary_file=None)
        )

        self.actionInput_Directory.triggered.connect(
            lambda: (
                open_directory(path=self.input_folder)
                if self.input_folder is not None
                else None
            )
        )
        self.actionResults_Directory.triggered.connect(
            lambda: (
                open_directory(path=self.output_folder)
                if self.output_folder is not None
                else None
            )
        )
        self.actionRender.triggered.connect(self.openglwidget.saveRenderDialog)
        self.actionPlottingDialog.triggered.connect(self.replotting_called)

        self.actionAboutCGAspects.triggered.connect(self.showAboutDialog)

    def showAboutDialog(self):
        if self.aboutDialog is None:
            self.aboutDialog = AboutCGDialog(self)

        if self.aboutDialog.isVisible():
            self.aboutDialog.raise_()
            self.aboutDialog.activateWindow()
        else:
            self.aboutDialog.show()

    def setup_button_connections(self):
        self.importPlotDataPushButton.clicked.connect(self.browse_plot_csv)
        self.import_pushButton.clicked.connect(
            lambda: self.import_and_visualise_xyz(folder=None)
        )
        self.batch_lineEdit.returnPressed.connect(
            lambda: self.import_and_visualise_xyz(folder=self.batch_lineEdit.text())
        )
        self.view_results_pushButton.clicked.connect(
            lambda: open_directory(path=self.output_folder)
        )

        self.aspect_ratio_pushButton.clicked.connect(self.calculate_aspect_ratio)
        self.growth_rate_pushButton.clicked.connect(self.calculate_growth_rates)

        self.plot_lineEdit.textChanged.connect(self.set_plotting)
        self.plot_lineEdit.returnPressed.connect(self.replotting_called)
        self.plot_pushButton.clicked.connect(self.replotting_called)

    def set_progressbar(self):
        self.set_message("Started Calculations...")
        self.progressBar.setValue(0)
        self.progressBar.show()

    def clear_progressbar(self):
        self.set_message("Calculations Completed!")
        if self.progressBar is not None:
            self.progressBar.hide()

    def update_progressbar(self, value):
        if self.progressBar is not None:
            self.progressBar.setValue(value)

    def update_sim_id(self, value):
        if value is None:
            return
        if self.input_folder is not None:
            self.setCurrentXYZIndex(value=value)

    def set_message(self, msg):
        self.log_message(message=msg, log_level="info", gui=True)

    def show_settings(self):
        self.settings_dialog.show()
        self.settings_dialog.raise_()

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

    def log_message(self, message: str, log_level: str, gui: bool = False):
        message = str(message)
        log_level_method = getattr(logger, log_level.lower(), logger.debug)

        if gui or log_level in ["info", "warning"]:
            # Update the status bar with the message
            self.update_statusbar(message)

        # Log the message with given level
        log_level_method(message)

    def set_output_folder(self, value):
        self.output_folder = Path(value)
        self.actionResults_Directory.setEnabled(True)
        self.view_results_pushButton.setEnabled(True)

    def import_and_visualise_xyz(self, folder=None):
        if folder is not None and folder != "":
            folder = Path(folder)
            if not folder.is_dir():
                return

        imported = self.import_xyz(folder=folder)
        if imported:
            self.set_visualiser()

    def import_xyz(self, folder=None):
        """Import XYZ file(s) by first opening the folder
        and then opening them via an OpenGL widget"""

        # Initialize or clear the list of XYZ files
        self.xyz_files = []

        # Read the .XYZ files from the selected folder
        if folder is None:
            folder = QFileDialog.getExistingDirectory(
                None, "Select Folder that contains the Crystal Outputs (.XYZ)"
            )
        if folder == "":
            self.log_message("No folder selected", "debug")
            return False
        if self.input_folder == folder:
            self.log_message("Same path as current location!", "info")
            return False

        self.log_message("Reading Images...", "info")
        xyz_files = locate_xyz_files(folder)

        # Check for valid data, folder reinitialised as a Path object
        if (folder, xyz_files) == (None, None):
            return False

        self.xyz_files = xyz_files
        self.input_folder = folder
        self.batch_lineEdit.setText(str(self.input_folder))
        self.actionInput_Directory.setEnabled(True)
        self.log_message(f"Input path set to: {self.input_folder}", "info")
        self.log_message(f"Initial XYZ list: {xyz_files}", "debug")

        if folder:
            self.xyz_files = natsorted(xyz_files)

        return True

    def set_visualiser(self):
        self.actionImport_Summary_File.setEnabled(False)
        self.summ_df = None
        if self.simulation_variables_widget is not None:
            self.simulation_variables_widget.deleteLater()
            self.simulation_variables_widget = None

        if self.xyz_files is None:
            self.log_message(f"No XYZ files to visualise", "warning")
            return
        n_xyz = len(self.xyz_files)
        if n_xyz == 0:
            self.log_message(f"{n_xyz} XYZ files found to set to self!", "warning")
        if n_xyz > 0:
            self.init_opengl()
            result = self.get_xyz_frame_or_movie(0)
            self.init_crystal(result)

            self.update_XYZ_info(self.openglwidget.xyz)
            self.aspect_ratio_pushButton.setEnabled(True)
            self.set_batch_type()
            self.variablesTabWidget.setCurrentIndex(0)
            self.actionImport_Summary_File.setEnabled(True)

    def init_opengl(self):
        tot_sims = len(self.xyz_files)
        self.openglwidget.pass_XYZ_list([str(path) for path in self.xyz_files])
        self.sim_num = 0
        self.openglwidget.get_XYZ_from_list(0)
        self.xyzFilenameListWidget.clear()
        self.xyzFilenameListWidget.addItems([x.name for x in self.xyz_files])

        self.xyz_spinBox.setMinimum(0)
        self.xyz_spinBox.setMaximum(tot_sims - 1)

        self.xyzFilenameListWidget.setEnabled(True)
        self.xyz_id_label.setEnabled(True)
        self.xyz_spinBox.setEnabled(True)

        self.log_message(f"{len(self.xyz_files)} XYZ files set to visualiser!", "info")

    def init_crystal(self, result):
        self.movie_controls_frame.hide()
        logger.debug("Initializing crystal: %s", result)
        self.xyz, self.movie = result
        self.openglwidget.pass_XYZ(self.xyz)
        self.openglwidget.movie = self.movie

        if self.movie:
            self.playingState = False
            self.frame_timer.stop()
            self.movie_controls_frame.show()
            self.frame_list = self.movie.keys()
            self.frame = 0
            logger.debug("Frames: %s", self.frame_list)

            num_frames = len(self.frame_list)

            self.frame_slider.setMinimum(0)
            self.frame_slider.setMaximum(num_frames - 1)

            self.frame_spinBox.setMinimum(0)
            self.frame_spinBox.setMaximum(num_frames - 1)
            self.frameMaxLabel.setText(f"{num_frames - 1}")

        try:
            self.openglwidget.initGeometry()
            self.actionRender.setEnabled(True)
            self.saveframe_pushButton.setEnabled(True)
        except AttributeError as e:
            logger.warning("Initialising XYZ: No Crystal Data Found! %s", e)

    def get_xyz_frame_or_movie(self, index):
        folder = self.input_folder
        if 0 <= index < len(self.xyz_files):
            file_name = self.xyz_files[index]
            full_file_path = os.path.join(folder, file_name)
            results = xyz_tuple

            self.set_progressbar()

            def prog(val, tot):
                self.update_progressbar(100.0 * val / tot)

            xyz, xyz_movie = read_XYZ(full_file_path, progress_callback=prog)
            self.clear_progressbar()

            result = results(xyz=xyz, xyz_movie=xyz_movie)

            return result

    def update_XYZ_info(self, xyz):
        if xyz is None:
            return
        worker_xyz = WorkerXYZ(xyz)
        worker_xyz.signals.result.connect(self.insert_info)
        worker_xyz.signals.message.connect(self.update_statusbar)
        self.threadpool.start(worker_xyz)

    def update_movie(self, frame):
        if frame != self.frame:
            self.update_frame(frame)
            # block to prevent double updates
            with QSignalBlocker(self.frame_slider):
                self.frame_slider.setValue(frame)
            with QSignalBlocker(self.xyz_spinBox):
                self.frame_spinBox.setValue(frame)

    def next_frame(self):
        num_frames = len(self.frame_list)

        if self.frame < num_frames:
            self.update_frame(self.frame)
            self.frame_slider.setValue(self.frame)
            self.frame_spinBox.setValue(self.frame)
            self.frame += 1
            if self.playingLoop and self.frame >= num_frames:
                self.frame = 0
        else:
            self.frame = 0
            self.frame_timer.stop()
            self.frame_slider.setValue(self.frame)
            self.frame_spinBox.setValue(self.frame)

    def play_movie(self):
        if not self.frame_list:
            return

        if self.playingState and self.fps == 0.0:
            # pause playing
            self.playPauseButton.setIcon(self.playIcon)
            self.frame_timer.stop()
            self.playingState = False
        else:
            # play movie
            self.playPauseButton.setIcon(self.pauseIcon)
            # make sure we don't play from after the end
            if self.frame >= len(self.frame_list):
                self.frame = 0

            self.frame_timer.start(1000 // self.fps)
            self.playingState = True

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
                    "Folder selection was canceled or no folder was selected.",
                    "warning",
                )

        # Note: Bare Exception
        except Exception as e:
            self.log_message(f"An error occurred: {e}", "error")

    def set_batch_type(self):
        folder = self.input_folder
        # Initially disable buttons that depend on the data
        self.growth_rate_pushButton.setEnabled(False)

        if not Path(folder).is_dir():
            QMessageBox.warning(
                None, "Directory Error", f"{folder} is not a valid directory."
            )
            return

        self.input_folder = folder
        information = find_info(folder)

        # Enable buttons and set data based on available information
        if information.size_files and information.directions:
            self.growth_rate_pushButton.setEnabled(True)
            self.growthrate.set_folder(folder=folder)
            self.growthrate.set_information(information=information)
            self.growthrate.set_xyz_files(xyz_files=self.xyz_files)
        else:
            if not information.size_files:
                logger.warning("No size files were found in the directory!")

        # Set Aspect Ratio information
        self.aspectratio.set_folder(folder=folder)
        self.aspectratio.set_information(information=information)
        self.aspectratio.set_xyz_files(xyz_files=self.xyz_files)

        if not information.directions:
            QMessageBox.warning(
                None,
                "Data Incomplete",
                "No crystallographic direction data found in the simulation parameters output.\n"
                "Please make sure this data is available if Crystal Directional Analysis (CDA) is required.",
            )

        if information.summary_file:
            self.read_summary(summary_file=information.summary_file)
        else:
            QMessageBox.warning(None, "Data Incomplete", "Summary file not found.")

        self.input_folder = Path(folder)

    def calculate_aspect_ratio(self):
        self.aspectratio.calculate_aspect_ratio()

    def calculate_growth_rates(self):
        self.growthrate.calculate_growth_rates()

    def setShowPlottingButtons(self, state=True):
        self.actionPlottingDialog.setEnabled(state)
        self.importPlotDataPushButton.setVisible(not state)
        self.plot_lineEdit.setVisible(state)
        self.plot_pushButton.setVisible(state)

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
                    "File selection was canceled or no file was selected.", "debug"
                )

        # Note: Bare Exception
        except Exception as e:
            self.log_message(f"An error occurred: {e}", "error")

    def set_plotting(self, value):
        with QSignalBlocker(self.plot_lineEdit):
            self.plot_lineEdit.setText(value)

        valid_file = Path(value).is_file()
        self.setShowPlottingButtons(valid_file)
        if valid_file:
            self.plotting_csv = Path(value)
            self.plot_pushButton.setEnabled(True)
            self.log_message(f"Plotting CSV set to {self.plotting_csv}", "info")
        else:
            self.plot_pushButton.setEnabled(False)
            self.plotting_csv = None
            self.log_message("Plotting CSV set to None", "debug")

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

            if self.plotting_dialog is None:
                self.plotting_dialog = PlottingDialog(
                    csv=self.plotting_csv, signals=self.worker_signals, parent=self
                )
                self.plotting_dialog.connect
            else:
                self.plotting_dialog.setCSV(self.plotting_csv)
                self.plotting_dialog.trigger_plot()

            self.plotting_dialog.show()

    # Read Summary
    def read_summary(self, summary_file=None):
        if not self.xyz_files:
            self.log_message(
                "XYZ files needs to be loaded first to use summary file information",
                "warning",
            )
            return

        self.log_message("Reading Summary file...", "info")
        if not summary_file:
            summary_file = QFileDialog.getOpenFileName(None, "Read Summary File")
            summary_file = Path(summary_file[0])

        if not summary_file:
            self.log_message("Summary file not set!", "warning")
            return

        # Select summary file and read in as a Dataframe
        self.log_message(f"Summary File Found at: {summary_file}", "debug")
        self.summ_df = pd.read_csv(summary_file)
        if list(self.summ_df.columns)[-1].startswith("Unnamed"):
            self.summ_df = self.summ_df.iloc[:, 1:-1]
        else:
            self.summ_df = self.summ_df.iloc[:, 1:]
        self.log_message(
            f"Summary data succesfully read! [SHAPE {self.summ_df.shape}]", "info"
        )

        column_names = list(self.summ_df)
        self.log_message(f"Summary Column Name: {column_names}", "debug")
        # Create dictionary to store the change in variables (tile/interaction energies)
        var_dict = defaultdict(list)

        # Records the variable values from summary file
        for column in column_names:
            for index, row in self.summ_df.iterrows():
                if row[str(column)] not in var_dict[column]:
                    var_dict[column].append(row[str(column)])

        layout = self.simulationVariablesWidget.layout()

        widget = SimulationVariablesWidget(var_dict, parent=self)

        if self.simulation_variables_widget is not None:
            layout.replaceWidget(self.simulation_variables_widget, widget)
            self.simulation_variables_widget.deleteLater()
            self.simulation_variables_widget = widget

        else:
            self.simulation_variables_widget = widget
            layout.addWidget(self.simulation_variables_widget)

        self.simulation_variables_widget.variableCombinationChanged.connect(
            self.summary_change
        )

        self.statusBar().showMessage("Complete: Summary file read in!")

    def summary_change(self):
        values = self.simulation_variables_widget.currentValues()
        self.log_message(f"Looking for: {values}", log_level="debug")

        mask = (self.summ_df == values).all(axis=1)
        filtered_df = self.summ_df[mask]
        if filtered_df.empty:
            return

        if len(filtered_df.index) > 1:
            self.log_message(
                "Set of values have selected more than one row/simulation", "warning"
            )
            return

        # self.update_variables(values=values)

        selected_index = filtered_df.index[0]
        self.setCurrentXYZIndex(value=selected_index)

    def update_variables(self, values):
        if self.simulation_variables_widget is not None:
            self.simulation_variables_widget.setValues(values)
        else:
            logger.error("Simulation variables widget is None")

    def setCurrentXYZIndex(self, value):
        self.sim_num = value
        self.openglwidget.get_XYZ_from_list(value=value)
        self.movie = self.openglwidget.movie
        self.movie_controls_frame.hide()
        if self.movie:
            self.movie_controls_frame.show()

        # block to prevent double updates
        with QSignalBlocker(self.xyzFilenameListWidget):
            self.xyzFilenameListWidget.setCurrentRow(value)
        with QSignalBlocker(self.xyz_spinBox):
            self.xyz_spinBox.setValue(value)

        self.update_XYZ_info(self.openglwidget.xyz)

        self.updateVisualizationSettings()

        if self.summ_df is not None:
            var_values = self.summ_df.iloc[value, :].values
            self.update_variables(values=var_values)

    def updateVisualizationSettings(self):
        pass

    def handleVisualizationSettingsChange(self):
        self.openglwidget.updateSettings(**self.visualizationSettings.settings())
        self.fps = self.visualizationSettings.fps()

    # Utility function to clear a layout of all its widgets
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def insert_info(self, result):
        self.log_message("Inserting data to GUI!", log_level="debug", gui=True)
        self.crystal_info.aspectRatio1 = result.aspect1
        self.crystal_info.aspectRatio2 = result.aspect2
        self.crystal_info.shapeClass = result.shape
        self.crystal_info.surfaceAreaVolumeRatio = result.sa_vol
        self.crystal_info.surfaceArea = result.sa
        self.crystal_info.volume = result.vol

        self.crystalInfoChanged.emit(self.crystal_info)

    def update_frame(self, frame):
        self.frame = frame
        self.xyz = self.movie[frame]
        self.openglwidget.pass_XYZ(self.xyz)
        self.update_XYZ_info(self.openglwidget.xyz)
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
            else:
                pass
        else:
            super().keyPressEvent(event)


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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-native-menubar",
        default=False,
        action="store_true",
        help="Don't use native menubar",
    )
    parser.add_argument(
        "--no-dpi-scaling",
        default=False,
        action="store_true",
        help="Disable High DPI scaling",
    )
    args = parser.parse_args()

    set_default_opengl_version(3, 3)
    # Setting taskbar icon permissions - windows
    appid = "CrystalGrower.CGAspects.0.8.0"
    import ctypes

    if hasattr(ctypes, "windll"):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    # ############# Runs the application ############## #
    # sys.argv += ['--style', 'Material.Light']
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, args.no_dpi_scaling)

    QtWidgets.QApplication.setAttribute(
        Qt.AA_DontUseNativeMenuBar, args.no_native_menubar
    )

    QtWidgets.QApplication.setApplicationName("CGAspects")
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
