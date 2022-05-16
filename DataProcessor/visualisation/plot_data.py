import imp
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import pandas as pd
import os
import plotly.express as px


class Plotting:

    def create_plots_folder(self, path):
        plots_folder = Path(path) / 'CGPlots'
        plots_folder.mkdir(parents=True, exist_ok=True)
        return plots_folder

    def build_PCAZinng(self, csv='', df='', folderpath='.', i_plot=False):
        if df == '':
            df = pd.read_csv(csv)

        if csv != '':
            folderpath = Path(csv).parents[0]

        savefolder = self.create_plots_folder(folderpath)

        interactions = [col for col in df.columns
                        if col.startswith('interaction')]

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

            if i_plot:
                fig = px.scatter(df, x="S:M", y="M:L", color=interaction,
                                 hover_data=['Simulation Number'])
                fig.write_html(f'{savefolder}/PCAZingg_{interaction}.html')
                fig.show()

    def sph_plot(self, csv, mode=1):
        savefolder = self.create_plots_folder(Path(csv).parents[0])

        df = pd.read_csv(csv)
        interactions = [col for col in df.columns
                        if col.startswith('interaction')]
        if mode == 1:

            for i in interactions:
                fig = px.scatter_3d(df, x='S:M',
                                    y='M:L',
                                    z='Distance',
                                    color=i,
                                    hover_data=['Simulation Number'])
                fig.write_html(f'{savefolder}/SPH_D_Zingg_{i}.html')
                fig.show()

        if mode == 2:
            window_size = 2

            for i in range(len(interactions) - window_size + 1):
                int_window = interactions[i: i + window_size]
                fig = px.scatter_3d(df, x=int_window[0],
                                    y=int_window[1],
                                    z='Distance',
                                    hover_data=['Simulation Number'])
                fig.write_html(f'{savefolder}/SPH_ints_{i}.html')
                fig.show()

            
