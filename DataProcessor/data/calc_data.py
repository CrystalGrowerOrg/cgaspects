import numpy as np
import pandas as pd
from DataProcessor.tools.shape_analysis import CrystalShape as cs


class Calculate:

    def __init__(self):
        pass

    def aspectratio_crystallographic(self):
        pass

    def aspectratio_pca(self, pca_vals):
        self.long, self.medium, self.small = (sorted(pca_vals))
        
        self.aspect1 = self.small / self.medium
        self.aspect2 = self.medium / self.long

        return [self.long, self.medium, self.small, self.aspect1, self.aspect2]
