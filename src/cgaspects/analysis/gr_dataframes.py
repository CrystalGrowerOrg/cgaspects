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
    n_size_files = len(size_file_list)

    if n_size_files == 0:
        return None

    logger.info("%s size files used to calculate growth rate data", n_size_files)

    growth_list = []
    use_index_for_all = False
    restart = True

    while restart:
        restart = False
        growth_list = []

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

            # Determine x-axis data
            if use_index_for_all:
                x_data = np.arange(len(lt_df), dtype=float)
            else:
                # Check if time column is suitable
                time_col = "time"
                if time_col not in lt_df.columns:
                    logger.info(
                        "Time column missing in file %s - restarting with index for all files",
                        f.name,
                    )
                    use_index_for_all = True
                    restart = True
                    break
                else:
                    x_time = lt_df[time_col].to_numpy(dtype=float)
                    if (
                        not np.isfinite(x_time).all()
                        or len(x_time) < 2
                        or np.ptp(x_time) < time_tol
                    ):
                        logger.info(
                            "Time column unsuitable in file %s - restarting with index for all files",
                            f.name,
                        )
                        use_index_for_all = True
                        restart = True
                        break
                    else:
                        x_data = x_time

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
