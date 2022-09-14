import numpy as np
import pandas as pd
from DataProcessor.tools.shape_analysis import CrystalShape as cs


class Calculate:

    def __init__(self):
        pass

    def aspectratio_cda_eq(self):
        pass

    def aspectratio(self, vals):
        self.small, self.medium, self.long = (sorted(vals))
        
        self.aspect1 = self.small / self.medium
        self.aspect2 = self.medium / self.long

        aspect_array = np.array([[self.small,
                                self.medium,
                                self.long,
                                self.aspect1,
                                self.aspect2]])
        
        return aspect_array

    def calc_growth_rate(self, size_file_list, supersat_list):
        growth_list = []
        lengths = []
        i = 0
        for f in size_file_list:
            lt_df = pd.read_csv(f)
            x_data = lt_df['time']

            columns = lt_df.columns
            if i == 0:
                for col in columns:
                    if col.startswith(' '):
                        lengths.append(col)

            gr_list = []
            for direction in lengths:
                print(direction)
                print(f)
                y_data = np.array(lt_df[direction])
                model = np.polyfit(x_data, y_data, 1)
                gr_list.append(model[0])
                # growth_array = np.append(growth_array, gr_list)
            growth_list.append(gr_list)
            print(growth_list)
            i += 1
        growth_array = np.array(growth_list)
        gr_df = pd.DataFrame(growth_array, columns=lengths)
        gr_df.insert(0, 'Supersaturation', supersat_list)

        return gr_df