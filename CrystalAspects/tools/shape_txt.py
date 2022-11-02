from sklearn.decomposition import PCA
from scipy.spatial import ConvexHull
from pathlib import Path
import re
import numpy as np
import trimesh


def normalise_verts(verts, path="", write=False):

    centered = verts - np.mean(verts, axis=0)
    norm = np.linalg.norm(centered, axis=1).max()
    centered /= norm

    if write:
        xyz_path = Path(path)
        save_path = f"{xyz_path.parents[0]}/{xyz_path.stem}_norm.xyz"
        np.savetxt(
            save_path,
            centered,
            header=f"{centered.shape[0]}\n{xyz_path.stem} --> Normalised",
            comments=False,
        )

    return centered


def norm_out(path):
    path = Path(path)
    for xyz_file in path.rglob("*.XYZ"):
        xyz = read_XYZ(xyz_file)
        normalise_verts(xyz, path=xyz_file, write=True)


def get_PCA(xyz_vals, n=3):
    pca = PCA(n_components=n)
    pca.fit(normalise_verts(xyz_vals))

    # pca_vectors = pca.components_
    # pca_values = pca.explained_variance_ratio_
    pca_svalues = pca.singular_values_

    return pca_svalues


def get_SAVOL(self, xyz):
    hull = ConvexHull(xyz)
    vol_hull = hull.volume
    SA_hull = hull.area

    return (SA_hull, vol_hull)


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
    shape_class = "Unassigned"
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
                shape_class = "block"
            else:
                shape_class = "needle"
        if aspect1 <= 2 / 3:
            if aspect2 <= 2 / 3:
                shape_class = "plate"
            else:
                shape_class = "lath"

        surface_area, volume = get_SAVOL(xyz=xyz)

        with open(
            xyz_file.parents[0] / f"shape_{sim_num}.txt", "w", encoding="utf-6"
        ) as output:
            print(f"Simulation: {sim_num}-->{shape_class}\n")
            output.write(shape_class + "\n")
            output.write(f"S:M={aspect1}\nM:L={aspect2}\n")
            output.write(f"Surface_Area={surface_area}\nVolume={volume}\n")
            output.write(f"SA/Vol={surface_area/volume}")


create_shape_txt("path/to/simulation_directory")
