import numpy as np
import pandas as pd
import os
from natsort import natsorted
import re
from pathlib import Path
from DataProcessor.tools.shape_analysis import CrystalShape as cs
from DataProcessor.data.calc_data import Calculate as calc
from DataProcessor.data.aspect_ratios import AspectRatio

from PyQt5 import QtWidgets, QtGui, QtCore, QtOpenGL 
from PyQt5.QtWidgets import QApplication, QComboBox, QMainWindow, QMessageBox, QShortcut, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence


class Find:

    def __init__(self):
        self.method = 0

    def create_aspects_folder(self, path):
        aspects_folder = Path(path) / 'CrystalAspects'
        aspects_folder.mkdir(parents=True, exist_ok=True)

        return aspects_folder

    def find_info(self, path):
        '''The method returns the crystallographic directions,
        supersations, and the size_file paths from a CG simulation folder'''

        path = Path(path)
        files = os.listdir(path)
        contents = natsorted(files)
        folders = []
        for item in contents:
            item_name = item
            print(item_name)
            item_path = path / item
            if os.path.isdir(item_path):
                if item_name.endswith('XYZ_files') or item_name.endswith('CrystalAspects') \
                or item_name.endswith('CrystalMaps'):
                    continue
                else:
                    folders.append(item_path)
        print(folders)
        size_files = []
        supersats = []
        directions = []

        i = 0
        for folder in folders:
            files = os.listdir(folder)
            for f in files:
                f_path = path / folder / f
                f_name = f

                if f_name.startswith("._"):
                    continue
                if f_name.endswith('size.csv'):
                    if os.stat(f_path).st_size == 0:
                        growth_rates = False
                    else:
                        size_files.append(f_path)
                        growth_rates = True

                    # directions = self.find_growth_directions(f_path)
            
                if f_name.endswith('simulation_parameters.txt'):
                    with open(f_path, 'r', encoding='utf-8') as sim_file:
                        lines = sim_file.readlines()

                    for line in lines:
                        if line.startswith('Starting delta mu value (kcal/mol):') and growth_rates:
                            supersat = float(line.split()[-1])
                            supersats.append(supersat)
                        if line.startswith('normal, ordered or growth modifier'):
                            selected_mode = line.split('               ')[-1]
                            if selected_mode == 'growth_modifier\n':
                                growth_mod = True
                            else:
                                growth_mod = False
                        

                        
                        if line.startswith('Size of crystal at frame output') and i==0:
                            frame = lines.index(line) + 1
                            # From starting point - read facet information
                            for n in range(frame, len(lines)):
                                line = lines[n]
                                if line == ' \n':
                                    break
                                else:
                                    facet = line.split('      ')[0]
                                    if len(facet) <= 8:
                                        directions.append(facet)
            i += 1

        
        return (supersats, size_files, directions, growth_mod)


    def find_growth_directions(self, csv):
        '''Returns the lenghts from a size_file'''
        lt_df = pd.read_csv(csv)
        columns = lt_df.columns
        directions = []
        for col in columns:
            if col.startswith(' '):
                directions.append(col)

        return directions

    def find_cda_directions(self, file):
        pass    

    def aspect_ratio_csv(self, folder, method=0):
        aspects = AspectRatio()
        if method == 0:
            self.method = "PCA"
            print(self.method)
        if method == 1:
            self.method = "Crystallographic"
        
        if self.method == 'PCA':
            return aspects.build_AR_PCA(folder)
        if self.method == 'Crystallographic':
            return aspects.build_AR_Crystallographic(folder)

    def build_SPH_distance(self, subfolder,
                           ref_shape_list, l_max=20,
                           id_list=['Distance']):

        aspects_folder = self.create_aspects_folder(subfolder)

        n_refs = len(ref_shape_list)
        distance_array = np.empty((0, 1 + n_refs), np.float64)

        shape = cs(l_max)
        ref_coeffs_list = []

        for ref_shape in ref_shape_list:
            ref_coeffs = shape.reference_shape(ref_shape)
            ref_coeffs_list.append(ref_coeffs)

        for file in Path(subfolder).iterdir():
            if not file.suffix == '.XYZ':
                continue
            distance_list = []

            sim_num = re.findall(r'\d+', Path(file).name)[-1]
            try:
                coeffs = shape.get_coeffs(filepath=file)
                for ref_coeffs in ref_coeffs_list:
                    distance = shape.compare_shape(ref_coeffs=ref_coeffs,
                                                   shape_coeffs=coeffs)
                    distance_list.append(distance)
                arr_data = np.array([[sim_num, *distance_list]])

                distance_array = np.append(distance_array, arr_data, axis=0)
                print(distance_array.shape)

            except StopIteration:
                continue
            except UnicodeDecodeError:
                continue

        df = pd.DataFrame(distance_array, columns=['Simulation Number',
                                                   *id_list])
        df = df.sort_values(by=['Simulation Number'],
                            ignore_index=True)
        aspects_folder = self.create_aspects_folder(subfolder)
        sph_csv = f'{aspects_folder}/SpH_compare.csv'
        print(df)
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

    def energy_from_sph(self, csv_path, solvents=['water']):
        
        csv = Path(csv_path)
        df = pd.read_csv(csv)

        interactions = [col for col in df.columns
                        if col.startswith('interaction')]

        solvents_found = [col for col in df.columns
                    if col.startswith('distance')]
        solvents_matched = []
        for sol in solvents:
            for sol_found in solvents_found:
                if sol in sol_found:
                    solvents_matched.append(sol_found)
        
        print(solvents_matched)

        for sol in solvents_matched:
            print(sol)

            df = df.sort_values(by=[sol])

            for i in interactions:
                int_label = i.split('_')
                mean_col = f'mean_{int_label[-1]}'
                df[mean_col] = df[i].expanding().mean()

            energy_solvent_csv = f'{csv.parents[0]}/mean_energies_{sol}.csv'

            df.to_csv(energy_solvent_csv)
