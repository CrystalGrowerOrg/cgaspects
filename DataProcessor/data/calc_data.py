import numpy as np
import pandas as pd
from DataProcessor.tools.shape_analysis import CrystalShape as cs


class Calculate:

    def __init__(self):
        pass

    def aspectratio_crystallographic(self):
        pass

    def aspectratio_pca(self, pca_vals):
        self.small, self.medium, self.long = (sorted(pca_vals))
        
        self.aspect1 = self.small / self.medium
        self.aspect2 = self.medium / self.long

        aspect_array = np.array([[self.small,
                                self.medium,
                                self.long,
                                self.aspect1,
                                self.aspect2]])
        
        return aspect_array
