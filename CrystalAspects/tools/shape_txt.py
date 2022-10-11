from sklearn.decomposition import PCA
from pathlib import Path
import re
import numpy as np
import trimesh


def normalise_verts(verts):

    centered = verts - np.mean(verts, axis=0)
    norm = np.linalg.norm(centered, axis=1).max()
    centered /= norm

    return centered


def get_PCA(xyz_vals, n=3):
    pca = PCA(n_components=n)
    pca.fit(normalise_verts(xyz_vals))

    # pca_vectors = pca.components_
    # pca_values = pca.explained_variance_ratio_
    pca_svalues = pca.singular_values_

    return pca_svalues


def read_XYZ(filepath):
    filepath = Path(filepath)
    print(filepath)
    xyz = None

    if filepath.suffix == ".XYZ":
        print("XYZ File read!")
        xyz = np.loadtxt(filepath, skiprows=2)[:, 3:]
    if filepath.suffix == ".txt":
        print("xyz File read!")
        xyz = np.loadtxt(filepath, skiprows=2)
    if filepath.suffix == ".stl":
        print("stl File read!")
        xyz = trimesh.load(filepath)

    return xyz


def create_shape_txt(path):
    folder_path = Path(path)
    shape_class = 'Unassigned'
    print(shape_class)

    for xyz_file in folder_path.rglob("*.XYZ"):

        sim_num = re.findall(r"\d+", Path(xyz_file).name)[-1]
        xyz = read_XYZ(xyz_file)
        pca_svalues = get_PCA(xyz_vals=xyz)
        small, medium, long = sorted(pca_svalues)
        aspect1 = small / medium
        aspect2 = medium / long

        if aspect1 >= 2 / 3:
            if aspect2 >= 2 / 3:
                shape_class = 'block'
            else:
                shape_class = 'needle'
        if aspect1 <= 2 / 3:
            if aspect2 <= 2 / 3:
                shape_class = 'plate'
            else:
                shape_class = 'lath'

        with open(xyz_file.parents[0] / f'shape_{sim_num}.txt', 'w') as output:
            print(f'Simulation: {sim_num}-->{shape_class}')
            output.write(shape_class)
            output.write(f'S:M={aspect1}\nM:L={aspect2}')


create_shape_txt('/Users/alvin/Library/CloudStorage/OneDrive-TheUniversityofManchester/Adipic_Acid/ADIPIC_testset')
