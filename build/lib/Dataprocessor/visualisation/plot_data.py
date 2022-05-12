import imp
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import pandas as pd
import os


class Plotting:

    def create_plots_folder(self, path):
        plots_folder = Path(path) / 'CGPlots'
        plots_folder.mkdir(parents=True, exist_ok=True)
        return plots_folder

    def build_PCAZinng(self, csv='', df='', folderpath='.'):
        if df == '':
            df = pd.read_csv(csv)

        if csv != '':
            folderpath = Path(csv).parents[0]

        savefolder = self.create_plots_folder(folderpath)

        interactions = [col for col in df.columns if col.startswith('interaction')]

        x_data = df['S:M']
        y_data = df['M:L']

        for interaction in interactions:
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle='square', facecolor='white')

            plt.figure()

            plt.scatter(x_data, y_data, c=c_df, cmap='plasma', s=1.2)
            plt.axhline(y=0.66, color='black', linestyle='--')
            plt.axvline(x=0.66, color='black', linestyle='--')
            plt.title(textstr)
            plt.xlabel('S/M')
            plt.ylabel('M/L')
            # plt.xlim(0.0, 1.0)
            # plt.ylim(0.0, 1.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r'$\Delta G_{Crystallisation}$ (kcal/mol)')
            savepath = f'{savefolder}/PCAZingg_{interaction}'
            plt.savefig(savepath)
