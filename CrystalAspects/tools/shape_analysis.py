import numpy as np
from pathlib import Path
import trimesh
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA


class CrystalShape:
    def __init__(
        self,
    ):
        pass

    def normalise_verts(self, verts):

        self.centered = verts - np.mean(verts, axis=0)
        norm = np.linalg.norm(self.centered, axis=1).max()
        self.centered /= norm

        return self.centered

    def read_XYZ(self, filepath):
        filepath = Path(filepath)
        print(filepath)

        if filepath.suffix == ".XYZ":
            print("XYZ File read!")
            self.xyz = np.loadtxt(filepath, skiprows=2)[:, 3:]
        if filepath.suffix == ".txt":
            print("xyz File read!")
            self.xyz = np.loadtxt(filepath, skiprows=2)
        if filepath.suffix == ".stl":
            print("stl File read!")
            self.xyz = trimesh.load(filepath)

        return self.xyz

    def get_PCA(self, xyz_vals, filetype=".XYZ", n=3):
        pca = PCA(n_components=n)

        if filetype == ".XYZ" or ".xyz":
            pca.fit(self.normalise_verts(xyz_vals))

        # pca_vectors = pca.components_
        # pca_values = pca.explained_variance_ratio_
        pca_svalues = pca.singular_values_

        # print(pca_vectors)
        # print(pca_values)
        # print(pca_svalues)s

        return pca_svalues

    def get_savar(self, xyz_files):
        hull = ConvexHull(xyz_files)
        vol_hull = hull.volume
        SA_hull = hull.area
        sa_vol = SA_hull / vol_hull

        savar_array = np.array([[vol_hull, SA_hull, sa_vol]])

        return savar_array

    def get_all(self, xyz_vals, n=3):

        pca = PCA(n_components=n)
        pca.fit(xyz_vals)
        pca_vectors = pca.components_
        pca_values = pca.explained_variance_ratio_
        pca_svalues = pca.singular_values_

        hull = ConvexHull(xyz_vals)
        vol_hull = hull.volume
        SA_hull = hull.area
        sa_vol = SA_hull / vol_hull

        small, medium, long = sorted(pca_svalues)

        aspect1 = small / medium
        aspect2 = medium / long

        shape_info = np.array([[aspect1, aspect2, SA_hull, vol_hull, sa_vol]])

        return shape_info
