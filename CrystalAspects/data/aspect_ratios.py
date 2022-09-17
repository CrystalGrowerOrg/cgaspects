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

    def defining_equation(self, df=''):
        '''Defining CDA aspect ratio equations depending on the selected directions from the gui.
        This means we will also need to input the selected directions into the function'''
        a = ar_df[' 1  1  0']  # This is the first selected direction
        b = ar_df[' 1  0  0']  # This is the second selected direction
        c = ar_df[' 0  0  1']  # This is the third selected direction

        '''cda_aspect_ratio needs the insert of the directions that have been selected, creating a table for what number means what cda aspect ratio'''
        list_eq = [1, 2, 3, 4, 5, 6]
        CDA_aspect_ratio = ['[110]: [100]: [001]', '[001]: [100]: [110]', '[100]: [001]: [110] ', '[110]: [001]: [100]',
                            '[100]: [110]: [001]', '[001]: [110]: [100]']
        # CDA_aspect_ratio = [a:b:c, c:b:a, b:c:a, a:c:b, b:a:c, c:a:b]
        cda_equation = [list_eq, CDA_aspect_ratio]
        cda_equation_df = pd.DataFrame(cda_equation).transpose()
        cda_equation_df.columns = ['CDA Aspect Ratio Equation', 'CDA Aspect Ratio']
        cda_equation_df.to_csv(folderpath + 'CDA equations')

        pd.set_option('display.max_rows', None)
        ar_df.loc[(a <= b) & (b <= c), 'S/M'] = a / b
        ar_df.loc[(c <= b) & (b <= a), 'S/M'] = c / b
        ar_df.loc[(b <= c) & (c <= a), 'S/M'] = b / c
        ar_df.loc[(a <= c) & (c <= b), 'S/M'] = a / c
        ar_df.loc[(b <= a) & (a <= c), 'S/M'] = b / a
        ar_df.loc[(c <= a) & (a <= b), 'S/M'] = c / a
        print(ar_df['S/M'])

        ar_df.loc[(a <= b) & (b <= c), 'M/L'] = b / c
        ar_df.loc[(c <= b) & (b <= a), 'M/L'] = b / a
        ar_df.loc[(b <= c) & (c <= a), 'M/L'] = c / a
        ar_df.loc[(a <= c) & (c <= b), 'M/L'] = c / b
        ar_df.loc[(b <= a) & (a <= c), 'M/L'] = a / c
        ar_df.loc[(c <= a) & (a <= b), 'M/L'] = a / b
        print(ar_df['M/L'])

        ar_df.loc[(a <= b) & (b <= c), 'CDA Aspect Ratio Equation'] = '1'
        ar_df.loc[(c <= b) & (b <= a), 'CDA Aspect Ratio Equation'] = '2'
        ar_df.loc[(b <= c) & (c <= a), 'CDA Aspect Ratio Equation'] = '3'
        ar_df.loc[(a <= c) & (c <= b), 'CDA Aspect Ratio Equation'] = '4'
        ar_df.loc[(b <= a) & (a <= c), 'CDA Aspect Ratio Equation'] = '5'
        ar_df.loc[(c <= a) & (a <= b), 'CDA Aspect Ratio Equation'] = '6'
        print(ar_df['CDA Aspect Ratio Equation'])

        ar_df.to_csv(folderpath + 'CDA_DataFrame.csv')

        return ar_df

    def Zingg_CDA_shape_percentage(self, pca_df='', cda_df='', folderpath=''):
        '''This is analysing the pca and cda data creating a dataframe of crystal shapes and cda aspect ratio.
        The issue with this one is that it requires both the PCA and the CDA .csv's so I had to transpose them.'''
        pca_df = pd.read_csv(pca_df)
        cda_df = pd.read_csv(cda_df)
        pca_cda = [pca_df['S:M'], pca_df['M:L'], cda_df['S/M'], cda_df['M/L'], cda_df['CDA Aspect Ratio Equation']]
        pca_cda_df = pd.DataFrame(pca_cda).transpose()
        pca_cda_df.to_csv(folderpath + 'PCA_CDA.csv')
        cda = [1, 2, 3, 4, 5, 6]
        total = len(pca_cda_df)
        lath = pca_cda_df[(pca_cda_df['S:M'] <= 0.66) & (pca_cda_df['M:L'] <= 0.66)]
        plate = pca_cda_df[(pca_cda_df['S:M'] <= 0.66) & (pca_cda_df['M:L'] >= 0.66)]
        block = pca_cda_df[(pca_cda_df['S:M'] >= 0.66) & (pca_cda_df['M:L'] >= 0.66)]
        needle = pca_cda_df[(pca_cda_df['S:M'] >= 0.66) & (pca_cda_df['M:L'] <= 0.66)]
        total_lath = len(lath)
        total_plate = len(plate)
        total_block = len(block)
        total_needle = len(needle)
        lath_list = []
        plate_list = []
        block_list = []
        needle_list = []
        for i in cda:
            lath_list.append(len(lath[lath['CDA Aspect Ratio Equation'] == i]))
            plate_list.append(len(plate[plate['CDA Aspect Ratio Equation'] == i]))
            block_list.append(len(block[block['CDA Aspect Ratio Equation'] == i]))
            needle_list.append(len(needle[needle['CDA Aspect Ratio Equation'] == i]))
        total_list = [cda, lath_list, plate_list, block_list, needle_list]
        total_df = pd.DataFrame(total_list).transpose()
        total_df.columns = ['CDA Aspect Ratio Equation', 'Laths', 'Plates', 'Blocks', 'Needles']
        total_df.to_csv(folderpath + 'Total_Shapes_CDA.csv')
        lath_percentage = []
        plate_percentage = []
        block_percentage = []
        needle_percentage = []
        for i in lath_list:
            lath_percentage.append(i / total_lath * 100)
        for i in plate_list:
            plate_percentage.append(i / total_plate * 100)
        for i in block_list:
            block_percentage.append(i / total_block * 100)
        for i in needle_list:
            needle_percentage.append(i / total_needle * 100)
        percentage_list = [lath_percentage, plate_percentage, block_percentage, needle_percentage]
        percentage_df = pd.DataFrame(percentage_list).transpose()
        percentage_df.columns = ['Laths', 'Plates', 'Blocks', 'Needles']
        percentage_df.to_csv(folderpath + 'Percentage_Shapes_CDA.csv')

        return total_df, percentage_df

    def Zingg_No_Crystals(df, folderpath):
        '''analysis of the CDA data to output total and percentage of crystals
        This requires CDA .csv'''
        zn_df = pd.read_csv(df)
        eq1 = len(zn_df[zn_df['CDA Aspect Ratio Equation'] == 1])
        eq2 = len(zn_df[zn_df['CDA Aspect Ratio Equation'] == 2])
        eq3 = len(zn_df[zn_df['CDA Aspect Ratio Equation'] == 3])
        eq4 = len(zn_df[zn_df['CDA Aspect Ratio Equation'] == 4])
        eq5 = len(zn_df[zn_df['CDA Aspect Ratio Equation'] == 5])
        eq6 = len(zn_df[zn_df['CDA Aspect Ratio Equation'] == 6])

        CDA_total_crystals = eq1 + eq2 + eq3 + eq4 + eq5 + eq6

        total_CDA = [CDA_total_crystals, eq1, eq2, eq3, eq4, eq5, eq6]
        total_CDA_df = pd.DataFrame(total_CDA).transpose()
        total_CDA_df.columns = ['Total Crystals', 'eq1', 'eq2', 'eq3', 'eq4', 'eq5', 'eq6']
        total_CDA_df.to_csv(folderpath + 'Total Crystals CDA.csv')

        eq1_percentage = eq1 / CDA_total_crystals * 100
        eq2_percentage = eq2 / CDA_total_crystals * 100
        eq3_percentage = eq3 / CDA_total_crystals * 100
        eq4_percentage = eq4 / CDA_total_crystals * 100
        eq5_percentage = eq5 / CDA_total_crystals * 100
        eq6_percentage = eq6 / CDA_total_crystals * 100

        percentage_CDA = [eq1_percentage, eq2_percentage, eq3_percentage, eq4_percentage, eq5_percentage,
                          eq6_percentage]
        percentage_CDA_df = pd.DataFrame(percentage_CDA).transpose()
        percentage_CDA_df.columns = ['eq1', 'eq2', 'eq3', 'eq4', 'eq5', 'eq6']
        percentage_CDA_df.to_csv(folderpath + 'Percentage Crystals CDA.csv')

        return percentage_CDA_df

    def PCA_shape_percentage(self, df='', folderpath=''):
        '''Analysing the PCA data to output total and percentages of crystals
        This requires PCA .csv'''
        pca_df = pd.read_csv(df)
        colours = [1, 2, 3, 4, 5, 6]
        total = len(pca_df)
        lath = pca_df[(pca_df['S:M'] <= 0.66) & (pca_df['M:L'] <= 0.66)]
        plate = pca_df[(pca_df['S:M'] <= 0.66) & (pca_df['M:L'] >= 0.66)]
        block = pca_df[(pca_df['S:M'] >= 0.66) & (pca_df['M:L'] >= 0.66)]
        needle = pca_df[(pca_df['S:M'] >= 0.66) & (pca_df['M:L'] <= 0.66)]
        total_lath = len(lath)
        total_plate = len(plate)
        total_block = len(block)
        total_needle = len(needle)
        total_list = [total, total_lath, total_plate, total_block, total_needle]
        total_df = pd.DataFrame(total_list).transpose()
        total_df.columns = ['Number of Crystals', 'Laths', 'Plates', 'Blocks', 'Needles']
        total_df.to_csv(folderpath + 'Total_Shapes_PCA.csv')
        lath_percentage = total_lath / total * 100
        plate_percentage = total_plate / total * 100
        block_percentage = total_block / total * 100
        needle_percentage = total_needle / total * 100
        percentage_list = [lath_percentage, plate_percentage, block_percentage, needle_percentage]
        percentage_df = pd.DataFrame(percentage_list).transpose()
        percentage_df.columns = ['Laths', 'Plates', 'Blocks', 'Needles']
        percentage_df.to_csv(folderpath + 'Percentage_Shapes_PCA.csv')

        return percentage_df, total_df