import imp
import os
import numpy as np
from natsort import natsorted
import pandas as pd
from pathlib import Path
from DataProcessor.data.calc_data import Calculate as calculator

class Run:

    def __init__(self):
        self.method = 0
        

    def creates_rates_folder(self, path):
        '''This method returns a new folder to save data,
        with a selected CG simulation / Crystal Aspects folder'''

        rates_folder = Path(path) / 'CrystalAspects' / 'GrowthRates'
        rates_folder.mkdir(parents=True, exist_ok=True)

        return rates_folder

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

        for folder in folders:
            files = os.listdir(folder)
            for f in files:
                f_path = path / folder / f
                f_name = f
                if f_name.startswith("._"):
                    continue
                if f_name.endswith('size.csv'):
                    size_files.append(f_path)
            
                if f_name.endswith('simulation_parameters.txt'):
                    with open(f_path, 'r', encoding='utf-8') as sim_file:
                        lines = sim_file.readlines()

                    for line in lines:
                        if line.startswith('Starting delta mu value (kcal/mol):'):
                            supersat = float(line.split()[-1])
                            supersats.append(supersat)
        print(size_files)

        
        return (supersats, size_files)


    def find_lengths(self, csv):
        '''Returns the lenghts from a size_file'''
        lt_df = pd.read_csv(csv)
        columns = lt_df.columns
        lengths = []
        for col in columns:
            if col.startswith(' '):
                lengths.append(col)

        return lengths

    def run_calc_growth(self, path):
        '''Returns the final df/csv of the 
        growth rates vs supersaturation'''

        savefolder = self.creates_rates_folder(path)
        supersats, size_files = self.find_info(path)

        print(supersats)
        print(size_files)

        calc = calculator()

        growth_rate_df = calc.calc_growth_rate(size_files, supersats)
        growth_rate_df.to_csv(savefolder / 'growthrates.csv')
        