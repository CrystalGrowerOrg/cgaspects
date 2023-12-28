import logging
import os
from itertools import permutations
from pathlib import Path
from statistics import median
import re


import numpy as np
import pandas as pd

from crystalaspects.utils.shape_analysis import CrystalShape

logger = logging.getLogger("crystalaspects_Logger")


class AspectRatio:
    def __init__(self):
        pass

    def build_AR_CDA(self, folders, folderpath, savefolder, directions, selected):
        path = Path(folderpath)
        print(directions)
        print("selected directions:")
        print(selected)

        # ar_array = np.empty((0, len(directions) + 1))
        ar_keys = ["Simulation Number"] + directions
        print("AR_keys", ar_keys)
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
                        try:
                            if line.startswith("Size of crystal at frame output"):
                                frame = lines.index(line) + 1
                                ar_dict["Simulation Number"].append(sim_num)
                        except NameError:
                            continue

                    len_info_lines = lines[frame:]
                    for len_line in len_info_lines:
                        for direction in directions:
                            if len_line.startswith(direction):
                                # print(direction, float(len_line.split(" ")[-2]))
                                ar_dict[direction].append(
                                    float(len_line.split(" ")[-2])
                                )
                                # print(ar_dict)

            sim_num += 1
        print("sim_num = ", sim_num)
        print("Order of Directions in Columns =", *directions)
        print("ar_dict", ar_dict)

        df = pd.DataFrame.from_dict(ar_dict)
        print("df", ar_dict)

        # aspect ratio calculation
        for i in range(len(selected) - 1):
            print(selected[i], selected[i + 1])
            df[f"AspectRatio_{selected[i]}/{selected[i+1]}"] = (
                df[selected[i]] / df[selected[i + 1]]
            )

        # df.to_csv(savefolder / "CDA_AspectRatio.csv", index=False)

        print(df)

        return df

    def CDA_Shape_Percentage(self, df, savefolder):
        shape_columns = ["OBA Shape", "PCA Shape"]
        cda_shape_data = []

        for shape_column in shape_columns:
            grouped = (
                df.groupby(["CDA_Equation", shape_column])
                .size()
                .reset_index(name="Count")
            )
            for cda_equation, group in grouped.groupby("CDA_Equation"):
                for shape, count in zip(group[shape_column], group["Count"]):
                    source = "OBA" if shape_column == "OBA Shape" else "PCA"
                    cda_shape_data.append(
                        {
                            "CDA_Equation": cda_equation,
                            "Shape": shape,
                            "Count": count,
                            "Source": source,
                        }
                    )

        cda_shape_df = pd.concat(
            [pd.DataFrame([data]) for data in cda_shape_data], ignore_index=True
        )
        cda_shape_df.sort_values("CDA_Equation", inplace=True)
        cda_shape_df.to_csv(f"{savefolder}/shapes and equations.csv")

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

        # ar_df.to_csv(Path(filepath) / "CDA_DataFrame.csv")

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
                        ddf.loc[idx, "Equation"] = eq_num
                    else:
                        # continue to next window
                        continue

        if csv != "":
            ddf.to_csv(csv.parents[0] / "CDA_Dataframe.csv")

        return ddf

    def shape_number_percentage(self, df, savefolder):
        """This section is calculating the number of times
        that lath, needle, plate and block and found in
        the columns OBA Shape Definition and PCA Shape
        Definition to create csv  that shows the percentage
        of each shape found"""
        OBA_shape_counts = df["OBA Shape"].str.lower().value_counts()
        OBA_total_count = OBA_shape_counts.sum()
        OBA_shape_percentages = OBA_shape_counts / OBA_total_count * 100

        PCA_shape_counts = df["PCA Shape"].str.lower().value_counts()
        PCA_total_count = PCA_shape_counts.sum()
        PCA_shape_percentages = PCA_shape_counts / PCA_total_count * 100

        result_df = pd.DataFrame(
            {
                "Shape": OBA_shape_counts.index,
                "OBA Count": OBA_shape_counts,
                "OBA Percentage": OBA_shape_percentages,
                "PCA Count": PCA_shape_counts,
                "PCA Percentage": PCA_shape_percentages,
            }
        )
        total_shapes_csv = f"{savefolder}/shape_counts.csv"
        result_df.to_csv(total_shapes_csv, index=False)

    def collect_all(self, folder):
        shape = CrystalShape()
        """This collects all the crystalaspects
        information from each of the relevant functions
        and congregates that into the final DataFrame"""
        col_headings = [
            "Simulation Number",
            "OBA Length X",
            "OBA Length Y",
            "OBA Length Z",
            "OBA S:M",
            "OBA M:L",
            "OBA Shape",
            "PCA small",
            "PCA medium",
            "PCA long",
            "PCA S:M",
            "PCA M:L",
            "PCA Shape",
            "Surface Area (SA)",
            "Volume (Vol)",
            "SA:Vol Ratio (SAVAR)",
        ]
        shape_df = None
        for files in Path(folder).iterdir():
            if files.is_dir():
                for file in files.iterdir():
                    if file.suffix == ".XYZ":
                        sim_num = re.findall(r"\d+", file.name)[-1]
                        try:
                            xyz = shape.read_XYZ(file)
                            pca_size = shape.get_pca(xyz)  
                            crystal_size = shape.get_oba(
                                xyz
                            )
                            # Collect SAVAR data
                            sa_vol_ratio_size = shape.get_sa_vol_ratio(xyz)
                            sim_num_value = np.array(
                                [[sim_num]]
                            )  # Generate simulation number
                            size_data = np.concatenate(
                                (sim_num_value, crystal_size, pca_size, sa_vol_ratio_size),
                                axis=1,
                            )
                            col_nums = size_data.shape[1]
                            if shape_df is None:
                                shape_df = np.empty((0, col_nums), np.float64)
                            shape_df = np.append(shape_df, size_data, axis=0)
                            # print(shape_df)

                        except (StopIteration, UnicodeDecodeError):
                            continue

        if len(shape_df) > 0:
            df = pd.DataFrame(shape_df, columns=col_headings)

            print(df)
            # df.to_csv(savefolder + "crystalaspects.csv", index=False)

        return df

