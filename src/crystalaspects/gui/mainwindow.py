import logging
import os
import sys
from collections import namedtuple
from pathlib import Path
from typing import List
from natsort import natsorted
from collections import defaultdict
import pandas as pd
from PySide6 import QtWidgets
from PySide6.QtCore import (
    QObject,
    QThreadPool,
    Signal,
)
from PySide6 import QtGui
from PySide6 import QtCore

from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSlider,
    QProgressBar,
)

from qt_material import apply_stylesheet

from crystalaspects.analysis.aspect_ratios import AspectRatio
from crystalaspects.analysis.growth_rates import GrowthRate
from crystalaspects.analysis.gui_threads import WorkerXYZ
from crystalaspects.analysis.shape_analysis import CrystalShape
from crystalaspects.fileio.logging import setup_logging
from crystalaspects.fileio.opendir import open_directory
from crystalaspects.fileio.find_data import read_crystals, find_info
from crystalaspects.gui.dialogs.settings import SettingsDialog
from crystalaspects.gui.openGL import VisualisationWidget

# Project Module imports
from crystalaspects.gui.load_ui import Ui_MainWindow
from crystalaspects.gui.dialogs.plot_dialog import PlottingDialog
from crystalaspects.widgets import SimulationVariablesWidget

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # self.apply_style(theme_main="dark", theme_colour="teal")

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

        self.progressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)
        self.progressBar.hide()

        self.simulation_variables_widget = None

        self.movie_controls_frame.hide()

        self.settings_dialog = SettingsDialog(self)
        self.openglwidget = VisualisationWidget()
        self.gl_vLayout.addWidget(self.openglwidget)
        self.settings_pushButton.clicked.connect(self.show_settings)
        self.xyz_fname_comboBox.currentIndexChanged.connect(self.update_xyz)
        self.xyz_spinBox.valueChanged.connect(self.update_xyz)

        self.saveframe_pushButton.clicked.connect(self.openglwidget.saveRenderDialog)

        self.settings_dialog.ui.colour_comboBox.currentIndexChanged.connect(
            self.openglwidget.updateSelectedColormap
        )
        self.settings_dialog.ui.bgcolour_comboBox.currentIndexChanged.connect(
            self.openglwidget.updateBackgroundColor
        )
        self.settings_dialog.ui.colourmode_comboBox.currentIndexChanged.connect(
            self.openglwidget.updateColorType
        )
        self.settings_dialog.ui.point_slider.valueChanged.connect(
            self.openglwidget.updatePointSize
        )
        # self.settings_dialog.ui.projection_comboBox.currentIndexChanged.connect(
        #     self.openglwidget.updateProjectionType
        # )

    def setup_menubar(self):
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create two menus
        file_menu = QMenu("File", self)
        calculations_menu = QMenu("Calculations", self)
        plotting_menu = QMenu("Plotting", self)

        # Add menus to the menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(calculations_menu)

        # Create actions for the File menu
        import_action = QAction("Import", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)

        # Add actions to the File menu
        file_menu.addAction(import_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Connect actions from the File menu
        import_action.triggered.connect(
            lambda: self.import_and_visualise_xyz(folder=None)
        )

        # Create actions to the crystalaspects menu
        aspect_ratio_action = QAction("Aspect Ratio", self)
        growth_rate_action = QAction("Growth Rates", self)
        plotting_action = QAction("Plot", self)

        # Add actions and Submenu to crystalaspects menu
        calculations_menu.addAction(aspect_ratio_action)
        calculations_menu.addAction(growth_rate_action)

        plotting_menu.addAction(plotting_action)

        # Connect the crystalaspects actions
        aspect_ratio_action.triggered.connect(self.calculate_aspect_ratio)
        growth_rate_action.triggered.connect(self.calculate_growth_rates)
        plotting_action.triggered.connect(self.replotting_called)
        exit_action.triggered.connect(self.close_application)

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

        self.simulationVariablesSelectButton.clicked.connect(
            lambda: self.read_summary(summary_file=None)
        )

        self.plot_browse_pushButton.clicked.connect(self.browse_plot_csv)
        self.plot_lineEdit.textChanged.connect(self.set_plotting)
        self.plot_lineEdit.returnPressed.connect(self.replotting_called)
        self.plot_pushButton.clicked.connect(self.replotting_called)

        self.play_button.clicked.connect(self.play_movie)

    def setup_keyboard_shortcuts(self):
        # Import XYZ file with Ctrl+I
        import_xyz_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        import_xyz_shortcut.activated.connect(
            lambda: self.import_and_visualise_xyz(folder=None)
        )

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
        if self.input_folder is not None:
            self.update_xyz(value=value)

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
        self.view_results_pushButton.setEnabled(True)

    def import_and_visualise_xyz(self, folder=None):
        if folder != None and folder != "":
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
        if self.input_folder == folder:
            self.log_message("Same path as current location!", "info")
            return False

        self.log_message("Reading Images...", "info")
        folder, xyz_files = read_crystals(folder)

        # Check for valid data
        if (folder, xyz_files) == (None, None):
            return False

        self.xyz_files = xyz_files
        self.input_folder = folder
        self.batch_lineEdit.setText(str(self.input_folder))

        self.log_message(f"Initial XYZ list: {xyz_files}", "debug")

        if folder:
            self.xyz_files = natsorted(xyz_files)

        return True

    def set_visualiser(self):
        n_xyz = len(self.xyz_files)
        if n_xyz == 0:
            self.log_message(f"{n_xyz} XYZ files found to set to self!", "warning")
        if n_xyz > 0:
            self.init_opengl(self.xyz_files)
            result = self.get_xyz_frame_or_movie(0)
            self.init_crystal(result)

            self.simulationVariablesSelectButton.setEnabled(True)
            self.log_message(
                f"{len(self.xyz_files)} XYZ files set to visualiser!", "info"
            )
            self.update_XYZ_info(self.openglwidget.xyz)
            self.set_batch_type()

    def init_opengl(self, xyz_file_list):
        # XYZ Files
        self.xyz_file_list = [str(path) for path in xyz_file_list]
        tot_sims = len(self.xyz_file_list)
        self.openglwidget.pass_XYZ_list(xyz_file_list)
        self.sim_num = 0
        self.openglwidget.get_XYZ_from_list(0)
        self.xyz_fname_comboBox.addItems(self.xyz_file_list)

        self.xyz_spinBox.setMinimum(0)
        self.xyz_spinBox.setMaximum(tot_sims - 1)

        self.xyz_fname_comboBox.setEnabled(True)
        self.xyz_id_label.setEnabled(True)
        self.xyz_spinBox.setEnabled(True)
        self.saveframe_pushButton.setEnabled(True)

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

    def get_xyz_frame_or_movie(self, index):
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
                    "Folder selection was canceled or no folder was selected.",
                    "warning",
                )

        # Note: Bare Exception
        except Exception as e:
            self.log_message(f"An error occurred: {e}", "error")

    def set_batch_type(self):
        folder = self.input_folder
        self.aspect_ratio_pushButton.setEnabled(False)
        self.growth_rate_pushButton.setEnabled(False)
        self.summ_df = None
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
                if information.summary_file:
                    self.read_summary(summary_file=information.summary_file)
                self.input_folder = Path(folder)

            else:
                raise NotADirectoryError(f"{folder} is not a valid directory.")

        except (FileNotFoundError, NotADirectoryError) as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                f"{e}\nPlease make sure the folder you have selected "
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

            PlottingDialogs = PlottingDialog(csv=self.plotting_csv)
            PlottingDialogs.show()

    # Read Summary
    def read_summary(self, summary_file=None):
        if not self.xyz_file_list:
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

        layout = self.xyz_variables_tab.layout()
        if self.simulation_variables_widget is not None:
            layout.removeItem(self.simulation_variables_widget)

        layout.removeItem(self.simulationVariablesSpacer)

        self.simulation_variables_widget = SimulationVariablesWidget(
            var_dict, parent=self
        )

        self.simulation_variables_widget.variableCombinationChanged.connect(
            self.summary_change
        )

        layout.addWidget(self.simulation_variables_widget)

        layout.addItem(self.simulationVariablesSpacer)
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
        self.update_xyz(value=selected_index)

    def update_variables(self, values):
        if self.simulation_variables_widget is not None:
            self.simulation_variables_widget.setValues(values)

    def update_xyz(self, value):
        if self.sim_num != value:
            self.openglwidget.get_XYZ_from_list(value=value)
            self.xyz_fname_comboBox.setCurrentIndex(value)
            self.xyz_spinBox.setValue(value)
            self.update_XYZ_info(self.openglwidget.xyz)

            if self.summ_df is not None:
                var_values = self.summ_df.iloc[value, :].values
                self.update_variables(values=var_values)

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

        # Update or create new field widgets
        self.aspect1_label.setText(f"{aspect1:>10.2f}")
        self.aspect2_label.setText(f"{aspect2:>10.2f}")
        self.shape_label.setText(f"{shape_class:>10s}")
        self.savol_label.setText(f"{result.sa_vol:>10.2f}")
        self.sa_label.setText(f"{result.sa:>10.2f}")
        self.vol_label.setText(f"{result.vol:>10.2f}")

    def update_frame(self, frame):
        self.xyz = self.movie[frame]
        self.update_XYZ()
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
    app.setStyle("Fusion")
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
