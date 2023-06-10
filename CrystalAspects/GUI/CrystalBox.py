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

def measure_crystal_size_xyz(coordinates):
    min_x = np.min(coordinates[:, 0])
    max_x = np.max(coordinates[:, 0])
    length_x = max_x - min_x
    min_y = np.min(coordinates[:, 1])
    max_y = np.max(coordinates[:, 1])
    length_y = max_y - min_y
    min_z = np.min(coordinates[:, 2])
    max_z = np.max(coordinates[:, 2])
    length_z = max_z - min_z

    lengths = [length_x, length_y, length_z]
    lengths.sort()  # Sort the lengths in ascending order

    # Determine the smallest, middle, and longest lengths
    smallest = lengths[0]
    middle = lengths[1]
    longest = lengths[2]

    aspect1 = smallest / middle
    aspect2 = middle / longest

    shape = determine_crystal_shape(aspect1, aspect2)
    print('call shape')
    print(shape)

    size_array = np.array([[length_x, length_y, length_z, aspect1, aspect2, shape]])

    return size_array

def determine_crystal_shape(aspect1, aspect2):
    print("entering determine crystal shape")
    if aspect1 <= 0.667 and aspect2 <= 0.667:
        return "Lath"
    elif aspect1 <= 0.667 and aspect2 >= 0.667:
        return "Plate"
    elif aspect1 >= 0.667 and aspect2 >= 0.667:
        return "Block"
    elif aspect1 >= 0.667 and aspect2 <= 0.667:
        return "Needle"
    else:
        return "unknown"

def collect_Box(folder, savefolder):
    shape_box_df = np.empty((0, 7), np.float64)
    print(folder)
    for files in Path(folder).iterdir():
        if files.is_dir():
            for file in files.iterdir():
                print(file)
                if file.suffix == ".XYZ":
                    sim_num = re.findall(r"\d+", file.name)[-1]
                    try:
                        xyz = read_xyz_file(file)
                        crystal_size = measure_crystal_size_xyz(xyz)
                        print(crystal_size)
                        size_data = np.insert(crystal_size, 0, sim_num, axis=1)
                        print(size_data)
                        shape_box_df = np.append(
                            shape_box_df, size_data, axis=0
                        )
                        print(len(shape_box_df))
                    except (StopIteration, UnicodeDecodeError):
                        continue
                    except UnicodeDecodeError:
                        continue

    if len(shape_box_df) > 0:
        df = pd.DataFrame(
            shape_box_df,
            columns=["Simulation Number", "Length X", "Length Y", "Length Z", "Box S:M", "Box M:L", "Shape Definition"],
        )
        print(df)
        df.to_csv(savefolder + "Box Measurements.csv", index=False)
    else:
        print("No valid files found in the folder.")

collect_Box(
    folder="/Users/Nathan/Documents/University/CrystalGrower/DaniMOF/1-5/20230506_132334/",
    savefolder="/Users/Nathan/Documents/University/CrystalGrower/DaniMOF/1-5/20230506_132334/CrystalAspects/",
)
