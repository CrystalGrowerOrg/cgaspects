import numpy as np
import pandas as pd
from pathlib import Path

# PyQt imports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout

# Matplotlib import
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('QT5Agg')

from CrystalAspects.GUI.load_GUI import Ui_MainWindow
from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.visualisation.plot_data import Plotting


class Replotting:
    '''def __init__(self):
        pass'''

    def __init__(self):
        super(Replotting, self).__init__()

    def calculate_plots(self, csv="", info=""):
        print("Info:  ")
        print(info)
        print("Entered calculate plots")
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)
        plot_list = []
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]
        print(interactions)
        number_interactions = len(interactions)
        print(number_interactions)

        if info.PCA == True:
            plot_list.append("Morphology Map")
        if info.Energies and info.PCA == True:
            for interaction in interactions:
                plot_list.append("PCA Aspect Ratio " + interaction)
        if info.CDA == True:
            plot_list.append("CDA Aspect Ratio")
        if info.CDA and info.Energies == True:
            for interaction in interactions:
                plot_list.append("CDA Aspect Ratio " + interaction)
        if info.SAVol == True:
            plot_list.append("Surface Area vs Volume")
        if info.SAVol and info.Energies == True:
            for interaction in interactions:
                plot_list.extend("Surface area vs Volume " + interaction)
        if info.CDA_Extended == True:
            plot_list.append("Extended CDA")
        if info.CDA_Extended and info.Energies == True:
            for interaction in interactions:
                plot_list.append("CDA Extended " + interaction)
        if info.CDA and info.Temperature == True:
            plot_list.append("CDA Aspect Ratio vs Temperature")
        print("List of plots =====")
        print(plot_list)

        return plot_list

    def replot_AR(self, csv, info, selected):
        print('Entered Plotting')
        print(csv, info, selected)
        folderpath = Path(csv)
        df = pd.read_csv(csv)
        #savefolder = self.create_plots_folder(folderpath)
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        x_data = df["S:M"]
        y_data = df["M:L"]
        print(x_data)

        # Clear figure
        self.figure.clear()

        # Plot the data
        plt.scatter(x_data, y_data, s=1.2)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlabel('S:M')
        plt.ylabel('M:L')
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)

        # Refresh canvas
        self.canvas.draw()

        for interaction in interactions:
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
            #pylustrator.start()
            #plt.show()

        """
        CDA
        CDA + Eq
        CDA + Int
        Cryst D + Int
        PCA
        PCA + CDA Eq
        PCA + Int 
        """

    def replot_GrowthRate(self, csv, info, selected, savepath):
        plt.close()
        print(csv, info, selected)
        gr_df = pd.read_csv(csv)
        x_data = gr_df["Supersaturation"]
        print(selected)
        for i in selected:
            print(selected)
            plt.scatter(x_data, gr_df[i], s=1.2)
            plt.plot(x_data, gr_df[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
            #pylustrator.start()
            plt.show()



    def replot_SAVAR(self, csv):
        pass

class testing:

    def __init__(self):
        super(testing, self).__init__()


    def testplot(self, parent=None, width=5, height=4, dpi=100):
        print(csv, info, selected)
        folderpath = Path(csv)
        df = pd.read_csv(csv)
        # savefolder = self.create_plots_folder(folderpath)
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        x_data = df["S:M"]
        y_data = df["M:L"]
        print(x_data)

        # Clear figure
        self.figure.clear()

        # Plot the data
        plt.scatter(x_data, y_data, s=1.2)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlabel('S:M')
        plt.ylabel('M:L')
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)

        # Refresh canvas
        self.canvas.draw()



