import logging
from pathlib import Path
from collections import namedtuple

from PySide6.QtWidgets import QDialog, QWidget
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool

import crystalaspects.fileio.find_data  as fd
import crystalaspects.analysis.ar_dataframes as ar
from crystalaspects.gui.aspectratio_dialog import AnalysisOptionsDialog
from crystalaspects.visualisation.plot_data import Plotting
from crystalaspects.visualisation.plot_dialog import PlottingDialog
from crystalaspects.gui.progress_dialog import CircularProgress
from crystalaspects.analysis.gui_threads import WorkerAspectRatios

logger = logging.getLogger("CA:A-Ratios")

class WorkerSignals(QObject):
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
    progress = Signal(int)
    message = Signal(str)


class AspectRatio(QWidget):
    def __init__(self):
        self.input_folder = None
        self.output_folder = None
        self.directions = None
        self.information = None
        self.directions = None
        self.selected_direction = None
        self.options: namedtuple | None = None
        self.threadpool = None
        self.threadpool = QThreadPool()

        self.progress_updated = Signal(int)
        self.circular_progress = None
        self.signals = WorkerSignals()
        self.signals.progress.connect(self.update_progress)
    
    def update_progress(self, value):
        self.circular_progress.set_value(value)

    def set_folder(self, folder):
        self.input_folder = Path(folder)
        logger.info("Folder set for aspect ratio calculations")
    
    def set_information(self, information):
        self.information = information
        logger.info("Information set for aspect ratio calculations")

    def calculate_aspect_ratio(self):
        logger.debug(
            "Called aspect ratio method at directory: %s",
            self.input_folder        
            )
        # Check if the user selected a folder
        if self.input_folder:
            if self.information is None:
                logger.warning("Method called without information, looking for information now.")
                # Read the information from the selected folder
                self.information = fd.find_info(self.input_folder)
            logger.info("Attempting to calculate Aspect Ratios...")

            """Future Note: The follwing renders the 
            dataprocessor unable to process just XYZ files
            in the envent no *simulation_parameters.txt files are not present"""

        if not self.input_folder and self.information:
            logger.warning("Input folder and Information not set properly")
            return

        # Get the directions from the information
        self.directions = self.information.directions
        logger.debug("All Directions: %s", self.directions)

        # Create the analysis options dialog
        dialog = AnalysisOptionsDialog(self.directions)

        if dialog.exec() != QDialog.Accepted:
            logger.warning("Selecting aspect ratio options cancelled")
            return
        
        # if dialog.exec() == QDialog.Accepted:
        # Retrieve the selected options
        self.options = dialog.get_options()
        logger.info("Options:: AR: %s  CDA: %s  Checked: %s   Selected: %s   Auto Plot: %s",
            self.options.selected_ar,
            self.options.selected_cda,
            self.options.checked_directions,
            self.options.selected_directions,
            self.options.plotting
        )
        self.circular_progress = CircularProgress(calc_type="Aspect Ratio")
        self.circular_progress.show()
        self.circular_progress.raise_()
        # Display the information in a QMessageBox
        self.circular_progress.update_options(self.options)

        
        if self.threadpool:
            worker = WorkerAspectRatios(
                information=self.information,
                options=self.options,
                input_folder=self.input_folder,
                output_folder=self.output_folder
            )
            worker.signals.progress.connect(self.update_progress)
            worker.signals.result.connect(self.plot)
            self.threadpool.start(worker)
        
        else:
            logger.warning("Running Calculation on the same (GUI) thread!")
            self.run_on_same_thread()
            self.plot(plotting_csv=self.plotting_csv)        
    
    def plot(self, plotting_csv):
        self.circular_progress.hide()
        if self.options.plotting:
            self.perform_plotting(
                csv_file=plotting_csv,
                folderpath=self.output_folder,
                selected_directions=self.options.selected_directions
            )

        PlottingDialogs = PlottingDialog(self)
        PlottingDialogs.plotting_info(csv=plotting_csv)
        PlottingDialogs.show()
    
    def perform_plotting(self, csv_file, folderpath, selected_directions=None):
        plotting = Plotting()
        # Handle XYZ plotting
        if self.options.selected_ar:
            plotting.plot_pca(csv=csv_file, folderpath=folderpath)
            plotting.plot_oba(csv=csv_file, folderpath=folderpath)
            plotting.plot_sa_vol(csv=csv_file, folderpath=folderpath)

        # Handle CDA plotting
        if self.options.selected_cda:
            plotting.plot_cda_extended(csv=csv_file, folderpath=folderpath, selected=selected_directions)
            plotting.plot_cda(csv=csv_file, folderpath=folderpath)

        # Handle combined CDA and XYZ plotting
        if self.options.selected_ar and self.options.selected_cda:
            plotting.plot_cda_pca(csv=csv_file, folderpath=folderpath)
            plotting.plot_cda_oba(csv=csv_file, folderpath=folderpath)
    
    def run_on_same_thread(self):

        self.output_folder = fd.create_aspects_folder(self.input_folder)

        summary_file = self.information.summary_file
        folders = self.information.folders

        if self.options.selected_ar:
            xyz_df = ar.collect_all(folder=self.input_folder)
            xyz_combine = xyz_df
            if summary_file:
                xyz_df = fd.summary_compare(
                    summary_csv=summary_file, aspect_df=xyz_df
                )
            xyz_df_final_csv = self.output_folder / "aspectratio.csv"
            xyz_df.to_csv(xyz_df_final_csv, index=None)
            ar.get_xyz_shape_percentage(
                df=xyz_df, savefolder=self.output_folder
            )
            self.plotting_csv = xyz_df_final_csv

        if self.options.selected_cda:
            cda_df = ar.build_cda(
                folderpath=self.input_folder,
                folders=folders,
                directions= self.options.checked_directions,
                selected= self.options.selected_directions,
                savefolder=self.output_folder,
            )
            zn_df = ar.build_ratio_equations(
                directions= self.options.selected_directions,
                ar_df=cda_df,
                filepath=self.output_folder,
            )
            if summary_file:
                zn_df = fd.summary_compare(
                    summary_csv=summary_file, aspect_df=zn_df
                )
            zn_df_final_csv = self.output_folder / "cda.csv"
            zn_df.to_csv(zn_df_final_csv, index=None)
            self.plotting_csv = zn_df_final_csv
            
            if self.options.selected_ar and self.options.selected_cda:
                combined_df = fd.combine_xyz_cda(CDA_df=zn_df, XYZ_df=xyz_combine)
                final_cda_xyz_csv = self.output_folder / "crystalaspects.csv"
                combined_df.to_csv(final_cda_xyz_csv, index=None)
                ar.get_cda_shape_percentage(
                    df=combined_df, savefolder=self.output_folder
                )
                self.plotting_csv = final_cda_xyz_csv

