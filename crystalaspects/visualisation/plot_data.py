# Miscellaneous imports
import numpy as np
import pandas as pd
from pathlib import Path
import ast

# PyQt imports
from PySide6.QtCore import Qt
from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QDialog, QApplication, QPushButton, \
    QVBoxLayout, QMessageBox, QInputDialog, \
    QVBoxLayout, QHBoxLayout, QFileDialog, \
    QGridLayout, QSpinBox, QLabel, \
    QCheckBox, QSizePolicy, QComboBox, \
    QWidget

# Matplotlib import
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
import mplcursors
matplotlib.use('QT5Agg')

class Plotting(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    def create_plots_folder(self, path):
        plots_folder = Path(path) / "CGPlots"
        plots_folder.mkdir(parents=True, exist_ok=True)
        return plots_folder

    def plot_OBA(self, csv='', df='', folderpath="./outputs"):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)
        savefolder = self.create_plots_folder(folderpath)

        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]
        x_data = df["OBA S:M"]
        y_data = df["OBA M:L"]
        print(x_data)
        print(y_data)

        plt.figure()
        plt.scatter(x_data, y_data, s=10)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlim(0, 1)  # Adjust x-axis limits
        plt.ylim(0, 1)  # Adjust y-axis limits
        plt.xlabel('OBA S:M')
        plt.ylabel('OBA M:L')
        savepath = f'{savefolder}/OBA Zingg'
        plt.savefig(savepath, dpi=900)
        plt.close()

        for interaction in interactions:
            plt.figure()
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S: M")
            plt.ylabel("M: L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            savepath = f"{savefolder}/OBAZingg_{interaction}"
            plt.savefig(savepath, dpi=300)
            plt.close()

    def build_PCAZingg(self, csv="", df="", folderpath="./outputs", i_plot=False):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)
        savefolder = self.create_plots_folder(folderpath)

        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]
        x_data = df["PCA S:M"]
        y_data = df["PCA M:L"]

        plt.scatter(x_data, y_data, s=1.2)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)
        plt.xlabel('PCA S:M')
        plt.ylabel('PCA M:L')
        savepath = f'{savefolder}/PCA Zingg'
        plt.savefig(savepath, dpi=900)

        for interaction in interactions:
            plt.figure()
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S: M")
            plt.ylabel("M: L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            savepath = f"{savefolder}/PCAZingg_{interaction}"
            plt.savefig(savepath, dpi=300)
            plt.close()

    def Aspect_Extended_Plot(
        self, csv="", df="", folderpath="./outputs", selected="", i_plot=False
    ):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        savefolder = self.create_plots_folder(folderpath)
        extended_df = df

        i = 0
        plt.figure()
        x_data = extended_df[f"AspectRatio_{selected[i]}/{selected[i+1]}"]
        y_data = extended_df[f"AspectRatio_{selected[i+1]}/{selected[i+2]}"]
        plt.scatter(x_data, y_data, s=1.2)
        plt.xlabel(f"AspectRatio_{selected[i]}/{selected[i+1]}")
        plt.ylabel(f"AspectRatio_{selected[i+1]}/{selected[i+2]}")
        savepath = f"{savefolder}/Aspect_{selected[i]}_{selected[i+1]}_[{selected[i+2]}"
        plt.savefig(savepath, dpi=300)
        plt.close()

        interactions = [
            col
            for col in extended_df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        for interaction in interactions:
            plt.figure()
            c_df = extended_df[interaction]
            print(c_df)
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.title(textstr)
            plt.xlabel(f"AspectRatio_{selected[i]}/{selected[i+1]}")
            plt.ylabel(f"AspectRatio_{selected[i+1]}/{selected[i+2]}")
            plt.xlim(0.0)
            plt.ylim(0.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            savepath = f"{savefolder}/Aspect_{selected[i]}_{selected[i+1]}_{selected[i+2]}_{interaction}"
            print(savepath)
            plt.savefig(savepath, dpi=300)
            plt.close()

    def CDA_Plot(self, csv="", df="", folderpath="./outputs", i_plot=False):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        zn_df = df
        savefolder = self.create_plots_folder(folderpath)

        x_data = zn_df["S/M"]
        y_data = zn_df["M/L"]

        plt.figure()
        plt.scatter(x_data, y_data, s=1.2)
        plt.xlabel("S/M")
        plt.ylabel("M/L")
        savepath = f"{savefolder}/CDA"
        plt.savefig(savepath, dpi=300)
        plt.close()

        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        for interaction in interactions:
            plt.figure()
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S/M")
            plt.ylabel("M/L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            savepath = f"{savefolder}/CDAZingg_{interaction}"
            plt.savefig(savepath, dpi=300)
            plt.close()

    def PCA_CDA_Plot(self, csv="", df="", folderpath="./outputs", i_plot=False):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        zn_df = df
        savefolder = self.create_plots_folder(folderpath)

        equations = set(zn_df["CDA_Equation"])

        for equation in equations:
            plt.figure()
            textstr = equation
            equation_df = zn_df[zn_df["CDA_Equation"] == equation]
            x_data = equation_df["PCA S:M"]
            y_data = equation_df["PCA M:L"]
            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S:M")
            plt.ylabel("M:L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            savepath = f"{savefolder}/PCA_CDA_eq{equation}"
            plt.savefig(savepath, dpi=300)
            plt.close()

    def build_CDA_OBA(
        self, csv="", df="", folderpath="./outputs", i_plot=False
    ):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv) 

        zn_df = df
        savefolder = self.create_plots_folder(folderpath)
        equations = set(zn_df["CDA_Equation"])

        for equation in equations:
            plt.figure()
            textstr = equation
            equation_df = zn_df[zn_df["CDA_Equation"] == equation]
            x_data = equation_df["OBA S:M"]
            y_data = equation_df["OBA M:L"]
            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S:M")
            plt.ylabel("M:L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            savepath = f"{savefolder}/OBA_CDA_eq{equation}"
            plt.savefig(savepath, dpi=300)
            plt.close()

    ####################################
    # Plotting Surface Area and Volume #
    ####################################

    def SAVAR_plot(self, csv="", df="", folderpath="./outputs", i_plot=False):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        savar_df = df

        savefolder = self.create_plots_folder(folderpath)
        interactions = [
            col
            for col in savar_df.columns
            if col.startswith("interaction")
            or col.startswith("tile")
            or col.startswith("temperature")
        ]

        x_data = savar_df["Volume (Vol)"]
        y_data = savar_df["Surface Area (SA)"]
        plt.figure()
        for interaction in interactions:
            c_df = savar_df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            plt.xlabel(r"Volume ($\mu$$m^3$)")
            plt.ylabel(r"Surface Area ($\mu$$m^2$)")
            savepath = f"{savefolder}/SAVAR_{interaction}"
            plt.savefig(savepath, dpi=900)
        plt.close()

        plt.scatter(x_data, y_data, s=1.2)
        plt.xlabel(r"Volume ($\mu$$m^3$)")
        plt.ylabel(r"Surface Area ($\mu$$m^2$)")
        savepath = f"{savefolder}/SAVAR"
        plt.savefig(savepath, dpi=900)

    def sph_plot(self, csv, mode=1):
        savefolder = self.create_plots_folder(Path(csv).parents[0])

        df = pd.read_csv(csv)
        interactions = [col for col in df.columns if col.startswith("interaction")]
        solvents = [col for col in df.columns if col.startswith("distance")]
        if mode == 1:
            for sol in solvents:
                for i in interactions:
                    fig = px.scatter_3d(
                        df,
                        x="S:M",
                        y="M:L",
                        z=sol,
                        color=i,
                        hover_data=["Simulation Number"],
                    )
                    fig.write_html(f"{savefolder}/SPH_D_Zingg_{sol}_{i}.html")
                    fig.show()

        if mode == 2:
            window_size = 2

            for i in range(len(interactions) - window_size + 1):
                int_window = interactions[i : i + window_size]
                fig = px.scatter_3d(
                    df,
                    x=int_window[0],
                    y=int_window[1],
                    z="Distance",
                    hover_data=["Simulation Number"],
                )
                fig.write_html(f"{savefolder}/SPH_ints_{i}.html")
                fig.show()

    def sph_plot_SvL(self, csv, mode=1):
        savefolder = self.create_plots_folder(Path(csv).parents[0])

        df = pd.read_csv(csv)
        interactions = [col for col in df.columns if col.startswith("interaction")]
        solvents = [col for col in df.columns if col.startswith("distance")]
        if mode == 1:
            for sol in solvents:
                for i in interactions:
                    fig = px.scatter_3d(
                        df,
                        x="Small",
                        y="Long",
                        z=sol,
                        color=i,
                        hover_data=["Simulation Number"],
                    )
                    fig.write_html(f"{savefolder}/SPH_SvL_D_Zingg_{sol}_{i}.html")
                    # fig.show()

        if mode == 2:
            window_size = 2

            for i in range(len(interactions) - window_size + 1):
                int_window = interactions[i : i + window_size]
                fig = px.scatter_3d(
                    df,
                    x=int_window[0],
                    y=int_window[1],
                    z="Distance",
                    hover_data=["Simulation Number"],
                )
                fig.write_html(f"{savefolder}/SPH_ints_{i}.html")

    """    
    def visualise_pca(self, xyz):

        shape = CrystalShape()
        savefolder = self.create_plots_folder(Path(xyz).parents[0])

        points, _, _ = shape.read_XYZ(xyz)

        eig_sval, eig_val, eig_vec = shape.get_PCA_nn(points)

        # Center = origin
        mean_x = 0
        mean_y = 0
        mean_z = 0

        list_styles = [
            "Solarize_Light2",
            "_classic_test_patch",
            "bmh",
            "classic",
            "dark_background",
            "fast",
            "fivethirtyeight",
            "ggplot",
            "grayscale",
            "seaborn",
            "seaborn-bright",
            "seaborn-colorblind",
            "seaborn-dark",
            "seaborn-dark-palette",
            "seaborn-darkgrid",
            "seaborn-deep",
            "seaborn-muted",
            "seaborn-notebook",
            "seaborn-paper",
            "seaborn-pastel",
            "seaborn-poster",
            "seaborn-talk",
            "seaborn-ticks",
            "seaborn-white",
            "seaborn-whitegrid",
            "tableau-colorblind10",
        ]

        plt.style.use("seaborn-dark")

        ################################
        # Plotting eigenvectors
        ################################

        fig = plt.figure(figsize=(10, 10))
        ax = fig.add_subplot(111, projection="3d")

        ax.plot(
            points[:, 0],
            points[:, 1],
            points[:, 2],
            "o",
            markersize=0.4,
            color="blue",
            alpha=1,
        )
        ax.plot(
            [mean_x], [mean_y], [mean_z], "o", markersize=10, color="red", alpha=0.5
        )
        colours = ["red", "green", "blue"]
        i = 0
        scale_factor = [
            (eig_sval[0] / eig_sval[2]),
            (eig_sval[1] / eig_sval[2]),
            (eig_sval[1] / eig_sval[2]),
        ]
        for v in eig_vec:
            v = v * scale_factor[i] * 50
            print(v)
            print(v[0], v[1], v[2])
            print(eig_sval)
            ax.plot(
                [-v[0], v[0]],
                [-v[1], v[1]],
                [-v[2], v[2]],
                color=colours[i],
                alpha=0.8,
                lw=2,
            )

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
        plt.axis("off")
        plt.grid(b=None)

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")

        plt.show() 
        """

    ################################
    # Plotting Growth Rates        #
    ################################

    def plot_growth_rates(self, gr_df, lengths, savepath):
        x_data = gr_df["Supersaturation"]
        print(lengths)
        for i in lengths:
            plt.scatter(x_data, gr_df[i], s=1.2)
            plt.plot(x_data, gr_df[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
        plt.savefig(savepath / "Growth_rates+Dissolution_rates2", dpi=300)

        growth_data = gr_df[gr_df["Supersaturation"] >= 0]
        plt.clf()
        plt.figure(figsize=(5, 5))

        for i in lengths:
            plt.scatter(growth_data["Supersaturation"], growth_data[i], s=1.2)
            plt.plot(growth_data["Supersaturation"], growth_data[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
        plt.savefig(savepath / "Growth_rates2", dpi=300)

        plt.clf()
        plt.figure(figsize=(5, 5))
        for i in lengths:
            plt.scatter(growth_data["Supersaturation"], growth_data[i], s=1.2)
            plt.plot(growth_data["Supersaturation"], growth_data[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.xlim(0.0, 2.5)
            plt.ylim(0.0, 0.4)
            plt.tight_layout()
        plt.savefig(savepath / "Growth_rates2_zoomed", dpi=300)

        dissolution_data = gr_df[gr_df["Supersaturation"] <= 0]
        plt.clf()
        plt.figure(figsize=(7, 5))
        for i in lengths:
            plt.scatter(
                dissolution_data["Supersaturation"], dissolution_data[i], label=i, s=1.2
            )
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Dissolution Rate")
            plt.tight_layout()
        plt.savefig(savepath / "Dissolution_rates2", dpi=300)

        plt.clf()
        plt.figure(figsize=(5, 5))
        for i in lengths:
            plt.scatter(dissolution_data["Supersaturation"], dissolution_data[i], s=1.2)
            plt.plot(dissolution_data["Supersaturation"], dissolution_data[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.xlim(-2.5, 0.0)
            plt.ylim(-2.5, 0.0)
            plt.tight_layout()
        plt.savefig(savepath / "Dissolution2_zoomed", dpi=300)

    def update_annot(self, ind):

        pos = self.scatter.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        text = "Simulation Number: " + "{}".format(" ".join(list(map(str, ind["ind"]))))
        self.annot.set_text(text)
        #self.annot.get_bbox_patch().set_facecolor(self.c_df(norm(c[ind["ind"][0]])))
        self.annot.get_bbox_patch().set_alpha(0.4)
        print("Text for Annotation:")
        print(text)

    def on_hover(self, event):
        vis = self.annot.get_visible()
        try:
            if event.inaxes == self.ax:
                cont, ind = self.scatter.contains(event)
                if cont:
                    self.update_annot(ind)
                    self.annot.set_visible(True)
                    self.figure.canvas.draw_idle()
                else:
                    if vis:
                        self.annot.set_visible(False)
                        self.figure.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                self.figure.canvas.draw_idle()
        except NameError:
            pass

    def add_trendline(self):
        if self.scatter is None:
            self.statusBar().showMessage("Error: No scatter plot to add trendline to.")
            return
        x = self.scatter.get_offsets()[:, 0]
        y = self.scatter.get_offsets()[:, 1]

        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        self.ax.plot(x, p(x), "r--")

        self.canvas.draw()

    def save(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("png")
        file_dialog.setNameFilters(["PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)"])
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog.setDirectory(".")
        file_dialog.setWindowTitle("Save Plot")

        if file_dialog.exec_() == QDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]
            transparent = QMessageBox.question(self, "Transparent Background", "Do you want a transparent background?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes

            if file_name:
                size = [6.8, 4.8]
                if transparent:
                    self.figure.savefig(file_name, figsize=size, transparent=True, dpi=600)
                else:
                    self.figure.savefig(file_name, figsize=size, dpi=600)

    def edit(self):
        pass