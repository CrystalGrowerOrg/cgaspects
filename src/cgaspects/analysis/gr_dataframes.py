import logging
import re
from typing import List
from pathlib import Path
import numpy as np
import pandas as pd

logger = logging.getLogger("CA:GR-Dataframes")


def get_x_axis(df: pd.DataFrame, *, time_col: str = "time", tol: float = 1e-12):
    """Return a suitable x-axis for growth-rate fitting.

    Uses the time column if it has a sufficient span; otherwise falls back
    to the row index.
    """
    if time_col not in df.columns:
        logger.debug("Using row indices as x-axis (time column not found)")
        return np.arange(len(df), dtype=float)

    x_time = df[time_col].to_numpy(dtype=float)

    if (
        not np.isfinite(x_time).all()
        or len(x_time) < 2
        or np.ptp(x_time) < tol
    ):
        logger.debug("Using row indices as x-axis (time column unsuitable)")
        return np.arange(len(df), dtype=float)

    logger.debug("Using time column as x-axis")
    return x_time


def build_growthrates(
    size_file_list: List[str | Path],
    supersat_list: List[float],
    directions: List[str],
    signals=None,
    time_tol: float = 1e-12,
):
    """Generate the growth rate dataframe from size.csv files."""
    growth_list = []
    n_size_files = len(size_file_list)

    if n_size_files == 0:
        return None

    logger.info("%s size files used to calculate growth rate data", n_size_files)

    for i, f in enumerate(size_file_list):
        f = Path(f)
        lt_df = pd.read_csv(f, encoding="utf-8", encoding_errors="replace")

        missing_directions = [d for d in directions if d not in lt_df.columns]
        if missing_directions:
            logger.warning(
                "Skipping file %s: missing direction columns %s",
                f.name,
                missing_directions,
            )
            continue

        x_data = get_x_axis(lt_df, tol=time_tol)

        tokens = re.findall(r"\d+", f.name)
        sim_num = int(tokens[-1])

        gr_list = [sim_num]
        for direction in directions:
            y_data = np.asarray(lt_df[direction], dtype=float)
            model = np.polyfit(x_data, y_data, 1)
            gr_list.append(model[0])

        growth_list.append(gr_list)

        if signals:
            prog = (100 * (i + 1)) // n_size_files
            signals.progress.emit(prog)

    growth_array = np.asarray(growth_list)
    gr_df = pd.DataFrame(growth_array, columns=["Simulation Number"] + directions)
    gr_df.insert(1, "Supersaturation", supersat_list)

    return gr_df
