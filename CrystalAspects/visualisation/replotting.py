import numpy as np
import pandas as pd
from pathlib import Path

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

    def replot_GrowthRate(self, csv):
        pass

    def replot_SAVAR(self, csv):
        pass
