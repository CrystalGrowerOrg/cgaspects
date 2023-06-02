import numpy as np

def read_xyz_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()[2:]
        coordinates = []
        for line in lines:
            parts = line.split()
            coordinates.append([float(parts[3]), float(parts[4]), float(parts[5])])
    return np.array(coordinates)

def measure_crystal_size(coordinates):
    min_coords = np.min(coordinates, axis=0)
    max_coords = np.max(coordinates, axis=0)
    box_size = max_coords - min_coords
    small_dist = np.min(box_size)
    medium_dist = np.median(box_size)
    long_dist = np.max(box_size)
    return small_dist, medium_dist, long_dist

# Example usage
xyz_filename = "/Users/student/Downloads/DaniMOF/Testing/20230307_221958/XYZ_files/Test_lno_ovito_CGvisualiser.XYZ"
coordinates = read_xyz_file(xyz_filename)
small_dist, medium_dist, long_dist = measure_crystal_size(coordinates)
print("Small distance: {:.2f}".format(small_dist))
print("Medium distance: {:.2f}".format(medium_dist))
print("Long distance: {:.2f}".format(long_dist))