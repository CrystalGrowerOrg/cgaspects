import numpy as np
from pathlib import Path
import trimesh
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
import sys


class CrystalShape:
    def __init__(
        self,
    ):
        pass

    def normalise_verts(self, verts):
        """Normalises xyz crystal shape output through a
        transformation to unit lenghts and centering."""

        centered = verts - np.mean(verts, axis=0)
        norm = np.linalg.norm(centered, axis=1).max()
        centered /= norm

        return centered

    @staticmethod
    def read_XYZ(filepath, verbose=False, progress=True):
        """Read in shape data and generates a np arrary.
        Supported formats:
            .XYZ
            .txt (.xyz format)
            .stl
        """
        filepath = Path(filepath)
        print(filepath)
        xyz_movie = {}

        try:

            if filepath.suffix == ".XYZ":
                print("XYZ File read!")
                xyz = np.loadtxt(filepath, skiprows=2)
            if filepath.suffix == ".txt":
                print("xyz File read!")
                xyz = np.loadtxt(filepath, skiprows=2)
            if filepath.suffix == ".stl":
                print("stl File read!")
                xyz = trimesh.load(filepath)

            progress_num = 100

        except ValueError:
            print("Looking for Video")
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()
                num_frames = int(lines[1].split("//")[1])
                print(num_frames)

            if progress:
                toolbar_width = num_frames
                # setup toolbar
                sys.stdout.write("[%s]" % (" " * toolbar_width))
                sys.stdout.flush()
                sys.stdout.write(
                    "\b" * (toolbar_width + 1)
                )  # return to start of line, after '['

            particle_num_line = 0
            frame_line = 2
            for frame in range(num_frames):
                num_particles = int(lines[particle_num_line])
                xyz = np.loadtxt(lines[frame_line : (frame_line + num_particles)])
                xyz_movie[frame] = xyz
                particle_num_line = frame_line + num_particles
                frame_line = particle_num_line + 2

                progress_num = ((frame + 1) / num_frames) * 100

                if progress:
                    sys.stdout.write("#")
                    sys.stdout.flush()

                if verbose:
                    print(f"#####\nFRAME NUMBER: {frame}")
                    print(f"Particle Number Line: {particle_num_line}")
                    print(f"Frame Start Line: {frame_line}")
                    print(f"Frame End Line: {frame_line + num_particles}")
                    print(f"Number of Particles read: {frame_line}")

                    print(f"Number of Particles in list: {xyz.shape[0]}")
            sys.stdout.write("]\n")

        return (xyz, xyz_movie, progress_num)

    def get_PCA(self, xyz_vals, filetype=".XYZ", n=3):
        """Looks to obtain information on a crystal
        shape as the largest pricipal component is
        used as the longest length, second component
        the medium and the third the shortest"""

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

    def get_all(self, xyz_vals, n=3):
        """Returns both Aspect Ratio through PCA
        and Surface Area/Volume information on a
        crystal shape."""
        xyz_vals = xyz_vals[0:, 3:]
        print(xyz_vals)
        pca = PCA(n_components=n)
        pca.fit(xyz_vals)
        # pca_vectors = pca.components_
        # pca_values = pca.explained_variance_ratio_
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
