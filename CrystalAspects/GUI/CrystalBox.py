import numpy as np
import pandas as pd
from pathlib import Path
import re
import trimesh
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
import sys

def read_xyz_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()[2:]
        coordinates = []
        for line in lines:
            parts = line.split()
            coordinates.append([float(parts[3]), float(parts[4]), float(parts[5])])
    return np.array(coordinates)

def measure_crystal_size_xyz(coordinates):
    """OBA - (Orthogonal Box Analysis)
    Measuring the size of the crystal from
    the coordinates collected in read_xyz_file.
    This is measuring the size of the crystal
    based on the x, y and z directions
    """
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

    shape = determine_crystal_shape(aspect1, aspect2)      # Get Zingg definition of crystal
    print('call shape')
    print(shape)

    size_array = np.array([[length_x, length_y, length_z, aspect1, aspect2, shape]])

    return size_array

def determine_crystal_shape(aspect1, aspect2):
    """Creating the definition of the shape according
    to the Zingg diagram"""
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

def get_PCA(xyz_vals, filetype=".XYZ", n=3):
    """ PCA - (Principal Component analysis)
    Looks to obtain information on a crystal
    shape as the largest principal component is
    used as the longest length, second component
    the medium and the third the shortest"""
    pca = PCA(n_components=n)
    pca.fit(xyz_vals)
    pca_svalues = pca.singular_values_

    small, medium, long = sorted(pca_svalues)

    aspect1 = small / medium
    aspect2 = medium / long

    shape = determine_crystal_shape(aspect1, aspect2)      # Get Zingg definition of crystal

    pca_shape = np.array([[small, medium, long, aspect1, aspect2, shape]])

    return pca_shape

def get_savar(xyz_files):
    """Returns 3D data of a crystal shape,
    Volume:
    Surface Area:
    SA:Vol."""
    hull = ConvexHull(xyz_files)
    vol_hull = hull.volume
    SA_hull = hull.area
    sa_vol = SA_hull / vol_hull

    savar_array = np.array([[vol_hull, SA_hull, sa_vol]])

    return savar_array

def collect_all(folder, savefolder):
    """This collects all the CrystalAspects
    information from each of the relevant functions
    and congregates that into the final DataFrame"""
    print(folder)
    col_headings = ["Simulation Number",
                    "OBA Length X", "OBA Length Y", "OBA Length Z", "OBA S:M", "OBA M:L", "Shape Definition",
                    "PCA small", "PCA medium", "PCA long", "PCA S:M", "PCA M:L", "Shape Definition",
                    "Surface Area (SA)", "Volume (Vol)", "SA:Vol Ratio (SAVAR)"
                    ]
    shape_df = None
    for files in Path(folder).iterdir():
        if files.is_dir():
            for file in files.iterdir():
                # print(file)
                if file.suffix == ".XYZ":
                    sim_num = re.findall(r"\d+", file.name)[-1]
                    try:
                        xyz = read_xyz_file(file)                       # Read .XYZ file
                        pca_size = get_PCA(xyz)                         # Collect PCA data
                        crystal_size = measure_crystal_size_xyz(xyz)    # Collect OBA data
                        savar_size = get_savar(xyz)                     # Collect SAVAR data
                        sim_num_value = np.array([[sim_num]])           # Generate simulation number
                        size_data = np.concatenate((sim_num_value,
                                                    crystal_size,
                                                    pca_size,
                                                    savar_size
                                                    ),
                                                   axis=1)
                        col_nums = size_data.shape[1]
                        if shape_df is None:
                            shape_df = np.empty((0, col_nums),
                                                np.float64)
                        shape_df = np.append(shape_df, size_data, axis=0)
                        print(shape_df)

                    except (StopIteration, UnicodeDecodeError):
                        continue

    if len(shape_df) > 0:
        df = pd.DataFrame(
            shape_df,
            columns=col_headings
        )

        print(df)
        df.to_csv(savefolder + "CrystalAspects.csv", index=False)

collect_all(
    folder="/Users/Nathan/Documents/University/CrystalGrower/DaniMOF/1-5/20230506_132334/",
    savefolder="/Users/Nathan/Documents/University/CrystalGrower/DaniMOF/1-5/20230506_132334/CrystalAspects/",
)

