import logging
import os
import time
from collections import namedtuple
from pathlib import Path

import numpy as np
import pandas as pd
from natsort import natsorted

logger = logging.getLogger("crystalaspects_Logger")


class Find:
    def __init__(self):
        self.method = 0

    def create_aspects_folder(self, path):
        """Creates crystalaspects folder"""
        time_string = time.strftime("%Y%m%d-%H%M%S")
        savefolder = Path(path) / "crystalaspects" / time_string
        savefolder.mkdir(parents=True, exist_ok=True)

        return savefolder

    def find_info(self, path):
        """The method returns the crystallographic directions,
        supersations, and the size_file paths from a CG simulation folder"""
        print(path)
        path = Path(path)
        files = os.listdir(path)
        contents = natsorted(files)
        folders = []
        summary_file = None
        growth_mod = None
        for item in contents:
            item_name = item
            item_path = path / item
            if item.startswith("._"):
                continue
            if item.endswith("summary.csv"):
                summary_file = item_path
            if os.path.isdir(item_path):
                if (
                    item_name.endswith("XYZ_files")
                    or item_name.endswith("crystalaspects")
                    or item_name.endswith("CrystalMaps")
                ):
                    continue
                else:
                    folders.append(item_path)
        size_files = []
        supersats = []
        directions = []
        file_info = namedtuple(
            "file_info",
            "supersats, size_files, directions, growth_mod, folders, summary_file",
        )

        i = 0
        for folder in folders:
            files = os.listdir(folder)
            for f in files:
                f_path = path / folder / f
                f_name = f

                if f_name.startswith("._"):
                    continue
                if f_name.endswith("size.csv"):
                    if os.stat(f_path).st_size == 0:
                        growth_rates = False
                    else:
                        size_files.append(f_path)
                        growth_rates = True

                    # directions = self.find_growth_directions(f_path)

                if f_name.endswith("simulation_parameters.txt"):
                    # print(f_path)
                    with open(f_path, "r", encoding="utf-8") as sim_file:
                        lines = sim_file.readlines()

                    for line in lines:
                        if line.startswith("Starting delta mu value (kcal/mol):"):
                            supersat = float(line.split()[-1])
                            supersats.append(supersat)
                        if line.startswith("normal, ordered or growth modifier"):
                            selected_mode = line.split("               ")[-1]
                            if selected_mode == "growth_modifier\n":
                                growth_mod = True
                            else:
                                growth_mod = False

                        if (
                            line.startswith("Size of crystal at frame output")
                            and i == 0
                        ):
                            frame = lines.index(line) + 1
                            # From starting point - read facet information
                            for n in range(frame, len(lines)):
                                line = lines[n]
                                if line == " \n":
                                    break
                                else:
                                    facet = line.split("      ")[0]
                                    if len(facet) <= 8:
                                        directions.append(facet)
            i += 1

        infomation = file_info(
            supersats, size_files, directions, growth_mod, folders, summary_file
        )

        return infomation

    def find_growth_directions(self, csv):
        """Returns the lenghts from a size_file"""
        lt_df = pd.read_csv(csv)
        columns = lt_df.columns
        directions = []
        for col in columns:
            if col.startswith(" "):
                directions.append(col)

        return directions

    def summary_compare(self, summary_csv, aspect_csv=False, aspect_df=""):
        summary_df = pd.read_csv(summary_csv)

        if aspect_csv:
            aspect_df = pd.read_csv(aspect_csv)

        summary_cols = summary_df.columns
        aspect_cols = aspect_df.columns

        try:
            """This allows the user to pick the two different
            summary file verions from CrystalGrower"""

            search = summary_df.iloc[0, 0]
            search = search.split("_")
            start_num = int(search[-1])
            search_string = "_".join(search[:-1])

            int_cols = summary_cols[1:]
            # print("Int cols", int_cols)
            summary_df = summary_df.set_index(summary_cols[0])
            compare_array = np.empty((0, len(aspect_cols) + len(int_cols)))
            # print("Compare array shape", compare_array.shape)

            for index, row in aspect_df.iterrows():
                sim_num = int(row["Simulation Number"]) - 1 + start_num
                num_string = f"{search_string}_{sim_num}"
                # print("num string", num_string)
                aspect_row = row.values
                aspect_row = np.array([aspect_row])
                collect_row = summary_df.filter(items=[num_string], axis=0).values
                """print(
                    f"Row from aspect file: {aspect_row}\nRow from summuary: {collect_row}"
                )"""
                collect_row = np.concatenate([aspect_row, collect_row], axis=1)
                compare_array = np.append(compare_array, collect_row, axis=0)
                # print(compare_array.shape)

        except AttributeError:
            int_cols = summary_cols[1:]
            compare_array = np.empty((0, len(aspect_cols) + len(int_cols)))

            for index, row in aspect_df.iterrows():
                sim_num = int(row["Simulation Number"] - 1)
                aspect_row = row.values
                aspect_row = np.array([aspect_row])
                # print(aspect_row)
                collect_row = [summary_df.iloc[sim_num].values[1:]]
                # print(collect_row)
                collect_row = np.concatenate([aspect_row, collect_row], axis=1)
                compare_array = np.append(compare_array, collect_row, axis=0)
                # print(compare_array.shape)

        # print(aspect_cols, int_cols)
        cols = aspect_cols.append(int_cols)
        # print(aspect_cols)
        # print(f"COLS:::: {cols}")
        compare_df = pd.DataFrame(compare_array, columns=cols)
        # print(compare_df)
        full_df = compare_df.sort_values(by=["Simulation Number"], ignore_index=True)
        # aspect_energy_csv = f"{savefolder}/crystalaspects.csv"
        # full_df.to_csv(aspect_energy_csv, index=None)

        # print(full_df)

        return full_df

    def combine_XYZ_CDA(self, CDA_df, XYZ_df):
        cda_cols = CDA_df.columns
        xyz_cols = XYZ_df.columns

        cda_cols = cda_cols[1:]

        combine_array = np.empty((0, len(xyz_cols) + len(cda_cols)))
        print(XYZ_df)

        for index, row in XYZ_df.iterrows():
            sim_num = int(row["Simulation Number"]) - 1
            print("sim_num", sim_num)
            xyz_row = row.values
            # print("xyz_row", xyz_row)
            xyz_row = np.array([xyz_row])
            # print(xyz_row)
            collect_row = [CDA_df.iloc[sim_num].values[1:]]
            print(collect_row)
            collect_row = np.concatenate([xyz_row, collect_row], axis=1)
            combine_array = np.append(combine_array, collect_row, axis=0)
            print(combine_array.shape)

        cols = xyz_cols.append(cda_cols)
        # print(aspect_cols)
        # print(f"COLS:::: {cols}")
        compare_df = pd.DataFrame(combine_array, columns=cols)
        # print(compare_df)
        combine_df = compare_df.sort_values(by=["Simulation Number"], ignore_index=True)
        """aspect_energy_csv = f"{savefolder}/crystalaspects.csv"
        full_df.to_csv(aspect_energy_csv, index=None)"""

        return combine_df
