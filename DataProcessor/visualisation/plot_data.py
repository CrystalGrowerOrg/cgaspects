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
# from DataProcessor.tools.shape_analysis import CrystalShape

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs
        print('INITIALISED')


    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

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

    def read_XYZ(self, filepath):
        self.xyz = np.loadtxt(filepath, skiprows=2)[:, 3:]
        return self.xyz
    
    def normalise_verts(self, verts):

        self.centered = verts - np.mean(verts, axis=0)
        norm = np.linalg.norm(self.centered, axis=1).max()
        self.centered /= norm

        return self.centered
    
    def get_PCA_all(self, file, n=3):
        points = self.read_XYZ(filepath=file)
        points_norm = self.normalise_verts(points)
        pca = PCA(n_components=n)
        pca.fit(points_norm)
        pca_vectors = pca.components_
        pca_values = pca.explained_variance_ratio_
        pca_svalues = pca.singular_values_

        # print(pca_vectors)
        # print(pca_values)
        # print(pca_svalues)

        return (pca_svalues, pca_values, pca_vectors, points_norm)

    
    def visualise_pca(self, xyz):
        savefolder = self.create_plots_folder(Path(xyz).parents[0])

        eig_sval, eig_val, eig_vec, points = self.get_PCA_all(xyz)

        # Center = origin
        mean_x = 0
        mean_y = 0
        mean_z = 0


        ################################
        # Plotting eigenvectors
        ################################

        fig = plt.figure(figsize=(5,5))
        ax = fig.add_subplot(111, projection='3d')

        ax.plot(points[:,0], points[:,1], points[:,2], 'o', markersize=0.05, color='black', alpha=0.8)
        ax.plot([mean_x], [mean_y], [mean_z], 'o', markersize=10, color='red', alpha=0.5)
        colours = ['red', 'green', 'blue']
        i = 0
        for v in eig_vec:
            print(v[0], v[1], v[2])
            scale_factor = eig_sval[i]
            print(eig_sval)
            ax.plot([mean_x,v[0]],
                    [mean_y,v[1]],
                    [mean_z,v[2]],
                    color=colours[i], alpha=0.8, lw=2)

            ax.xaxis.set_tick_params(labelsize=5)
            ax.yaxis.set_tick_params(labelsize=5)
            ax.zaxis.set_tick_params(labelsize=5)
            # ax.set(facecolor='pink')
            ax.set_xticks([-1, -0.5, 0, 0.5, 1])
            ax.set_xlim([-1, 1])
            ax.set_yticks([-1, -0.5, 0, 0.5, 1])
            ax.set_ylim([-1, 1]) 
            ax.set_zticks([-1, -0.5, 0, 0.5, 1])
            ax.set_zlim([-1, 1])
            i += 1
    
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        plt.show()

