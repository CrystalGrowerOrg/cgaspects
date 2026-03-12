import logging
from collections import namedtuple
from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool, Signal
from PySide6.QtWidgets import QDialog

from ..fileio import find_data as fd
from ..fileio.find_data import apply_supersat_mode, summary_has_starting_delmu
from ..gui.dialogs.growthrate_dialog import GrowthRateAnalysisDialogue
from ..utils.data_structures import results_tuple
from . import gr_dataframes as gr
from .gui_threads import WorkerGrowthRates

logger = logging.getLogger("CA:G-Rates")


class GrowthRate:
    def __init__(self, signals):
        self.input_folder = None
        self.output_folder = None
        self.directions = None
        self.information = None
        self.xyz_files: list[Path] | None = None
        self.directions = None
        self.selected_direction = None
        self.signals = signals
        self.threadpool = None
        self.threadpool = QThreadPool()
        self.worker = None

        self.result_tuple = results_tuple

        self.progress_updated = Signal(int)
        self.circular_progress = None
        self.signals = signals

    def update_progress(self, value):
        self.signals.progress.emit(value)

    def set_folder(self, folder):
        self.input_folder = Path(folder)
        logger.info("Folder set for growth rate calculations")

    def set_information(self, information):
        self.information = information
        logger.info("Information set for growth rate calculations")

    def set_xyz_files(self, xyz_files: list[Path]):
        self.xyz_files = xyz_files

    def calculate_growth_rates(self):
        logger.debug("Called growth rate method at directory: %s", self.input_folder)
        # Check if the user selected a folder
        if self.input_folder:
            if self.information is None:
                logger.warning("Method called without information, looking for information now.")
                # Read the information from the selected folder
                self.information = fd.find_info(self.input_folder)
            logger.info("Attempting to calculate Growth Rates...")

        if not (self.input_folder and self.information):
            logger.warning(
                "Unable to proceed as Input folder and Information was not set properly."
            )
            return

        # Get the directions from the information
        self.directions = self.information.directions

        has_starting_delmu = (
            bool(self.information.summary_file)
            and summary_has_starting_delmu(self.information.summary_file)
        )
        growth_rate_dialog = GrowthRateAnalysisDialogue(
            self.directions, has_starting_delmu=has_starting_delmu
        )

        if growth_rate_dialog.exec() != QDialog.Accepted:
            logger.warning("Selecting growth directions cancelled")
            return

        self.selected_directions = growth_rate_dialog.selected_directions
        self.xaxis_mode = growth_rate_dialog.xaxis_mode
        self.supersat_mode = growth_rate_dialog.supersat_mode

        self.output_folder = fd.create_aspects_folder(self.input_folder)
        self.signals.location.emit(self.output_folder)
        # self.circular_progress = CircularProgress(calc_type="Growth Rates")
        # self.circular_progress.show()
        # self.circular_progress.raise_()
        # directions_text = "\n".join(self.selected_directions)
        # self.circular_progress.update_text(f"Calculating...\nFor Directions:\n{directions_text}")

        if not self.threadpool:
            growth_rate_df = gr.build_growthrates(
                size_file_list=self.information.size_files,
                supersat_list=self.information.supersats,
                directions=self.selected_directions,
                xaxis_mode=self.xaxis_mode,
            )
            if growth_rate_df is not None and not growth_rate_df.empty:
                if self.information.summary_file:
                    logger.info("Merging growth rates with summary file: %s", self.information.summary_file)
                    growth_rate_df = fd.summary_compare(
                        summary_csv=self.information.summary_file,
                        aspect_df=growth_rate_df,
                    )
                    growth_rate_df = apply_supersat_mode(growth_rate_df, self.supersat_mode)
            self.plot(plotting_csv=growth_rate_df)
        if self.threadpool:
            self.worker = WorkerGrowthRates(
                information=self.information,
                selected_directions=self.selected_directions,
                xaxis_mode=self.xaxis_mode,
                supersat_mode=self.supersat_mode,
            )
            
            self.worker.signals.progress.connect(self.update_progress, Qt.QueuedConnection)
            self.worker.signals.result.connect(self.plot, Qt.QueuedConnection)
            self.signals.started.emit()
            self.threadpool.start(self.worker)

    def plot(self, plotting_csv):
        # self.circular_progress.hide()
        if plotting_csv is None:
            logger.warning("No Size Files (*size.csv) found to calculate growth rates")
            self.signals.finished.emit()
        else:
            if not plotting_csv.empty:  # Properly checks if DataFrame is not empty
                growth_rate_csv = self.output_folder / "growthrates.csv"
                plotting_csv.to_csv(growth_rate_csv, index=None)
                result = self.result_tuple(
                    csv=growth_rate_csv,
                    selected=self.selected_directions,
                    folder=self.output_folder,
                )
                logger.debug("Sending plotting information to GUI: %s", result)
                self.signals.result.emit(result)
                self.signals.finished.emit()
                # if self.auto_plotting:
                #     plot = Plotting()
                #     plot.plot_growth_rates(
                #         plotting_csv, self.selected_directions, self.output_folder
                #     )
            else:
                logger.warning("The DataFrame is empty. No calculated growth rates.")
                self.signals.finished.emit()
