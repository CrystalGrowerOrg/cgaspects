import numpy as np
import pandas as pd
from pathlib import Path
import re
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

class AspectRatioCalc:
    def __init__(
        self,
    ):
        pass

    def read_XYZ(self, filename):
        """Opening and reading the .XYZ file"""
        with open(filename, 'r') as f:
            lines = f.readlines()[2:]
            coordinates = []
            for line in lines:
                parts = line.split()
                coordinates.append([float(parts[3]), float(parts[4]), float(parts[5])])
        return np.array(coordinates)

    def measure_crystal_size_xyz(self, coordinates):
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

        shape = self.determine_crystal_shape(aspect1, aspect2)  # Get Zingg definition of crystal

        size_array = np.array([[length_x, length_y, length_z, aspect1, aspect2, shape]])

        return size_array

    def determine_crystal_shape(self, aspect1, aspect2):
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

    def shape_number_percentage(self, df, savefolder):
        '''This section is calculating the number of times
        that lath, needle, plate and block and found in
        the columns OBA Shape Definition and PCA Shape
        Definition to create csv  that shows the percentage
        of each shape found'''
        OBA_shape_counts = df['OBA Shape'].str.lower().value_counts()
        OBA_total_count = OBA_shape_counts.sum()
        OBA_shape_percentages = OBA_shape_counts / OBA_total_count * 100

        PCA_shape_counts = df['PCA Shape'].str.lower().value_counts()
        PCA_total_count = PCA_shape_counts.sum()
        PCA_shape_percentages = PCA_shape_counts / PCA_total_count * 100

        result_df = pd.DataFrame({
            'Shape': OBA_shape_counts.index,
            'OBA Count': OBA_shape_counts,
            'OBA Percentage': OBA_shape_percentages,
            'PCA Count': PCA_shape_counts,
            'PCA Percentage': PCA_shape_percentages
        })
        total_shapes_csv = f"{savefolder}/shape_counts.csv"
        result_df.to_csv(total_shapes_csv, index=False)

    def get_PCA(self, xyz_vals, filetype=".XYZ", n=3):
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

        shape = self.determine_crystal_shape(aspect1, aspect2)  # Get Zingg definition of crystal

        pca_shape = np.array([[small, medium, long, aspect1, aspect2, shape]])

        return pca_shape

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

    def collect_all(self, folder):
        """This collects all the CrystalAspects
        information from each of the relevant functions
        and congregates that into the final DataFrame"""
        col_headings = ["Simulation Number",
                        "OBA Length X", "OBA Length Y", "OBA Length Z", "OBA S:M", "OBA M:L", "OBA Shape",
                        "PCA small", "PCA medium", "PCA long", "PCA S:M", "PCA M:L", "PCA Shape",
                        "Surface Area (SA)", "Volume (Vol)", "SA:Vol Ratio (SAVAR)"
                        ]
        shape_df = None
        for files in Path(folder).iterdir():
            if files.is_dir():
                for file in files.iterdir():
                    if file.suffix == ".XYZ":
                        sim_num = re.findall(r"\d+", file.name)[-1]
                        try:
                            xyz = self.read_XYZ(file)  # Read .XYZ file
                            pca_size = self.get_PCA(xyz)  # Collect PCA data
                            crystal_size = self.measure_crystal_size_xyz(xyz)  # Collect OBA data
                            savar_size = self.get_savar(xyz)  # Collect SAVAR data
                            sim_num_value = np.array([[sim_num]])  # Generate simulation number
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
                            #print(shape_df)

                        except (StopIteration, UnicodeDecodeError):
                            continue

        if len(shape_df) > 0:
            df = pd.DataFrame(
                shape_df,
                columns=col_headings
            )

            print(df)
            #df.to_csv(savefolder + "CrystalAspects.csv", index=False)

        return df
