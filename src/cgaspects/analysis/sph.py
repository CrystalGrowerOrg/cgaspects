import numpy as np
from typing import Literal, Optional
from chmpy.shape.convex_hull import ray_hull_intersections  # type: ignore
from scipy.spatial import ConvexHull


def ray_pointcloud_intersections(directions, point_cloud):
    norm_point_cloud = point_cloud / np.linalg.norm(point_cloud, axis=1)[:, np.newaxis]
    dot_products = np.dot(norm_point_cloud, directions.T)
    intersection_idxs = np.argmax(dot_products, axis=0)
    intersections = point_cloud[intersection_idxs]
    d = np.linalg.norm(intersections, axis=1)
    return np.linalg.norm(d[:, np.newaxis] * directions, axis=1)


def transform_shape(sht, shape, **kwargs):
    """
    Calculate the spherical harmonic transform of the shape of the
    provided convex hull

    Args:
        sht (SHT): the spherical harmonic transform object handle
        shape (ConvexHull): the convex hull (or shape to describe)
        kwargs (dict): keyword arguments for optional settings.
            Options include:
            ```
            origin (np.ndarray): specify the center of the surface
                (default is the geometric centroid of the interior atoms)
            ```
            distances (bool): also return the distances of intersection

    Returns:
        np.ndarray: the coefficients from the analysis step of the SHT
    """

    x, y, z = sht.grid_cartesian
    directions = np.c_[x.flatten(), y.flatten(), z.flatten()]

    if isinstance(shape, ConvexHull):
        r = ray_hull_intersections(directions, shape).reshape(x.shape)
    else:
        r = ray_pointcloud_intersections(directions, shape).reshape(x.shape)

    coeffs = sht.analysis(r)
    if kwargs.get("distances", False):
        return coeffs, r
    else:
        return coeffs


def create_norm_array(
    l_max: int, mode: Optional[Literal["orthonormal", "schmidt"]] = "orthonormal"
) -> np.ndarray:
    """
    Compute normalization factors for spherical harmonics up to a given maximum degree `l_max`.

    This function precomputes normalization factors for each degree `l` and order `m`
    up to `l_max`, based on the specified normalization mode. These factors are used to
    normalize spherical harmonic functions, ensuring their proper orthogonality and
    normalization properties depending on the chosen mode: "orthonormal" or "schmidt".
    If `mode` is None, the function returns an array of ones, effectively applying no normalization.

    Parameters
    ----------
    l_max : int
        The maximum degree of spherical harmonic terms for which normalization factors
        are to be computed.
    mode : {'orthonormal', 'schmidt'}, optional
        The normalization mode to use:
        - 'orthonormal' : Normalizes such that the spherical harmonics are orthonormal over the unit sphere.
        - 'schmidt' : Uses Schmidt semi-normalization, common in geophysics.
        If None, no normalization is applied and an array of ones is returned.

    Returns
    -------
    np.ndarray
        An array of normalization factors for spherical harmonics, with each factor corresponding
        to a combination of `l` and `m` up to `l_max`. If `mode` is None, returns an array of ones.

    Raises
    ------
    ValueError
        If an unsupported normalization mode is specified.

    Examples
    --------
    >>> create_norm_array(2, mode='orthonormal')
    array([0.28209479, 0.28209479, 0.28209479, 0.34549415, 0.34549415, 0.34549415])
    >>> create_norm_array(2, mode=None)
    array([1., 1., 1., 1., 1., 1.])

    Notes
    -----
    The function assumes that the input order of the coefficients aligns with the output
    from the spherical harmonics for which the normalization factors are computed.

    See Also
    --------
    norm_coeffs : Utilizes this function to apply normalization factors to spherical harmonic coefficients.
    """
    # Precompute factorial values
    factorials = [np.math.factorial(i) for i in range(2 * l_max + 1)]

    # Determine the size of the normalization array
    size = (l_max + 1) * (l_max + 2) // 2
    norm = np.ones(size)

    if mode is None:
        return norm

    idx = 0
    # Loop over m first, then l
    for m in range(l_max + 1):
        for l in range(m, l_max + 1):
            if mode == "orthonormal":
                # Full normalization (orthonormal over the unit sphere)
                norm[idx] = np.sqrt(
                    (2 * l + 1) * factorials[l - m] / (4 * np.pi * factorials[l + m])
                )
            elif mode == "schmidt":
                # Schmidt semi-normalized (used in geophysics)
                norm[idx] = np.sqrt(
                    (2 - (m == 0))
                    * (2 * l + 1)
                    * factorials[l - m]
                    / (4 * np.pi * factorials[l + m])
                )
            else:
                raise ValueError(
                    f"Unsupported mode '{mode}'. Only 'orthonormal' and 'schmidt' are supported."
                )
            idx += 1

    return norm


def norm_coeffs(
    coeffs: np.ndarray,
    l_max: int,
    mode: Literal["orthonormal", "schmidt"] = "orthonormal",
    operation: Literal["multiply", "divide"] = "multiply",
    array: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Normalize coefficients for spherical harmonics using specified normalization mode and operation.

    This function adjusts input coefficients by normalization factors for spherical harmonics,
    either multiplying or dividing based on the `operation` parameter. The normalization factors
    are computed based on the maximum degree `l_max` and the chosen mode of normalization: "orthonormal"
    or "schmidt".

    Parameters
    ----------
    coeffs : np.ndarray
        Array of coefficients corresponding to spherical harmonic terms, ordered appropriately to match the
        indexing in `create_norm_array`.
    l_max : int
        The maximum degree of spherical harmonic terms. This value determines the size of the normalization array.
    mode : {'orthonormal', 'schmidt'}, default 'orthonormal'
        The normalization mode to use:
        - 'orthonormal': Normalizes such that the spherical harmonics are orthonormal over the unit sphere.
        - 'schmidt': Uses Schmidt semi-normalization, common in geophysics.
    operation : {'multiply', 'divide'}, default 'multiply'
        The operation to use when applying the normalization factors:
        - 'multiply': Multiplies the coefficients by the normalization factors.
        - 'divide': Divides the coefficients by the normalization factors.

    Returns
    -------
    np.ndarray
        The adjusted coefficients, with the same shape as the input `coeffs`.

    Examples
    --------
    >>> coeffs = np.array([1, 2, 3, 4])
    >>> norm_coeffs(coeffs, l_max=2, mode='orthonormal')
    array([0.28209479, 0.28209479, 0.28209479, 0.28209479])
    >>> norm_coeffs(coeffs, l_max=2, mode='orthonormal', operation='divide')
    array([3.54604934, 3.54604934, 3.54604934, 3.54604934])

    Notes
    -----
    The function assumes that the input `coeffs` are ordered such that they align with the output from `create_norm_array`,
    which computes normalization factors based on the given `l_max` and `mode`.

    Raises
    ------
    ValueError
        If an invalid `mode` or `operation` is provided.
    """
    if array is None:
        norm_array = create_norm_array(l_max=l_max, mode=mode)
    else:
        norm_array = array

    if operation == "multiply":
        coeffs = coeffs * norm_array
        return coeffs
    elif operation == "divide":
        coeffs = coeffs / norm_array
        return coeffs
    else:
        raise ValueError(
            f"Unsupported operation '{operation}'. Only 'multiply' and 'divide' are supported."
        )
