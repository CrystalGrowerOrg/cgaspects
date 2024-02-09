import logging
import time
from collections import namedtuple
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from natsort import natsorted
from PySide6.QtWidgets import QMessageBox

logger = logging.getLogger("CA:FileIO")


def file_empty(x):
    return x.stat().st_size == 0


def locate_xyz_files(xyz_folderpath):
    # Check if the folder selection was canceled or empty and handle appropriately
    if xyz_folderpath is None:
        logger.debug("Folder selection was canceled or no folder was selected.")
        return None

    xyz_folderpath = Path(xyz_folderpath)

    crystal_xyz_list = []

    try:
        if xyz_folderpath.is_dir():
            crystal_xyz_list = []

            for filepath in Path(xyz_folderpath).rglob("*.XYZ"):
                if file_empty(filepath):
                    logger.info("Ignore empty XYZ file: %s", filepath)
                else:
                    crystal_xyz_list.append(filepath)

            # Check if the list is empty
            if not crystal_xyz_list:
                raise FileNotFoundError(
                    "No .XYZ files found in the selected directory."
                )
        else:
            raise NotADirectoryError(f"{xyz_folderpath} is not a valid directory.")

        # Remove files that are not desired (e.g., ._DStore)
        crystal_xyz_list = [
            item for item in crystal_xyz_list if not Path(item).name.startswith("._")
        ]

        crystal_xyz_list = natsorted(crystal_xyz_list)

    except (FileNotFoundError, NotADirectoryError) as e:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(
            f"{e}\nPlease make sure the folder you have selected "
            "contains .XYZ files from the simulation(s)."
        )
        msg.setWindowTitle("Error! No XYZ files detected.")
        msg.exec()
        return None

    logger.debug("%s .XYZ Files Found", len(crystal_xyz_list))
    return crystal_xyz_list


def create_aspects_folder(path):
    """Creates crystalaspects folder"""
    time_string = time.strftime("%Y%m%d-%H%M%S")
    savefolder = Path(path) / "crystalaspects" / time_string
    savefolder.mkdir(parents=True, exist_ok=True)

    return savefolder


def find_info(path):
    """The method returns the crystallographic directions,
    supersations, and the size_file paths from a CG simulation folder"""
    logger.debug("find_info called at: %s", path)
    path = Path(path)
    contents = natsorted(path.iterdir())  # Directly sort the Path objects
    folders: List[Path] = []
    summary_file = None
    growth_mod = None

    for item_path in contents:
        if item_path.name.startswith("._"):
            continue
        if item_path.name.endswith("summary.csv"):
            summary_file = item_path
        if item_path.is_dir() and not any(
            item_path.name.endswith(suffix)
            for suffix in [
                "XYZ_files",
                "CrystalAspects",
                "CrystalMaps",
                "crystalaspects",
            ]
        ):
            folders.append(item_path)

    size_files = []
    supersats = []
    directions = []
    get_facets = True
    file_info = namedtuple(
        "file_info",
        "supersats, size_files, directions, growth_mod, folders, summary_file",
    )

    for folder in folders:
        for f_path in folder.iterdir():
            f_name = f_path.name
            if f_name.startswith("._"):
                continue
            if f_name.endswith("size.csv"):
                if f_path.stat().st_size != 0:
                    size_files.append(f_path)
                    growth_rates = True

            if f_name.endswith("simulation_parameters.txt"):
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

                    if line.startswith("Size of crystal") and get_facets:
                        frame = lines.index(line) + 1
                        # From starting point - read facet information
                        for n in range(frame, len(lines)):
                            line = lines[n]
                            if line in [" \n", "\n"]:
                                get_facets = False
                                break
                            else:
                                facet = line.split("      ")[0]
                                if len(facet) <= 8:
                                    directions.append(facet)

    information = file_info(
        supersats, size_files, directions, growth_mod, folders, summary_file
    )

    return information


def find_growth_directions(csv):
    """Returns the lenghts from a size_file"""
    lt_df = pd.read_csv(csv)
    columns = lt_df.columns
    directions = []
    for col in columns:
        if col.startswith(" "):
            directions.append(col)

    return directions


def summary_compare(summary_csv, aspect_csv=False, aspect_df=""):
    summary_df = pd.read_csv(summary_csv)

    if aspect_csv:
        aspect_df = pd.read_csv(aspect_csv)

    summary_cols = summary_df.columns
    aspect_cols = aspect_df.columns

    # This allows backcompatibility with
    # an older version of CrystalGrower

    search = str(summary_df.iloc[0, 0])
    search = search.split("_")
    start_num = int(search[-1])
    search_string = "_".join(search[:-1])

    int_cols = summary_cols[1:]
    summary_df = summary_df.set_index(summary_cols[0])
    compare_array = np.empty((0, len(aspect_cols) + len(int_cols)))

    for index, row in aspect_df.iterrows():
        sim_num = int(row["Simulation Number"]) - 1 + start_num
        num_string = f"{search_string}_{sim_num}"
        aspect_row = row.values
        aspect_row = np.array([aspect_row])
        collect_row = summary_df.filter(items=[num_string], axis=0).values
        collect_row = np.concatenate([aspect_row, collect_row], axis=1)
        compare_array = np.append(compare_array, collect_row, axis=0)

    cols = aspect_cols.append(int_cols)
    compare_df = pd.DataFrame(compare_array, columns=cols)
    full_df = compare_df.sort_values(by=["Simulation Number"], ignore_index=True)
    return full_df


def combine_xyz_cda(CDA_df, XYZ_df):
    cda_cols = CDA_df.columns[1:]
    xyz_cols = XYZ_df.columns

    logger.debug(
        "Attempting to combine CDA [%s] and XYZ [%s] dataframes",
        CDA_df.shape,
        XYZ_df.shape,
    )
    # Initialize a list to collect rows
    collected_rows = []
    combine_array = np.empty((0, len(xyz_cols) + len(cda_cols)))

    for index, row in XYZ_df.iterrows():
        sim_num = int(row["Simulation Number"]) - 1
        xyz_row = row.values
        xyz_row = np.array([xyz_row])
        cda_row = CDA_df.iloc[sim_num, 1:].values.reshape(1, -1)

        # Concatenate xyz_row with cda_row along axis 1 to form a combined row
        combined_row = np.concatenate([xyz_row, cda_row], axis=1)
        collected_rows.append(combined_row[0])

    # Convert the collected rows into a DataFrame
    combined_array = np.asarray(collected_rows)
    logger.debug("Combined array shape: %s", combined_array.shape)
    cols = xyz_cols.tolist() + cda_cols.tolist()
    logger.debug("Combined column titles: %s", cols)
    compare_df = pd.DataFrame(combined_array, columns=cols)
    combine_df = compare_df.sort_values(by=["Simulation Number"], ignore_index=True)

    logger.debug("Combined df:\n%s", combine_df)

    return combine_df
