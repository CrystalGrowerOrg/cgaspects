import numpy as np
import pandas as pd

class GrowthRate:
    def __init__(self):
        pass

    def calc_growth_rate(self, size_file_list, supersat_list, directions=[]):
        """ generate the growth rate dataframe from the
        size.csv files """
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

