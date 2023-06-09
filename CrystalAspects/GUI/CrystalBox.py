import numpy as np
import pandas as pd
from pathlib import Path
import re

def read_xyz_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()[2:]
        coordinates = []
        for line in lines:
            parts = line.split()
            coordinates.append([float(parts[3]), float(parts[4]), float(parts[5])])
    return np.array(coordinates)

def measure_crystal_size(coordinates):
    min_coords = np.min(coordinates, axis=0)
    print(min_coords)
    max_coords = np.max(coordinates, axis=0)
    box_size = max_coords - min_coords
    small_dist = np.min(box_size)
    medium_dist = np.median(box_size)
    long_dist = np.max(box_size)

    aspect1 = small_dist / medium_dist
    aspect2 = medium_dist / long_dist

    size_array = np.array([[aspect1, aspect2]])

    return size_array

def collect_Box(folder, savefolder):
    shape_box_df = np.empty((0, 3), np.float64)
    print(folder)
    for files in Path(folder).iterdir():
        #print(files)
        if files.is_dir():
            #print(files)
            for file in files.iterdir():
                print(file)
                if file.suffix == ".XYZ":
                    sim_num = re.findall(r"\d+", file.name)[-1]
                    try:
                        xyz = read_xyz_file(file)
                        crystal_size = measure_crystal_size(xyz)
                        print(crystal_size)
                        size_data = np.insert(crystal_size, 0, sim_num, axis=1)
                        print(size_data)
                        shape_box_df = np.append(
                            shape_box_df, size_data, axis=0
                        )
                        print(len(shape_box_df))
                    except (StopIteration, UnicodeDecodeError):
                        continue

    if len(shape_box_df) > 0:
        df = pd.DataFrame(
            shape_box_df,
            columns=["Simulation Number", "Box S:M", "Box M:L"],
        )
        print(df)
        df.to_csv(savefolder + "Box Measurements.csv", index=False)
    else:
        print("No valid files found in the folder.")

collect_Box(
    folder="/Users/student/Downloads/DaniMOF/Testing/20230307_221958/",
    savefolder="/Users/student/Downloads/DaniMOF/Testing/20230307_221958/CrystalAspects/Box Test/",
)
