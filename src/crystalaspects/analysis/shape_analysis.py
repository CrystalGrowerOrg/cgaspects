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
        self.xyz = None

    def set_xyz(self, xyz_array=None, filepath=None):
        
        # Check if the xyz_array is provided and is not None
        if xyz_array is not None:
            xyz_vals = np.array(xyz_array)

        # If a filepath is provided, read the XYZ from the file
        if filepath:
            xyz_vals, _, _ = self.read_XYZ(filepath=filepath)

        # Error handling for no valid input
        if xyz_vals is None:
            raise ValueError("Provide XYZ as either an array or a filepath.")


        if xyz_vals.shape[1] == 3:
            xyz_vals = xyz_vals
        if xyz_vals.shape[1] > 3:
            xyz_vals = xyz_vals[0:, 3:6]

        self.xyz = xyz_vals

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
        logger.debug(filepath)
        xyz_movie = {}

        try:
            if filepath.suffix == ".XYZ":
                logger.debug("XYZ: File read!")
                xyz = np.loadtxt(filepath, skiprows=2)
            if filepath.suffix == ".txt":
                logger.debug("xyz: File read!")
                xyz = np.loadtxt(filepath, skiprows=2)
            if filepath.suffix == ".stl":
                logger.debug("stl: File read!")
                xyz = trimesh.load(filepath)

            progress_num = 100

        except ValueError:
            # Set to warning currently since behavious was not tested
            # TO DO: Test and lower logging level
            logger.warning("Looking for Video")
            with open(filepath, "r", encoding="utf-8") as file:
                lines = file.readlines()
                num_frames = int(lines[1].split("//")[1])
                logger.info("Number of Frames: %s", num_frames)

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

    def get_pca(self, n=3):
        """Looks to obtain information on a crystal
        shape as the largest pricipal component is
        used as the longest length, second component
        the medium and the third the shortest"""

        pca = PCA(n_components=n)
        pca.fit(self._normalise_verts(self.xyz))

        # pca_vectors = pca.components_
        # pca_values = pca.explained_variance_ratio_
        pca_svalues = pca.singular_values_

        return pca_svalues

    def get_sa_vol_ratio(self):
        """Returns 3D data of a crystal shape,
        Volume:
        Surface Area:
        SA:Vol."""
        hull = ConvexHull(self.xyz)
        vol_hull = hull.volume
        sa_hull = hull.area
        sa_vol = sa_hull / vol_hull

        sa_vol_ratio_array = np.array([[sa_hull, vol_hull, sa_vol]])

        return sa_vol_ratio_array

    def get_oba(self):
        """OBA - (Orthogonal Box Analysis)
        Measuring the size of the crystal from
        the coordinates collected in read_xyz_file.
        This is measuring the size of the crystal
        based on the x, y and z directions
        """

        # Calculate min, max, and lengths for x, y, z coordinates
        mins = np.min(self.xyz, axis=0)
        maxs = np.max(self.xyz, axis=0)
        lengths = maxs - mins

        # Calculate aspect ratios
        sorted_lengths = np.sort(lengths)
        aspect1 = sorted_lengths[0] / sorted_lengths[1]
        aspect2 = sorted_lengths[1] / sorted_lengths[2]

        # Determine crystal shape
        shape = self.get_shape_class(aspect1, aspect2)

        oba_array = np.array(
            [[
                lengths[0],
                lengths[0],
                lengths[0],
                aspect1,
                aspect2,
                shape,
            ]]
        )
        return oba_array

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
    
    def get_all(self, n=3):
        """Returns both Aspect Ratio through PCA
        and Surface Area/Volume information on a
        crystal shape."""
        shape_tuple = namedtuple("shape_info", "aspect1, aspect2, sa, vol, sa_vol")

        pca_svalues = self.get_pca(n=n)
        sa_vol_r = self.get_sa_vol_ratio()
        sa_hull, vol_hull, sa_vol = sa_vol_r[0][0], sa_vol_r[0][1], sa_vol_r[0][2]
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
