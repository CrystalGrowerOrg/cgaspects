import re
import sys
from pathlib import Path
import logging
from collections import namedtuple

import numpy as np
import pandas as pd
import trimesh
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA

logger = logging.getLogger("CA:ShapeAnalysis")

class CrystalShape:
    def __init__(
        self,
    ):
        pass

    def get_shape_class(self, aspect1, aspect2):
        """Creating the definition of the shape according
        to the Zingg diagram, used by both PCA and OBA"""
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

    def _normalise_verts(self, verts):
        """Normalises xyz crystal shape output through a
        transformation to unit lenghts and centering."""

        centered = verts - np.mean(verts, axis=0)
        norm = np.linalg.norm(centered, axis=1).max()
        centered /= norm

        return centered

    @staticmethod
    def read_XYZ(filepath, progress=True):
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

            particle_num_line = 0
            frame_line = 2
            for frame in range(num_frames):
                num_particles = int(lines[particle_num_line])
                xyz = np.loadtxt(lines[frame_line : (frame_line + num_particles)])
                xyz_movie[frame] = xyz
                particle_num_line = frame_line + num_particles
                frame_line = particle_num_line + 2

                progress_num = ((frame + 1) / num_frames) * 100

                
                print(f"#####\nFRAME NUMBER: {frame}")
                print(f"Particle Number Line: {particle_num_line}")
                print(f"Frame Start Line: {frame_line}")
                print(f"Frame End Line: {frame_line + num_particles}")
                print(f"Number of Particles read: {frame_line}")

                print(f"Number of Particles in list: {xyz.shape[0]}")

        return (xyz, xyz_movie, progress_num)

    def get_pca(self, xyz_vals, filetype=".XYZ", n=3):
        """Looks to obtain information on a crystal
        shape as the largest pricipal component is
        used as the longest length, second component
        the medium and the third the shortest"""

        pca = PCA(n_components=n)

        if filetype == ".XYZ" or ".xyz":
            pca.fit(self._normalise_verts(xyz_vals))

        # pca_vectors = pca.components_
        # pca_values = pca.explained_variance_ratio_
        pca_svalues = pca.singular_values_

        return pca_svalues

    def get_sa_vol_ratio(self, xyz_vals):
        """Returns 3D data of a crystal shape,
        Volume:
        Surface Area:
        SA:Vol."""
        hull = ConvexHull(xyz_vals)
        vol_hull = hull.volume
        sa_hull = hull.area
        sa_vol = sa_hull / vol_hull

        sa_vol_ratio_array = np.array([[sa_hull, vol_hull, sa_vol]])

        return sa_vol_ratio_array

    def get_oba(self, coords):
        """OBA - (Orthogonal Box Analysis)
        Measuring the size of the crystal from
        the coordinates collected in read_xyz_file.
        This is measuring the size of the crystal
        based on the x, y and z directions
        """

        # Define namedtuple for dimensions
        result_tuple = namedtuple('Dimension', "x, y, z, aspect1, aspect2, shape")

        # Calculate min, max, and lengths for x, y, z coordinates
        mins = np.min(coords, axis=0)
        maxs = np.max(coords, axis=0)
        lengths = maxs - mins

        # Calculate aspect ratios
        sorted_lengths = np.sort(lengths)
        aspect1 = sorted_lengths[0] / sorted_lengths[1]
        aspect2 = sorted_lengths[1] / sorted_lengths[2]

        # Determine crystal shape
        shape = self.get_shape_class(aspect1, aspect2)

        
        oba_array = np.array(
            [
                lengths[0],
                lengths[0],
                lengths[0],
                aspect1,
                aspect2
            ]
        )
        return oba_array
    
    def get_all(self, xyz_vals, n=3):
        """Returns both Aspect Ratio through PCA
        and Surface Area/Volume information on a
        crystal shape."""
        shape_tuple = namedtuple("shape_info", "aspect1, aspect2, sa, vol, sa_vol")
        
        if xyz_vals.shape[1] == 3:
            xyz_vals = xyz_vals
        if xyz_vals.shape[1] > 3:
            xyz_vals = xyz_vals[0:, 3:6]

        pca_svalues = self.get_pca(xyz_vals, n=n)
        sa_hull, vol_hull, sa_vol = self.get_sa_vol_ratio(xyz_vals)
        small, medium, long = sorted(pca_svalues)

        aspect1 = small / medium
        aspect2 = medium / long
        shape_info = shape_tuple(
            aspect1=aspect1,
            aspect2=aspect2,
            sa=sa_hull,
            vol=vol_hull,
            sa_vol=sa_vol
        )
        return shape_info
