"""Utilities for smoothing, interpolating, and extrapolating data series."""

import logging
import numpy as np
import pandas as pd
from scipy import signal, interpolate
from scipy.ndimage import gaussian_filter1d

logger = logging.getLogger("CA:DataSmoothing")


def moving_average(data, window_size):
    """
    Apply moving average smoothing to data.

    Args:
        data: Array-like data
        window_size: Size of the moving window (must be odd)

    Returns:
        Smoothed data as numpy array
    """
    if window_size % 2 == 0:
        window_size += 1  # Make it odd

    if len(data) < window_size:
        logger.warning(f"Data length ({len(data)}) < window size ({window_size}), returning original data")
        return np.array(data)

    return np.convolve(data, np.ones(window_size) / window_size, mode='same')


def savitzky_golay(data, window_size, poly_order):
    """
    Apply Savitzky-Golay filter for smoothing.

    Args:
        data: Array-like data
        window_size: Size of the filter window (must be odd)
        poly_order: Order of the polynomial used for fitting

    Returns:
        Smoothed data as numpy array
    """
    if window_size % 2 == 0:
        window_size += 1  # Make it odd

    if len(data) < window_size:
        logger.warning(f"Data length ({len(data)}) < window size ({window_size}), returning original data")
        return np.array(data)

    if poly_order >= window_size:
        poly_order = window_size - 1
        logger.warning(f"Polynomial order too high, reduced to {poly_order}")

    try:
        return signal.savgol_filter(data, window_size, poly_order)
    except Exception as e:
        logger.error(f"Savitzky-Golay filter failed: {e}, returning original data")
        return np.array(data)


def gaussian_smooth(data, window_size):
    """
    Apply Gaussian smoothing to data.

    Args:
        data: Array-like data
        window_size: Standard deviation for Gaussian kernel

    Returns:
        Smoothed data as numpy array
    """
    try:
        sigma = window_size / 3.0  # Convert window size to sigma
        return gaussian_filter1d(data, sigma=sigma)
    except Exception as e:
        logger.error(f"Gaussian smoothing failed: {e}, returning original data")
        return np.array(data)


def lowess_smooth(data, window_size):
    """
    Apply LOWESS (Locally Weighted Scatterplot Smoothing).

    Args:
        data: Array-like data
        window_size: Window size for local regression

    Returns:
        Smoothed data as numpy array
    """
    try:
        # Try to import statsmodels (optional dependency)
        from statsmodels.nonparametric.smoothers_lowess import lowess

        # Create x values (indices)
        x = np.arange(len(data))

        # Convert window_size to fraction
        frac = min(window_size / len(data), 1.0)

        # Apply LOWESS
        smoothed = lowess(data, x, frac=frac, return_sorted=False)
        return smoothed

    except ImportError:
        logger.warning("statsmodels not available, falling back to moving average")
        return moving_average(data, window_size)
    except Exception as e:
        logger.error(f"LOWESS smoothing failed: {e}, returning original data")
        return np.array(data)


def smooth_data(x, y, method, window_size=5, poly_order=2):
    """
    Apply smoothing to data.

    Args:
        x: X-axis data (for sorting)
        y: Y-axis data to smooth
        method: Smoothing method ('Moving Average', 'Savitzky-Golay', 'Gaussian', 'LOWESS', or 'None')
        window_size: Window size for smoothing
        poly_order: Polynomial order (for Savitzky-Golay)

    Returns:
        Tuple of (x_sorted, y_smoothed)
    """
    # Convert to numpy arrays
    x = np.array(x)
    y = np.array(y)

    # Sort by x values
    sort_idx = np.argsort(x)
    x_sorted = x[sort_idx]
    y_sorted = y[sort_idx]

    # Remove NaN values
    valid_mask = ~(np.isnan(x_sorted) | np.isnan(y_sorted))
    x_sorted = x_sorted[valid_mask]
    y_sorted = y_sorted[valid_mask]

    if len(x_sorted) < 2:
        logger.warning("Not enough valid data points for smoothing")
        return x_sorted, y_sorted

    if method == "None" or method is None:
        return x_sorted, y_sorted
    elif method == "Moving Average":
        y_smoothed = moving_average(y_sorted, window_size)
    elif method == "Savitzky-Golay":
        y_smoothed = savitzky_golay(y_sorted, window_size, poly_order)
    elif method == "Gaussian":
        y_smoothed = gaussian_smooth(y_sorted, window_size)
    elif method == "LOWESS":
        y_smoothed = lowess_smooth(y_sorted, window_size)
    else:
        logger.warning(f"Unknown smoothing method: {method}, returning original data")
        y_smoothed = y_sorted

    return x_sorted, y_smoothed


def interpolate_data(x, y, method, num_points=100):
    """
    Interpolate data to create a smoother curve.

    Args:
        x: X-axis data
        y: Y-axis data
        method: Interpolation method ('Linear', 'Cubic Spline', 'Polynomial', 'Pchip', or 'None')
        num_points: Number of points in the interpolated result

    Returns:
        Tuple of (x_interp, y_interp)
    """
    # Convert to numpy arrays
    x = np.array(x)
    y = np.array(y)

    # Remove NaN and sort
    valid_mask = ~(np.isnan(x) | np.isnan(y))
    x = x[valid_mask]
    y = y[valid_mask]

    if len(x) < 2:
        logger.warning("Not enough valid data points for interpolation")
        return x, y

    # Sort by x
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]

    if method == "None" or method is None:
        return x, y

    # Create interpolation points
    x_interp = np.linspace(x.min(), x.max(), num_points)

    try:
        if method == "Linear":
            f = interpolate.interp1d(x, y, kind='linear')
            y_interp = f(x_interp)
        elif method == "Cubic Spline":
            if len(x) < 4:
                logger.warning("Need at least 4 points for cubic spline, using linear")
                f = interpolate.interp1d(x, y, kind='linear')
            else:
                f = interpolate.CubicSpline(x, y)
            y_interp = f(x_interp)
        elif method == "Polynomial":
            # Fit polynomial (degree based on number of points, max 5)
            degree = min(len(x) - 1, 5)
            coeffs = np.polyfit(x, y, degree)
            y_interp = np.polyval(coeffs, x_interp)
        elif method == "Pchip":
            if len(x) < 2:
                return x, y
            f = interpolate.PchipInterpolator(x, y)
            y_interp = f(x_interp)
        else:
            logger.warning(f"Unknown interpolation method: {method}, returning original data")
            return x, y

        return x_interp, y_interp

    except Exception as e:
        logger.error(f"Interpolation failed: {e}, returning original data")
        return x, y


def extrapolate_data(x, y, method, extend_percent=20.0, poly_order=2):
    """
    Extrapolate data beyond the existing range.

    Args:
        x: X-axis data
        y: Y-axis data
        method: Extrapolation method ('Linear', 'Polynomial', 'Exponential')
        extend_percent: Percentage of range to extend on each side
        poly_order: Order of polynomial for polynomial extrapolation

    Returns:
        Tuple of (x_extrap, y_extrap) including original and extrapolated points
    """
    # Convert to numpy arrays
    x = np.array(x)
    y = np.array(y)

    # Remove NaN and sort
    valid_mask = ~(np.isnan(x) | np.isnan(y))
    x = x[valid_mask]
    y = y[valid_mask]

    if len(x) < 2:
        logger.warning("Not enough valid data points for extrapolation")
        return x, y

    # Sort by x
    sort_idx = np.argsort(x)
    x = x[sort_idx]
    y = y[sort_idx]

    # Calculate extension range
    x_range = x.max() - x.min()
    extension = x_range * (extend_percent / 100.0)

    # Create extended x range
    x_min_new = x.min() - extension
    x_max_new = x.max() + extension

    # Number of extrapolation points on each side
    num_points = len(x)
    num_extrap_points = max(10, num_points // 5)

    x_left = np.linspace(x_min_new, x.min(), num_extrap_points, endpoint=False)
    x_right = np.linspace(x.max(), x_max_new, num_extrap_points + 1)[1:]  # Exclude duplicate of x.max()

    try:
        if method == "Linear":
            # Linear extrapolation using first and last two points
            # Left side
            slope_left = (y[1] - y[0]) / (x[1] - x[0]) if len(x) > 1 else 0
            y_left = y[0] + slope_left * (x_left - x[0])

            # Right side
            slope_right = (y[-1] - y[-2]) / (x[-1] - x[-2]) if len(x) > 1 else 0
            y_right = y[-1] + slope_right * (x_right - x[-1])

        elif method == "Polynomial":
            # Polynomial fit
            degree = min(poly_order, len(x) - 1)
            coeffs = np.polyfit(x, y, degree)

            y_left = np.polyval(coeffs, x_left)
            y_right = np.polyval(coeffs, x_right)

        elif method == "Exponential":
            # Exponential extrapolation (fit to log of positive data)
            try:
                # Ensure positive values for log
                if np.any(y <= 0):
                    logger.warning("Exponential extrapolation requires positive values, using polynomial")
                    degree = min(2, len(x) - 1)
                    coeffs = np.polyfit(x, y, degree)
                    y_left = np.polyval(coeffs, x_left)
                    y_right = np.polyval(coeffs, x_right)
                else:
                    # Fit exponential: y = a * exp(b * x)
                    log_y = np.log(y)
                    coeffs = np.polyfit(x, log_y, 1)
                    y_left = np.exp(np.polyval(coeffs, x_left))
                    y_right = np.exp(np.polyval(coeffs, x_right))
            except Exception as e:
                logger.warning(f"Exponential fit failed: {e}, using polynomial")
                degree = min(2, len(x) - 1)
                coeffs = np.polyfit(x, y, degree)
                y_left = np.polyval(coeffs, x_left)
                y_right = np.polyval(coeffs, x_right)
        else:
            logger.warning(f"Unknown extrapolation method: {method}, returning original data")
            return x, y

        # Combine all points
        x_extrap = np.concatenate([x_left, x, x_right])
        y_extrap = np.concatenate([y_left, y, y_right])

        return x_extrap, y_extrap

    except Exception as e:
        logger.error(f"Extrapolation failed: {e}, returning original data")
        return x, y


def process_series(x, y, config):
    """
    Apply full processing pipeline to a data series.

    Args:
        x: X-axis data
        y: Y-axis data
        config: Configuration dictionary with smoothing, interpolation, and extrapolation settings

    Returns:
        Tuple of (x_processed, y_processed)
    """
    x_proc = np.array(x)
    y_proc = np.array(y)

    # Step 1: Smoothing
    if config and "smoothing" in config:
        s = config["smoothing"]
        method = s.get("method", "None")
        if method != "None":
            x_proc, y_proc = smooth_data(
                x_proc, y_proc,
                method=method,
                window_size=s.get("window_size", 5),
                poly_order=s.get("poly_order", 2)
            )

    # Step 2: Interpolation
    if config and "interpolation" in config:
        i = config["interpolation"]
        method = i.get("method", "None")
        if method != "None":
            x_proc, y_proc = interpolate_data(
                x_proc, y_proc,
                method=method,
                num_points=i.get("points", 100)
            )

    # Step 3: Extrapolation
    if config and "extrapolation" in config:
        e = config["extrapolation"]
        if e.get("enabled", False):
            x_proc, y_proc = extrapolate_data(
                x_proc, y_proc,
                method=e.get("method", "Linear"),
                extend_percent=e.get("percent", 20.0),
                poly_order=e.get("poly_order", 2)
            )

    return x_proc, y_proc
