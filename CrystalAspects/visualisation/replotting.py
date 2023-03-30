import numpy as np
import pandas as pd
from pathlib import Path

# PyQt imports
from PyQt5 import QtCore, QtWidgets

# Matplotlib import
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
import pylustrator
matplotlib.use('QT5Agg')

from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.visualisation.plot_data import Plotting


class Replotting:
    '''def __init__(self):
        pass'''

    def __init__(self):
        super(Replotting, self).__init__()

    def replot_AR(self, csv, info, selected):
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

        plt.figure()
        plt.scatter(x_data, y_data, s=1.2)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlabel('S:M')
        plt.ylabel('M:L')
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)
        #savepath = f'{folderpath}/PCA Zingg'
        #plt.show()

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
            pylustrator.start()
            #% start: automatic generated code from pylustrator
            plt.figure(3).ax_dict = {ax.get_label(): ax for ax in plt.figure(3).axes}
            import matplotlib as mpl
            getattr(plt.figure(3), '_pylustrator_init', lambda: ...)()
            plt.figure(3).axes[0].collections[0].set_edgecolor("#ff0000ff")
            #% end: automatic generated code from pylustrator
            plt.show()

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
            plt.show()
            pylustrator.start()


    def replot_SAVAR(self, csv):
        pass

'''class testing:

    def __init__(self):
        super(testing, self).__init__()


    def testplot(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # Create our pandas DataFrame with some simple
        # data and headers.
        x = np.linspace(-5, 5, 100)
        y = np.sin(x)
        print(x)

        # plot the pandas DataFrame, passing in the
        # matplotlib Canvas axes.
        #fig.clear()
        plt.plot(x, y)

        #self.setCentralWidget(sc)
        plt.show()'''