import numpy as np
from natsort import natsorted
import pandas as pd
from pathlib import Path
from CrystalAspects.data.find_data import Find
from CrystalAspects.data.calc_data import Calculate
from CrystalAspects.visualisation.plot_data import Plotting


class GrowthRate:
    def __init__(self):
        pass

    def creates_rates_folder(self, path):
        """This method returns a new folder to save data,
        with a selected CG simulation / Crystal Aspects folder"""

        rates_folder = Path(path) / "CrystalAspects" / "GrowthRates"
        rates_folder.mkdir(parents=True, exist_ok=True)

        return rates_folder

    def calc_growth_rate(self, size_file_list, supersat_list, directions=[]):
        """ generate the growth rate dataframe from the
        size.csv files """
        growth_list = []
        lengths = []
        i = 0
        print(size_file_list)

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


    def run_calc_growth(self, path, directions, savefolder, plotting=True):
        """Returns the final df/csv of the
        growth rates vs supersaturation"""

        find = Find()
        file_info = find.find_info(path)

        calc = Calculate()

        growth_rate_df = calc.calc_growth_rate(
            file_info.size_files, file_info.supersats, file_info.directions
        )
        growth_rate_df.to_csv(savefolder / "growthrates.csv")

        if plotting:
            plot = Plotting()
            plot.plot_growth_rates(growth_rate_df, directions, savefolder)
