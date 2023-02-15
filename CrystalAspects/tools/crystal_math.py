import numpy as np

def transform_axes(lattice_parameters, arrow_coordinates):
    # Lattice parameters
    a = lattice_parameters['a']
    b = lattice_parameters['b']
    c = lattice_parameters['c']

    # Lattice angles
    alpha = lattice_parameters['alpha']
    beta = lattice_parameters['beta']
    gamma = lattice_parameters['gamma']

    # Cartesian coordinates of the arrow
    x = arrow_coordinates[0]
    y = arrow_coordinates[1]
    z = arrow_coordinates[2]

    # Conversion matrix
    M = np.array([[a, b * np.cos(gamma), c * np.cos(beta)],
                [0, b * np.sin(gamma), c * (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma)],
                [0, 0, c * np.sqrt(1 - np.cos(alpha)**2 - np.cos(beta)**2 - np.cos(gamma)**2 + 2 * np.cos(alpha) * np.cos(beta) * np.cos(gamma)) / np.sin(gamma)]])

    # Convert to crystallographic directions
    crystallographic_directions = np.dot(M, np.array([x, y, z]))

    return crystallographic_directions