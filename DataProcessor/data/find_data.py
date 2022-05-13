import numpy as np
import pandas as pd
import os
import re
from pathlib import Path
from natsort import natsorted
from DataProcessor.tools.shape_analysis import CrystalShape as cs
from DataProcessor.data.calc_data import Calculate as calc


class Run:

    def __init__(self):
        self.method = 0

    def create_aspects_folder(self, path):
        aspects_folder = Path(path) / 'CrystalAspects'
        aspects_folder.mkdir(parents=True, exist_ok=True)

        return aspects_folder

    def build_AR_PCA(self, subfolder):
        # from time import time
        # print(subfolder)
        aspects_folder = self.create_aspects_folder(subfolder)

        final_array = np.empty((0, 6), np.float64)
        print(final_array.shape)

        for file in Path(subfolder).iterdir():
            # print(file)
            # t0 = time()
            if not file.suffix == '.XYZ':
                continue

            sim_num = re.findall(r'\d+', Path(file).name)[-1]
            shape = cs(10)
            try:
                vals = shape.get_PCA(file=file)
                # print(vals)

                calculator = calc()
                ar_data = calculator.aspectratio_pca(pca_vals=vals)
                ar_data = np.insert(ar_data, 0, sim_num, axis=1)

                final_array = np.append(final_array, ar_data, axis=0)
                print(final_array.shape)

            except StopIteration:
                continue
            # t1 = time()
            # print("tot", t1 - t0)

        print(final_array.shape)

        # Converting np array to pandas df
        df = pd.DataFrame(final_array, columns=['Simulation Number',
                                                'Small',
                                                'Medium',
                                                'Long',
                                                'S:M',
                                                'M:L'])
        aspects_folder = Path(subfolder) / 'CrystalAspects'
        aspect_csv = f'{aspects_folder}/PCA_aspectratio.csv'
        df.to_csv(aspect_csv)

        return df

    def build_AR_Crystallographic(self):
        pass

    def aspect_ratio_csv(self, folder, method=0):
        if method == 0:
            self.method = "PCA"
            print(self.method)
        if method == 1:
            self.method = "Crystallographic"

        if self.method == 'PCA':
            return self.build_AR_PCA(folder)
        if self.method == 'Crystallographic':
            return self.build_AR_Crystallographic(folder)

    def build_SPH_distance(self, subfolder, ref_shape):
        aspects_folder = self.create_aspects_folder(subfolder)
        distance_array = np.empty((0, 2), np.float64)

        shape = cs(10)
        ref_coeffs = shape.reference_shape(ref_shape)

        for file in Path(subfolder).iterdir():
            # print(file)
            if not file.suffix == '.XYZ':
                continue

            sim_num = re.findall(r'\d+', Path(file).name)[-1]
            try:
                coeffs = shape.get_coeffs(filepath=file)
                distance = shape.compare_shape(ref_coeffs=ref_coeffs,
                                               shape_coeffs=coeffs)
                arr_data = np.array([[sim_num, distance]])

                distance_array = np.append(distance_array, arr_data, axis=0)
                print(distance_array.shape)
            except StopIteration:
                continue

        df = pd.DataFrame(distance_array, columns=['Simulation Number',
                                                   'Distance'])
        aspects_folder = self.create_aspects_folder(subfolder)
        sph_csv = f'{aspects_folder}/SpH_compare.csv'
        df.to_csv(sph_csv)

    def build_SAVAR(self):
        pass

    def summary_compare(self, summary_csv, aspect_csv='',
                        aspect_df='', cg_version='new'):

        summary_df = pd.read_csv(summary_csv)

        if aspect_df == '':
            aspect_df = pd.read_csv(aspect_csv)

        summary_cols = summary_df.columns
        aspect_cols = aspect_df.columns[1:]

        if cg_version == 'new':
            '''This allows the user to pick the two different 
            summary file verions from CrystalGrower'''

            search = summary_df.iloc[0, 0]
            search = search.split('_')
            search_string = '_'.join(search[:-1])

            int_cols = summary_cols[1:]
            summary_df = summary_df.set_index(summary_cols[0])
            compare_array = np.empty((0, 7 + len(int_cols)))

            for index, row in aspect_df.iterrows():
                sim_num = int(row['Simulation Number'] - 1)
                num_string = f'{search_string}_{sim_num}'
                print(num_string)
                aspect_row = row.values
                aspect_row = np.array([aspect_row])
                collect_row = summary_df.filter(items=[num_string],
                                                axis=0).values
                print(collect_row)
                collect_row = np.concatenate([aspect_row, collect_row], axis=1)
                compare_array = np.append(compare_array, collect_row, axis=0)
                print(compare_array.shape)

        if cg_version == 'old':
            int_cols = summary_cols[1:]
            compare_array = np.empty((0, 6 + len(int_cols)))

            for index, row in aspect_df.iterrows():
                sim_num = int(row['Simulation Number'] - 1)
                aspect_row = row.values[1:]
                aspect_row = np.array([aspect_row])
                print(aspect_row)
                collect_row = [summary_df.iloc[sim_num].values[1:]]
                print(collect_row)
                collect_row = np.concatenate([aspect_row, collect_row], axis=1)
                compare_array = np.append(compare_array, collect_row, axis=0)
                print(compare_array.shape)

        print(aspect_cols, int_cols)
        cols = aspect_cols.append(int_cols)
        print(f'COLS:::: {cols}')
        compare_df = pd.DataFrame(compare_array[:, :], columns=cols)
        print(compare_df)
        full_df = compare_df.sort_values(by=['Simulation Number'],
                                         ignore_index=True)

        filepath = Path(summary_csv)
        aspects_folder = Path(filepath.parents[0]) / 'CrystalAspects'
        if not os.path.exists(aspects_folder):
            os.makedirs(aspects_folder)

        aspect_energy_csv = f'{aspects_folder}/aspectratio_energy.csv'
        failed_sims_csv = f'{aspects_folder}/failed_sims.csv'

        full_df.to_csv(aspect_energy_csv)
        summary_df.to_csv(failed_sims_csv)

        print(full_df)
        print(summary_df)
