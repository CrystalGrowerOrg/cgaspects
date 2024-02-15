import logging
import re
from typing import List
from pathlib import Path
import numpy as np
import pandas as pd

logger = logging.getLogger("CA:GR-Dataframes")


def build_growthrates(
    size_file_list: List[str | Path],
    supersat_list: List[float],
    directions: List[str],
    signals=None,
):
    """generate the growth rate dataframe from the
    size.csv files"""
    growth_list = []
    lengths = []
    n_size_files = len(size_file_list)
    if n_size_files == 0:
        return None
    logger.info("%s size files used to calculate growth rate data", n_size_files)

    for i, f in enumerate(size_file_list):
        f = Path(f)
        lt_df = pd.read_csv(f)
        x_data = lt_df["time"]
        tokens = re.findall(r"\d+", f.name)
        sim_num = int(tokens[-1])

        logger.info("Directions passed in: %s", directions)
        lengths = directions

        gr_list = [sim_num]
        for direction in lengths:
            y_data = np.array(lt_df[direction])
            model = np.polyfit(x_data, y_data, 1)
            gr_list.append(model[0])
            # growth_array = np.append(growth_array, gr_list)
        growth_list.append(gr_list)
        if signals:
            prog = (100 * (i + 1)) // n_size_files
            signals.progress.emit(prog)
    logger.debug("Growth Rate data (list):  %s", growth_list)
    growth_array = np.asarray(growth_list)
    gr_df = pd.DataFrame(growth_array, columns=["Simulation Number"] + lengths)
    gr_df.insert(1, "Supersaturation", supersat_list)

    return gr_df
