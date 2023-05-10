import numpy as np
import pandas as pd
import os
from itertools import permutations
from statistics import median
import re
import logging
from pathlib import Path
from CrystalAspects.tools.shape_analysis import CrystalShape as cs
from CrystalAspects.data.calc_data import Calculate as calc

from PyQt5.QtCore import QObject, pyqtSignal


logger = logging.getLogger("CrystalAspects_Logger")


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    progress
        int indicating % progress
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    message = pyqtSignal(str)


class AspectRatio:
    def __init__(self):
        self.signals = WorkerSignals()

    def create_aspects_folder(self, path):
        aspects_folder = Path(path) / "CrystalAspects"
        aspects_folder.mkdir(parents=True, exist_ok=True)

        return aspects_folder

    def build_AR_PCA(self, subfolder, savefolder):
        path = Path(subfolder)

        final_array = np.empty((0, 6), np.float64)
        i = 0
        for folder in path.iterdir():
            if folder.is_dir():
                for file in folder.iterdir():
                    print(folder)
                    if file.suffix == ".XYZ":
                        print(file)
                        sim_num = re.findall(r"\d+", Path(file).name)[-1]
                        shape = cs()
                        try:
                            xyz, _, _ = shape.read_XYZ(file)
                            vals = shape.get_PCA(xyz)

                            calculator = calc()
                            ar_data = calculator.aspectratio(vals=vals)
                            ar_data = np.insert(ar_data, 0, sim_num, axis=1)

                            final_array = np.append(final_array, ar_data, axis=0)
                            print(final_array.shape)

                        except StopIteration:
                            continue
                        except UnicodeDecodeError:
                            continue
            i += 1

        print(final_array.shape)

        # Converting np array to pandas df
        df = pd.DataFrame(
            final_array,
            columns=["Simulation Number", "Small", "Medium", "Long", "S:M", "M:L"],
        )
        df.to_csv(savefolder / "PCA_AspectRatio.csv", index=False)
        '''aspects_folder = Path(subfolder) / 'CrystalAspects'
        aspect_csv = f'{aspects_folder}/PCA_aspectratio.csv'
        df.to_csv(aspect_csv)'''

        return df

    def build_AR_CDA(self, folders, folderpath, savefolder, directions, selected):

        path = Path(folderpath)
        print(directions)
        print('selected directions:')
        print(selected)

        ar_array = np.empty((0, len(directions) + 1))
        ar_keys = ["Simulation Number"] + directions
        #print("AR_keys", ar_keys)
        ar_dict = {k: [] for k in ar_keys}
        print("ar_dict", ar_dict)
        sim_num = 1
        for folder in folders:
            files = os.listdir(folder)
            for f in files:
                f_path = path / folder / f
                f_name = f

                if f_name.startswith("._"):
                    continue
                if f_name.endswith("simulation_parameters.txt"):
                    with open(f_path, "r", encoding="utf-8") as sim_file:
                        lines = sim_file.readlines()

                    for line in lines:
                        if line.startswith("Size of crystal at frame output"):
                            frame = lines.index(line) + 1

                    ar_dict["Simulation Number"].append(sim_num)

                    len_info_lines = lines[frame:]
                    for len_line in len_info_lines:
                        for direction in directions:
                            if len_line.startswith(direction):
                                #print(direction, float(len_line.split(" ")[-2]))
                                ar_dict[direction].append(float(len_line.split(" ")[-2]))
                                #print(ar_dict)

            sim_num += 1

        print("Order of Directions in Columns =", *directions)
        #print("ar_dict", ar_dict)

        df = pd.DataFrame.from_dict(ar_dict)
        print("df", ar_dict)

        # aspect ratio calculation
        for i in range(len(selected) - 1):
            print(selected[i], selected[i + 1])
            df[f"AspectRatio_{selected[i]}/{selected[i+1]}"] = (
                df[selected[i]] / df[selected[i + 1]]
            )

        df.to_csv(savefolder / "CDA_AspectRatio.csv", index=False)

        print(df)

        return df

    def savar_calc(self, subfolder, savefolder):
        path = Path(subfolder)

        sav_final_df = np.empty((0, 4), np.float64)

        for files in path.iterdir():
            if files.is_dir():
                for file in files.iterdir():
                    if file.suffix == ".XYZ":
                        sim_num = re.findall(r"\d+", Path(file).name)[-1]
                        shape = cs()
                        try:
                            xyz, _, _ = shape.read_XYZ(file)
                            sav_data = shape.get_savar(xyz)
                            sav_data = np.insert(sav_data, 0, sim_num, axis=1)
                            sav_final_df = np.append(sav_final_df, sav_data, axis=0)
                        except (StopIteration, UnicodeDecodeError):
                            continue

        print(sav_final_df.shape)

        # Converting np array to pandas df
        df = pd.DataFrame(
            sav_final_df,
            columns=[
                "Simulation Number",
                "Volume (Vol)",
                "Surface_Area (SA)",
                "SA:Vol",
            ],
        )
        df.to_csv(savefolder / "SA_Vol_ratio.csv", index=False)

        return df

    def shape_all(self, subfolder, savefolder):

        shape_final_df = np.empty((0, 6), np.float64)

        for files in Path(subfolder).iterdir():
            if files.is_dir():
                for file in files.iterdir():
                    if file.suffix == ".XYZ":
                        sim_num = re.findall(r"\d+", Path(file).name)[-1]
                        shape = cs()
                        try:
                            xyz, _, _ = shape.read_XYZ(file)
                            shape_data = shape.get_all(xyz)
                            print(shape_data)
                            shape_data = np.insert(shape_data, 0, sim_num, axis=1)
                            print(shape_data)
                            shape_final_df = np.append(
                                shape_final_df, shape_data, axis=0
                            )
                            print(shape_final_df.shape)
                        except (StopIteration, UnicodeDecodeError):
                            continue

        # Converting np array to pandas df
        df = pd.DataFrame(
            shape_final_df,
            columns=[
                "Simulation Number",
                "S:M",
                "M:L",
                "Surface_Area (SA)",
                "Volume (Vol)",
                "SA:Vol",
            ],
        )
        print(df)
        df.to_csv(savefolder / "Shape Properties.csv", index=False)

        return df

    def defining_equation(self, directions, ar_df="", csv="", filepath="."):
        """Defining CDA aspect ratio equations depending on the selected directions from the gui.
        This means we will also need to input the selected directions into the function.

        EQ:     a b c
                a c b
                b a c
                b c a
                c a b
                c b a
        """

        equations = [combo for combo in permutations(directions)]

        if csv != "":
            csv = Path(csv)
            ar_df = pd.read_csv(csv)

        a_name = directions[0]
        b_name = directions[1]
        c_name = directions[2]

        a = ar_df[a_name]
        b = ar_df[b_name]
        c = ar_df[c_name]

        with open(Path(filepath) / "CDA_equations.txt", "w") as outfile:
            for i, line in enumerate(equations):
                outfile.writelines(f"Equation Number{i+1}: {line}\n")

        pd.set_option("display.max_rows", None)
        ar_df.loc[(a <= b) & (b <= c), "S/M"] = a / b
        ar_df.loc[(a <= c) & (c <= b), "S/M"] = a / c
        ar_df.loc[(b <= a) & (a <= c), "S/M"] = b / a
        ar_df.loc[(b <= c) & (c <= a), "S/M"] = b / c
        ar_df.loc[(c <= a) & (a <= b), "S/M"] = c / a
        ar_df.loc[(c <= b) & (b <= a), "S/M"] = c / b

        ar_df.loc[(a <= b) & (b <= c), "M/L"] = b / c
        ar_df.loc[(a <= c) & (c <= b), "M/L"] = c / b
        ar_df.loc[(b <= a) & (a <= c), "M/L"] = a / c
        ar_df.loc[(b <= c) & (c <= a), "M/L"] = c / a
        ar_df.loc[(c <= a) & (a <= b), "M/L"] = a / b
        ar_df.loc[(c <= b) & (b <= a), "M/L"] = b / a

        ar_df.loc[(a <= b) & (b <= c), "CDA_Equation"] = "1"
        ar_df.loc[(a <= c) & (c <= b), "CDA_Equation"] = "2"
        ar_df.loc[(b <= a) & (a <= c), "CDA_Equation"] = "3"
        ar_df.loc[(b <= c) & (c <= a), "CDA_Equation"] = "4"
        ar_df.loc[(c <= a) & (a <= b), "CDA_Equation"] = "5"
        ar_df.loc[(c <= b) & (b <= a), "CDA_Equation"] = "6"

        ar_df.to_csv(Path(filepath) / "CDA_DataFrame.csv")

        return ar_df

    def define_equations(self, directions, csv="", df=""):

        equations = [combo for combo in permutations(directions)]

        if csv != "":
            csv = Path(csv)
            df = pd.read_csv(csv)

        window_size = len(directions)

        ddf = df.iloc[:, 1:]

        for idx, row in ddf.iterrows():
            row = row.sort_values()
            sorted_row = row.keys()
            n = len(sorted_row)

            # find index of direction closest
            # to the median (in an ordered list)
            med = median(row)
            array = np.asarray(row)
            med_idx = (np.abs(array - med)).argmin()

            for eq_num, eq in enumerate(equations):  # Gets equation order
                for i in range(n - window_size + 1):
                    window = list(sorted_row[i : i + window_size])
                    if list(eq) == window:
                        print("match")

                        # df.loc[idx, f'S/M {eq[0]}/{eq[med_idx]}'] = \
                        #    row[i]/row[med_idx]
                        # df.loc[idx, f'S/M {eq[med_idx]}/{eq[-1]}'] = \
                        #    row[med_idx]/row[-1]
                        df.loc[idx, "Equation"] = eq_num
                    else:
                        # continue to next window
                        continue

        if csv != "":
            df.to_csv(csv.parents[0] / "CDA_Dataframe.csv")

        return df

    def Zingg_CDA_shape_percentage(
        self, pca_df="", cda_df="", pca_csv="", cda_csv="", folderpath="."
    ):
        """This is analysing the pca and cda data creating a dataframe of crystal shapes and cda aspect ratio.
        The issue with this one is that it requires both the PCA and the CDA .csv's so I had to transpose them."""

        if pca_csv != "":
            pca_csv = Path(pca_csv)
            pca_df = pd.read_csv(pca_csv)
        if cda_csv != "":
            cda_df = Path(cda_df)
            cda_df = pd.read_csv(cda_df)

        pca_df.sort_values(by=["Simulation Number"], inplace=True)
        pca_cda = [
            pca_df["S:M"],
            pca_df["M:L"],
            cda_df["S/M"],
            cda_df["M/L"],
            cda_df["CDA_Equation"],
        ]
        pca_cda_df = pd.DataFrame(pca_cda).transpose()
        pca_cda_df.to_csv(Path(folderpath) / "PCA_CDA.csv")

        cda = set(cda_df["CDA_Equation"])

        total = len(pca_cda_df)
        lath = pca_cda_df[(pca_cda_df["S:M"] <= 0.667) & (pca_cda_df["M:L"] <= 0.667)]
        plate = pca_cda_df[(pca_cda_df["S:M"] <= 0.667) & (pca_cda_df["M:L"] >= 0.667)]
        block = pca_cda_df[(pca_cda_df["S:M"] >= 0.667) & (pca_cda_df["M:L"] >= 0.667)]
        needle = pca_cda_df[(pca_cda_df["S:M"] >= 0.667) & (pca_cda_df["M:L"] <= 0.667)]
        total_lath = len(lath)
        total_plate = len(plate)
        total_block = len(block)
        total_needle = len(needle)
        lath_list = []
        plate_list = []
        block_list = []
        needle_list = []
        for i in cda:
            lath_list.append(len(lath[lath["CDA_Equation"] == i]))
            plate_list.append(len(plate[plate["CDA_Equation"] == i]))
            block_list.append(len(block[block["CDA_Equation"] == i]))
            needle_list.append(len(needle[needle["CDA_Equation"] == i]))
        total_list = [cda, lath_list, plate_list, block_list, needle_list]
        total_df = pd.DataFrame(total_list).transpose()
        total_df.columns = ["CDA_Equation", "Laths", "Plates", "Blocks", "Needles"]
        total_df.to_csv(Path(folderpath) / "Total_Shapes_CDA.csv")
        lath_percentage = []
        plate_percentage = []
        block_percentage = []
        needle_percentage = []
        for i in lath_list:
            try:
                lath_percentage.append(i / total_lath * 100)
            except ZeroDivisionError:
                lath_percentage.append(0)
        for i in plate_list:
            try:
                plate_percentage.append(i / total_plate * 100)
            except ZeroDivisionError:
                plate_percentage.append(0)
        for i in block_list:
            try:
                block_percentage.append(i / total_block * 100)
            except ZeroDivisionError:
                block_percentage.append(0)
        for i in needle_list:
            try:
                needle_percentage.append(i / total_needle * 100)
            except ZeroDivisionError:
                needle_percentage.append(0)

        percentage_list = [
            lath_percentage,
            plate_percentage,
            block_percentage,
            needle_percentage,
        ]
        percentage_df = pd.DataFrame(percentage_list).transpose()

        print(percentage_df)

        percentage_df.columns = ["Laths", "Plates", "Blocks", "Needles"]
        percentage_df.to_csv(Path(folderpath) / "Percentage_Shapes_CDA.csv")

        return pca_cda_df

    def Zingg_No_Crystals(self, zn_df="", csv="", folderpath="."):
        """analysis of the CDA data to output total and percentage of crystals
        This requires CDA .csv"""
        if csv != "":
            csv = Path(csv)
            zn_df = pd.read_csv(csv)
        print(zn_df)
        print(zn_df["CDA_Equation"])
        eq1 = len(zn_df[zn_df["CDA_Equation"] == 1])
        eq2 = len(zn_df[zn_df["CDA_Equation"] == 2])
        eq3 = len(zn_df[zn_df["CDA_Equation"] == 3])
        eq4 = len(zn_df[zn_df["CDA_Equation"] == 4])
        eq5 = len(zn_df[zn_df["CDA_Equation"] == 5])
        eq6 = len(zn_df[zn_df["CDA_Equation"] == 6])

        CDA_total_crystals = len(zn_df["CDA_Equation"])
        print(CDA_total_crystals)

        total_CDA = [CDA_total_crystals, eq1, eq2, eq3, eq4, eq5, eq6]
        total_CDA_df = pd.DataFrame(total_CDA).transpose()
        total_CDA_df.columns = [
            "Total Crystals",
            "eq1",
            "eq2",
            "eq3",
            "eq4",
            "eq5",
            "eq6",
        ]
        total_CDA_df.to_csv(Path(folderpath) / "Total Crystals CDA.csv")

        if eq1 == 0:
            eq1_percentage = 0
        else:
            eq1_percentage = eq1 / CDA_total_crystals * 100

        if eq2 == 0:
            eq2_percentage = 0
        else:
            eq2_percentage = eq2 / CDA_total_crystals * 100

        if eq3 == 0:
            eq3_percentage = 0
        else:
            eq3_percentage = eq3 / CDA_total_crystals * 100

        if eq4 == 0:
            eq4_percentage = 0
        else:
            eq4_percentage = eq4 / CDA_total_crystals * 100

        if eq5 == 0:
            eq5_percentage = 0
        else:
            eq5_percentage = eq5 / CDA_total_crystals * 100

        if eq6 == 0:
            eq6_percentage = 0
        else:
            eq6_percentage = eq6 / CDA_total_crystals * 100

        percentage_CDA = [
            eq1_percentage,
            eq2_percentage,
            eq3_percentage,
            eq4_percentage,
            eq5_percentage,
            eq6_percentage,
        ]
        percentage_CDA_df = pd.DataFrame(percentage_CDA).transpose()
        percentage_CDA_df.columns = ["eq1", "eq2", "eq3", "eq4", "eq5", "eq6"]
        percentage_CDA_df.to_csv(Path(folderpath) / "Percentage Crystals CDA.csv")

        return percentage_CDA_df

    def PCA_shape_percentage(self, pca_df="", csv="", folderpath="."):
        """Analysing the PCA data to output total and percentages of crystals
        This requires PCA .csv"""
        # pca_df = pd.read_csv(df)
        # colours = [1, 2, 3, 4, 5, 6]
        if csv != "":
            csv = Path(csv)
            pca_df = pd.read_csv(csv)

        total = len(pca_df)
        lath = pca_df[(pca_df["S:M"] <= 0.667) & (pca_df["M:L"] <= 0.667)]
        plate = pca_df[(pca_df["S:M"] <= 0.667) & (pca_df["M:L"] >= 0.667)]
        block = pca_df[(pca_df["S:M"] >= 0.667) & (pca_df["M:L"] >= 0.667)]
        needle = pca_df[(pca_df["S:M"] >= 0.667) & (pca_df["M:L"] <= 0.667)]
        total_lath = len(lath)
        total_plate = len(plate)
        total_block = len(block)
        total_needle = len(needle)
        total_list = [total, total_lath, total_plate, total_block, total_needle]
        total_df = pd.DataFrame(total_list).transpose()
        total_df.columns = [
            "Number of Crystals",
            "Laths",
            "Plates",
            "Blocks",
            "Needles",
        ]
        total_df.to_csv(Path(folderpath) / "Total_Shapes_PCA.csv")

        try:
            lath_percentage = total_lath / total * 100
        except ZeroDivisionError:
            lath_percentage = 0

        try:
            plate_percentage = total_plate / total * 100
        except ZeroDivisionError:
            plate_percentage = 0

        try:
            block_percentage = total_block / total * 100
        except ZeroDivisionError:
            block_percentage = 0

        try:
            needle_percentage = total_needle / total * 100
        except ZeroDivisionError:
            needle_percentage = 0

        percentage_list = [
            lath_percentage,
            plate_percentage,
            block_percentage,
            needle_percentage,
        ]
        percentage_df = pd.DataFrame(percentage_list).transpose()
        percentage_df.columns = ["Laths", "Plates", "Blocks", "Needles"]
        percentage_df.to_csv(Path(folderpath) / "Percentage_Shapes_PCA.csv")

        return percentage_df, total_df
