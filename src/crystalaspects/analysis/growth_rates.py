import numpy as np
import pandas as pd

from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox


from crystalaspects.fileio.find_data import *
from crystalaspects.gui.growthrate_dialog import GrowthRateAnalysisDialogue
from crystalaspects.visualisation.plot_data import Plotting
from crystalaspects.visualisation.replotting import PlottingDialogue


class GrowthRate:
    def __init__(self):
        self.output_folder = None

    def calculate_growth_rates(self):
        """Activate calculate growth rates from the crystalaspects
        menubar after growth rates has been selected"""
        # Prompt the user to select the folder
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "./",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        # Check if the user selected a folder
        if folder:
            # Perform calculations using the selected folder
            QMessageBox.information(
                self, "Result", f"Growth rates calculated for the folder: {folder}"
            )

            # Read the information from the selected folder
            information = find_info(folder)

            # Get the directions from the information
            checked_directions = information.directions

            growth_rate_dialog = GrowthRateAnalysisDialogue(checked_directions)
            if growth_rate_dialog.exec() == QDialog.Accepted:
                selected_directions = growth_rate_dialog.selected_directions
                auto_plotting = growth_rate_dialog.plotting_checkbox.isChecked()

                save_folder = create_aspects_folder(folder)
                self.output_folder = save_folder
                size_files = information.size_files
                supersats = information.supersats
                directions = selected_directions

                growth_rate_df = self.calc_growth_rate(
                    size_file_list=size_files,
                    supersat_list=supersats,
                    directions=directions,
                )
                print(growth_rate_df)
                growth_rate_csv = f"{save_folder}/GrowthRates.csv"
                growth_rate_df.to_csv(growth_rate_csv, index=None)
                PlottingDialogues = PlottingDialogue(self)
                PlottingDialogues.plotting_info(csv=growth_rate_csv)
                PlottingDialogues.show()
                if auto_plotting:
                    plot = Plotting()
                    plot.plot_growth_rates(growth_rate_df, directions, save_folder)

    def calc_growth_rate(self, size_file_list, supersat_list, directions=[]):
        """generate the growth rate dataframe from the
        size.csv files"""
        growth_list = []
        lengths = []
        i = 0

        for f in size_file_list:
            lt_df = pd.read_csv(f)
            x_data = lt_df["time"]

            if directions:
                lengths = directions
            if directions is False:
                columns = lt_df.columns
                if i == 0:
                    for col in columns:
                        if col.startswith(" ") or col.startwith("-1"):
                            print(col)
                            lengths.append(col)

            gr_list = []
            for direction in lengths:
                y_data = np.array(lt_df[direction])
                model = np.polyfit(x_data, y_data, 1)
                gr_list.append(model[0])
                # growth_array = np.append(growth_array, gr_list)
            growth_list.append(gr_list)
            i += 1
        growth_array = np.array(growth_list)
        gr_df = pd.DataFrame(growth_array, columns=lengths)
        gr_df.insert(0, "Supersaturation", supersat_list)

        return gr_df
