# Miscellaneous imports
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA


#Matplotlib imports
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

# Current Project imports
from DataProcessor.tools.shape_analysis import CrystalShape

class Plotting:

    def create_plots_folder(self, path):
        plots_folder = Path(path) / 'CGPlots'
        plots_folder.mkdir(parents=True, exist_ok=True)
        return plots_folder

    def build_PCAZinng(self, csv='', df='', folderpath='./outputs', i_plot=False):
        if df == '':
            df = pd.read_csv(csv)


        if csv != '':
            folderpath = Path(csv).parents[0]

        savefolder = self.create_plots_folder(folderpath)

        interactions = [col for col in df.columns
                        if col.startswith('interaction') or col.startswith('tile')]
        

        x_data = df['S:M']
        y_data = df['M:L']

        for interaction in interactions:
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle='square', facecolor='white')

            plt.figure()
            print('FIG')
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
            plt.savefig(savepath, dpi=300)

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
        solvents = [col for col in df.columns
                    if col.startswith('distance')]
        if mode == 1:
            for sol in solvents:
                for i in interactions:
                    fig = px.scatter_3d(df, x='S:M',
                                        y='M:L',
                                        z=sol,
                                        color=i,
                                        hover_data=['Simulation Number'])
                    fig.write_html(f'{savefolder}/SPH_D_Zingg_{sol}_{i}.html')
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

    def sph_plot_SvL(self, csv, mode=1):
        savefolder = self.create_plots_folder(Path(csv).parents[0])

        df = pd.read_csv(csv)
        interactions = [col for col in df.columns
                        if col.startswith('interaction')]
        solvents = [col for col in df.columns
                    if col.startswith('distance')]
        if mode == 1:
            for sol in solvents:
                for i in interactions:
                    fig = px.scatter_3d(df, x='Small',
                                        y='Long',
                                        z=sol,
                                        color=i,
                                        hover_data=['Simulation Number'])
                    fig.write_html(f'{savefolder}/SPH_SvL_D_Zingg_{sol}_{i}.html')
                    # fig.show()

        if mode == 2:
            window_size = 2

            for i in range(len(interactions) - window_size + 1):
                int_window = interactions[i: i + window_size]
                fig = px.scatter_3d(df, x=int_window[0],
                                    y=int_window[1],
                                    z='Distance',
                                    hover_data=['Simulation Number'])
                fig.write_html(f'{savefolder}/SPH_ints_{i}.html')
                # fig.show()

    def visualise_pca(self, xyz):

        shape = CrystalShape()
        savefolder = self.create_plots_folder(Path(xyz).parents[0])
        
        points = shape.read_XYZ(xyz)

        eig_sval, eig_val, eig_vec = shape.get_PCA_nn(points)

        # Center = origin
        mean_x = 0
        mean_y = 0
        mean_z = 0

        list_styles = ['Solarize_Light2', '_classic_test_patch', 'bmh', 'classic', 'dark_background', 'fast', 'fivethirtyeight', 'ggplot', 'grayscale', 'seaborn', 'seaborn-bright', 'seaborn-colorblind', 'seaborn-dark', 'seaborn-dark-palette', 'seaborn-darkgrid', 'seaborn-deep', 'seaborn-muted', 'seaborn-notebook', 'seaborn-paper', 'seaborn-pastel', 'seaborn-poster', 'seaborn-talk', 'seaborn-ticks', 'seaborn-white', 'seaborn-whitegrid', 'tableau-colorblind10']
        
        plt.style.use('seaborn-dark')

        ################################
        # Plotting eigenvectors
        ################################

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection='3d')

        ax.plot(points[:, 0], points[:, 1], points[:, 2], 'o',
                markersize=0.4,
                color='blue', alpha=1)
        ax.plot([mean_x], [mean_y], [mean_z], 'o',
                markersize=10, color='red', alpha=0.5)
        colours = ['red', 'green', 'blue']
        i = 0
        scale_factor = [(eig_sval[0]/eig_sval[2]), (eig_sval[1]/eig_sval[2]), (eig_sval[1]/eig_sval[2])]
        for v in eig_vec:
            v = v * scale_factor[i] * 50
            print(v)
            print(v[0], v[1], v[2])
            print(eig_sval)
            ax.plot([-v[0], v[0]],
                    [-v[1], v[1]],
                    [-v[2], v[2]],
                    color=colours[i], alpha=0.8, lw=2)

            ax.xaxis.set_tick_params(labelsize=5)
            ax.yaxis.set_tick_params(labelsize=5)
            ax.zaxis.set_tick_params(labelsize=5)
            # ax.set(facecolor='pink')
            # ax.set_xticks([-1, -0.5, 0, 0.5, 1])
            ax.set_xlim([-75, 75])
            # ax.set_yticks([-1, -0.5, 0, 0.5, 1])
            ax.set_ylim([-75, 75]) 
            # ax.set_zticks([-1, -0.5, 0, 0.5, 1])
            ax.set_zlim([-75, 75])

            i += 1
        plt.axis('off')
        plt.grid(b=None)

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        plt.show()

    def plot_growth_rates(self, gr_df, lengths, savepath):
        x_data = gr_df['Supersaturation']
        print(lengths)
        for i in lengths:
            plt.scatter(x_data, gr_df[i], s=1.2)
            plt.plot(x_data, gr_df[i], label=i)
            plt.legend()
            plt.xlabel('Supersaturation (kcal/mol)')
            plt.ylabel('Growth Rate')
            plt.tight_layout()
        # plt.show()
        plt.savefig(savepath / 'Growth_rates+Dissolution_rates2', dpi=300)

        growth_data = gr_df[gr_df['Supersaturation'] >= 0]
        # print(growth_data)
        plt.clf()
        plt.figure(figsize=(5, 5))

        for i in lengths:
            plt.scatter(growth_data['Supersaturation'], growth_data[i], label=i, s=1.2)
            plt.legend()
            plt.xlabel('Supersaturation (kcal/mol)')
            plt.ylabel('Growth Rate')
            plt.tight_layout()
        # plt.show()
        plt.savefig(savepath / 'Growth_rates2', dpi=300)

        plt.clf()
        plt.figure(figsize=(5, 5))
        for i in lengths:
            plt.scatter(growth_data['Supersaturation'], growth_data[i], s=1.2)
            plt.plot(growth_data['Supersaturation'], growth_data[i], label=i)
            plt.legend()
            plt.xlabel('Supersaturation (kcal/mol)')
            plt.ylabel('Growth Rate')
            plt.xlim(0.0, 2.5)
            plt.ylim(0.0, 0.4)
            plt.tight_layout()
        # plt.show()
        plt.savefig(savepath / 'Growth_rates2_zoomed', dpi=300)

        dissolution_data = gr_df[gr_df['Supersaturation'] <= 0]
        # print(dissolution_data)
        plt.clf()
        plt.figure(figsize=(7, 5))
        for i in lengths:
            plt.scatter(dissolution_data['Supersaturation'], dissolution_data[i], label=i, s=1.2)
            plt.legend()
            plt.xlabel('Supersaturation (kcal/mol)')
            plt.ylabel('Dissolution Rate')
            plt.tight_layout()
        # plt.show()
        plt.savefig(savepath / 'Dissolution_rates2', dpi=300)

        plt.clf()
        plt.figure(figsize=(5, 5))
        for i in lengths:
            plt.scatter(dissolution_data['Supersaturation'], dissolution_data[i], s=1.2)
            plt.plot(dissolution_data['Supersaturation'], dissolution_data[i], label=i)
            plt.legend()
            plt.xlabel('Supersaturation (kcal/mol)')
            plt.ylabel('Growth Rate')
            plt.xlim(-2.5, 0.0)
            plt.ylim(-2.5, 0.0)
            plt.tight_layout()
        # plt.show()
        plt.savefig(savepath / 'Dissolution2_zoomed', dpi=300)
        return

