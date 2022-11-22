import numpy as np
import pandas as pd
from pathlib import Path

# Matplotlib import
import matplotlib.pyplot as plt

from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.visualisation.plot_data import Plotting


class Replotting:
    def __init__(self):
        pass

    def replot_AR(self, csv, info, selected):

        print(csv, info, selected)
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
            plt.scatter(x_data, gr_df[i], s=1.2)
            plt.plot(x_data, gr_df[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
        plt.savefig(savepath / "Growth_rates+Dissolution_rates", dpi=300)

    def replot_SAVAR(self, csv):
        pass
