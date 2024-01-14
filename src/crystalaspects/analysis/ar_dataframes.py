import logging
import os
import re
from itertools import permutations
from pathlib import Path
from statistics import median

import numpy as np
import pandas as pd

from crystalaspects.analysis.shape_analysis import CrystalShape
from crystalaspects.fileio.find_data import *

logger = logging.getLogger("CA:AR-Dataframes")


def build_cda(folders, folderpath, savefolder, directions, selected, singals=None):
    path = Path(folderpath)

    ar_keys = ["Simulation Number"] + directions
    logger.debug("AR_keys %s", ar_keys)
    ar_dict = {k: [] for k in ar_keys}
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
                            ar_dict[direction].append(float(len_line.split(" ")[-2]))
                            # print(ar_dict)

        sim_num += 1

    df = pd.DataFrame.from_dict(ar_dict)

    for i in range(len(selected) - 1):
        logger.debug("Aspect Ratio [%s] : [%s] / [%s]", i, selected[i], selected[i + 1])
        df[f"AspectRatio_{selected[i]}/{selected[i+1]}"] = (
            df[selected[i]] / df[selected[i + 1]]
        )

    logger.debug("CDA Dataframe:\n%s", ar_dict)

    return df


def get_cda_shape_percentage(df, savefolder):
    shape_columns = ["OBA Shape", "PCA Shape"]
    cda_shape_data = []

    for shape_column in shape_columns:
        grouped = (
            df.groupby(["CDA_Equation", shape_column]).size().reset_index(name="Count")
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
    cda_shape_df.to_csv(savefolder / "shapes_equations.csv")


def build_ratio_equations(directions, ar_df="", csv="", filepath="."):
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

    with open(Path(filepath) / "cda_equations.txt", "w") as outfile:
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

    return ar_df


def set_ratio_equations(directions, csv="", df=""):
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


def get_xyz_shape_percentage(df, savefolder):
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


def collect_all(folder, signals=None):
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

    # List for collecting data
    data_list = []
    # Iterate through each .XYZ file in the subdirectories of the given folder
    xyzs = Path(folder).rglob("*.XYZ")
    n_xyzs = len(list(xyzs))
    i = 1
    for file in Path(folder).rglob("*.XYZ"):
        sim_num = re.findall(r"\d+", file.name)[-1]
        try:
            shape.set_xyz(filepath=file)

            pca_size = shape.get_pca()
            small, medium, long = sorted(pca_size)
            aspect1 = small / medium
            aspect2 = medium / long
            pca_shape = shape.get_shape_class(aspect1=aspect1, aspect2=aspect2)
            pca_vals = np.asarray([[small, medium, long, aspect1, aspect2, pca_shape]])

            crystal_size = shape.get_oba()
            sa_vol_ratio_size = shape.get_sa_vol_ratio()
            sim_num_value = np.array([[sim_num]])
            size_data = np.concatenate(
                (sim_num_value, crystal_size, pca_vals, sa_vol_ratio_size), axis=1
            )
            data_list.append(size_data)
            if signals:
                signals.progress.emit(int((i / n_xyzs) * 100))
            i += 1
        except (StopIteration, UnicodeDecodeError):
            continue

    # Convert data to a DataFrame if not empty
    if data_list:
        shape_df = np.concatenate(data_list, axis=0)
        df = pd.DataFrame(shape_df, columns=col_headings)
        return df
    else:
        logger.warning(
            "Couldn't create Aspect Ratio Dataframe. Please check the XYZ files provided."
        )
