import numpy as np
import pandas as pd
import os
from natsort import natsorted
import re
from pathlib import Path
from CrystalAspects.tools.shape_analysis import CrystalShape as cs
from CrystalAspects.data.calc_data import Calculate as calc


class AspectRatio:
    def __init__(self):
        pass

    def create_aspects_folder(self, path):
        aspects_folder = Path(path) / 'CrystalAspects'
        aspects_folder.mkdir(parents=True, exist_ok=True)

        return aspects_folder
    

    def build_AR_PCA(self, subfolder):
        aspects_folder = self.create_aspects_folder(subfolder)

        final_array = np.empty((0, 6), np.float64)
        print(final_array.shape)

        for file in Path(subfolder).iterdir():
            if file.suffix == '.XYZ':

                sim_num = re.findall(r'\d+', Path(file).name)[-1]
                shape = cs()
                try:
                    xyz = shape.read_XYZ()
                    vals = shape.get_PCA(xyz)
                    # print(vals)

                    calculator = calc()
                    ar_data = calculator.aspectratio(pca_vals=vals)
                    ar_data = np.insert(ar_data, 0, sim_num, axis=1)

                    final_array = np.append(final_array, ar_data, axis=0)
                    print(final_array.shape)

                except StopIteration:
                    continue
                except UnicodeDecodeError:
                    continue

        print(final_array.shape)

        # Converting np array to pandas df
        df = pd.DataFrame(final_array, columns=['Simulation Number',
                                                'Small',
                                                'Medium',
                                                'Long',
                                                'S:M',
                                                'M:L'])
        aspects_folder = Path(subfolder) / 'CrystalAspects'
        aspect_csv = f'{aspects_folder}/PCA_aspectratio.csv'
        df.to_csv(aspect_csv)

        return df

    def build_AR_Crystallographic(self, file):
        filepath = Path(file)
        df = pd.read_csv(filepath)
        
        final_array = np.empty((0, 6), np.float64)
        print(final_array.shape)

        for index, row in df.iterrows():
            index =+ 1
            try:
                vals = row[1:4].values
                # print(vals)

                calculator = calc()
                ar_data = calculator.aspectratio(vals=vals)
                ar_data = np.insert(ar_data, 0, index, axis=1)

                final_array = np.append(final_array, ar_data, axis=0)
                print(final_array.shape)

            except StopIteration:
                continue
            except UnicodeDecodeError:
                continue

        print(final_array.shape)

        # Converting np array to pandas df
        df = pd.DataFrame(final_array, columns=['Simulation Number',
                                                'Small',
                                                'Medium',
                                                'Long',
                                                'S:M',
                                                'M:L'])
        aspects_folder = filepath.parents[0] / 'CrystalAspects'
        aspects_folder.mkdir(parents=True, exist_ok=True)
        aspect_csv = f'{aspects_folder}/PCA_aspectratio.csv'
        df.to_csv(aspect_csv)

        return df