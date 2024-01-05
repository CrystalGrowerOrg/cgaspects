import numpy as np
import pandas as pd
from pathlib import Path
import logging

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox


import crystalaspects.fileio.find_data as fd
import crystalaspects.analysis.gr_dataframes as gr
from crystalaspects.gui.growthrate_dialog import GrowthRateAnalysisDialogue
from crystalaspects.visualisation.plot_data import Plotting
from crystalaspects.visualisation.plot_dialog import PlottingDialog

logger = logging.getLogger("CA:G-Rates")


class GrowthRate:
    def __init__(self):
        self.input_folder = None
        self.output_folder = None
        self.directions = None
        self.information = None
        self.directions = None
        self.selected_direction = None

    def set_folder(self, folder):
        self.input_folder = Path(folder)
        logger.info("Folder set for growth rate calculations")
    
    def set_information(self, information):
        self.information = information
        logger.info("Information set for growth rate calculations")

    def calculate_growth_rates(self):
        logger.debug(
            "Called growth rate method at directory: %s",
            self.input_folder        
            )
        # Check if the user selected a folder
        if self.input_folder:
            if self.information is None:
                logger.warning("Method called without information, looking for information now.")
                # Read the information from the selected folder
                self.information = fd.find_info(self.input_folder)
            logger.info("Attempting to calculate Growth Rates...")

        if not (self.input_folder and self.information):
            logger.warning("Unable to proceed as Input folder and Information was not set properly.")
            return

        # Get the directions from the information
        self.directions = self.information.directions

        growth_rate_dialog = GrowthRateAnalysisDialogue(self.directions)

        if growth_rate_dialog.exec() != QDialog.Accepted:
            logger.warning("Selecting growth directions cancelled")
            return
        
        # if growth_rate_dialog.exec() == QDialog.Accepted:
        selected_directions = growth_rate_dialog.selected_directions
        auto_plotting = growth_rate_dialog.plotting_checkbox.isChecked()

        self.output_folder = fd.create_aspects_folder(self.input_folder)

        size_files = self.information.size_files
        supersats = self.information.supersats

        growth_rate_df = gr.build_growthrates(
            size_file_list=size_files,
            supersat_list=supersats,
            directions=selected_directions,
        )

        if growth_rate_df is None:
            logger.warning("No Size Files (*size.csv) found to calculate growth rates")
        else:
            if not growth_rate_df.empty:  # Properly checks if DataFrame is not empty
                logger.debug("Growth Rates Dataframe:\n%s", growth_rate_df)
                growth_rate_csv = self.output_folder / "GrowthRates.csv"
                growth_rate_df.to_csv(growth_rate_csv, index=None)
                PlottingDialogs = PlottingDialog(self)
                PlottingDialogs.plotting_info(csv=growth_rate_csv)
                PlottingDialogs.show()
                if auto_plotting:
                    plot = Plotting()
                    plot.plot_growth_rates(growth_rate_df, selected_directions, self.output_folder)
            else:
                logger.warning("The DataFrame is empty. No calculated growth rates.")
