import numpy as np
import pandas as pd
from pathlib import Path
from DataProcessor.tools.shape_analysis import CrystalShape as cs
from DataProcessor.data.calc_data import Calculate as calc


class Run:

    def __init__(self):
        self.method = 0

    def build_AR_PCA(self, subfolder):
        print(subfolder)
        for file in Path(subfolder).iterdir():
            # print(file)
            if not file.suffix == '.XYZ':
                continue

            shape = cs(10)
            vals = shape.get_PCA(file=file)
            # print(vals)

            calculator = calc()
            ar_data = calculator.aspectratio_pca(pca_vals=vals)
            print(ar_data)

    def build_AR_Crystallographic(self):
        pass

    def aspect_ratio_csv(self, folder, method=0):
        if method == 0:
            self.method = "PCA"
            print(self.method)
        if method == 1:
            self.method = "Crystallographic"

        if self.method == 'PCA':
            self.build_AR_PCA(folder)
        if self.method == 'Crystallographic':
            self.build_AR_Crystallographic(folder)

    def build_SPH_distance(self):
        print('something')

    def build_SAVAR(self):
        pass
