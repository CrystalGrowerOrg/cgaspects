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

def calculate_lattice_vectors(a, b, c, alpha, beta, gamma):
    alpha_rad = np.deg2rad(alpha)
    beta_rad = np.deg2rad(beta)
    gamma_rad = np.deg2rad(gamma)

    a1 = np.array([a, 0, 0])
    a2 = np.array([b * np.cos(gamma_rad), b * np.sin(gamma_rad), 0])
    a3 = np.array([c * np.cos(beta_rad),
                   c * (np.cos(alpha_rad) - np.cos(beta_rad) * np.cos(gamma_rad)) / np.sin(gamma_rad),
                   c * np.sqrt(1 + 2 * np.cos(alpha_rad) * np.cos(beta_rad) * np.cos(gamma_rad)
                               - np.cos(alpha_rad) ** 2 - np.cos(beta_rad) ** 2 - np.cos(gamma_rad) ** 2)
                   / np.sin(gamma_rad)])
    print(a1, a2, a3)

    return a1, a2, a3

def convert_frac_to_cartesian(coordinates, a1, a2, a3):
    cartesian_coords = np.dot(coordinates, np.vstack((a1, a2, a3)))
    print(cartesian_coords)

    return cartesian_coords


def measure_facet_distances(coordinates):
    # Calculate distances between specific facets
    # Add your specific calculations here based on the crystal structure and orientation
    distances = []

    return np.array(distances)

def collect_Box(folder, savefolder):
    shape_box_df = np.empty((0, 6), np.float64)
    print(folder)
    for files in Path(folder).iterdir():
        if files.is_dir():
            for file in files.iterdir():
                print(file)
                if file.suffix == ".XYZ":
                    sim_num = re.findall(r"\d+", file.name)[-1]
                    try:
                        xyz = read_xyz_file(file)
                        facet_distances = measure_facet_distances(xyz)
                        size_data = np.hstack(([sim_num], facet_distances))
                        shape_box_df = np.vstack((shape_box_df, size_data))
                        print(len(shape_box_df))
                    except (StopIteration, UnicodeDecodeError):
                        continue
                    except UnicodeDecodeError:
                        continue

    if len(shape_box_df) > 0:
        df = pd.DataFrame(
            shape_box_df,
            columns=["Simulation Number", "Distance_1", "Distance_2", "Distance_3"],
        )
        print(df)
        df.to_csv(savefolder + "Facet Distances.csv", index=False)
    else:
        print("No valid files found in the folder.")

collect_Box(
    folder="/Users/Nathan/Documents/University/CrystalGrower/DaniMOF/1-5/20230506_132334/",
    savefolder="/Users/Nathan/Documents/University/CrystalGrower/DaniMOF/1-5/20230506_132334/CrystalAspects/",
    a=32.2880, b=6.7989, c=16.7932, alpha=90.0, beta=90.0, gamma=90.0
)
