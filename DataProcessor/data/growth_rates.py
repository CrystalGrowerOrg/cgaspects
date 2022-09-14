import imp
import os
import numpy as np
from natsort import natsorted
import pandas as pd
from pathlib import Path

from DataProcessor.data.find_data import Find
from DataProcessor.data.calc_data import Calculate
from DataProcessor.visualisation.plot_data import Plotting

class GrowthRate:

    def __init__(self):
        self.method = 0
        

    def creates_rates_folder(self, path):
        '''This method returns a new folder to save data,
        with a selected CG simulation / Crystal Aspects folder'''

        rates_folder = Path(path) / 'CrystalAspects' / 'GrowthRates'
        rates_folder.mkdir(parents=True, exist_ok=True)

        return rates_folder

    

    def run_calc_growth(self, path, plotting=True):
        '''Returns the final df/csv of the 
        growth rates vs supersaturation'''

        savefolder = self.creates_rates_folder(path)

        find = Find()
        supersats, size_files = find.find_info(path)

        print(supersats)
        print(size_files)

        calc = Calculate()

        growth_rate_df = calc.calc_growth_rate(size_files, supersats)
        growth_rate_df.to_csv(savefolder / 'growthrates.csv')

        if plotting:
            plot = Plotting()
            plot.plot_growth_rates(growth_rate_df, savefolder)