import os
import numpy as np
from natsort import natsorted
import pandas as pd

class Run:

    def __init__(self):
        self.method = 0

    def creates_rates_folder(self, path):
        rates_folder = Path(path) / 'CrystalAspects' + '/GrowthRates/'
        rates_folder.mkdir(parents=True, exist_ok=True)

        return rates_folder

    def find_size(self, folders, path):
        files = os.listdir(path)
        contents = natsorted(os.listdir(path))
        folders = []
        for item in contents:
            path = path + '/' + item
            if os.path.isdir(path):
                if item.endswith('XYZ_files') or item.endswith('CrystalAspects') or item.endswith('CrystalMaps'):
                    continue
                else:
                    folders.append(item)
        file = []
        for i in range(len(folders)):
            path = path + '/' + folders[i]
            files = os.listdir(path)
            for f in files:
                if f.startswith("._"):
                    continue
                if f.endswith('size.csv'):
                    file.append(f)
                    file_path = folderpath + '/' + f
                    # print(file_path)
        return folders, file

    def find_supersat(self, path, folders):
        files = os.listdir(path)
        supersaturation = []
        for i in range(len(folders)):
            path = path + '/' + folders[i]
            files = os.listdir(path)
            for f in files:
                if f.startswith("._"):
                    continue
                if f.endswith('simulation_parameters.txt'):
                    filepath = folderpath + '/' + folders[i] + '/' + f
                    # print(filepath)
                    with open(filepath, 'r') as sim_file:
                        lines = sim_file.readlines()

                    for line in lines:
                        if line.startswith('Starting delta mu value (kcal/mol):'):
                            supersat = float(line.split()[-1])
                            supersaturation.append(supersat)

        return supersaturation

    def find_lengths(self, folders, path, file):
        lt_df = pd.read_csv(path + '/' + folders[0] + '/' + file[0])
        columns = lt_df.columns
        time = []
        ratios = []
        lengths = []
        for col in columns:
            if col.startswith('time'):
                time.append(col)
            if col.startswith(' '):
                lengths.append(col)
        return lengths

    def calc_growth_rate(self, path, folders, file, lengths, supersaturation):
        growth_list = []
        growth_array = np.array(lengths)
        i = 0
        for f in folders:
            lt_df = pd.read_csv(path + '/' + f + '/' + file[i])
            x_data = lt_df['time']
            gr_list = []
            for direction in lengths:
                print(direction)
                print(path + '/' + f + '/' + file[i])
                y_data = np.array(lt_df[direction])
                model = np.polyfit(x_data, y_data, 1)
                gr_list.append(model[0])
                # growth_array = np.append(growth_array, gr_list)
            growth_list.append(gr_list)
            # print(growth_list)
            i += 1
        growth_array = np.append(growth_array, growth_list)
        gr_df = pd.DataFrame(growth_list, columns=lengths)
        gr_df.insert(0, 'Supersaturation', supersaturation)

        return gr_df