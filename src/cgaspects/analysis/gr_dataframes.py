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
    directions: List[str] | None = None,
    signals=None,
):
    """generate the growth rate dataframe from the
    size.csv files"""
    growth_list = []
    lengths = []
    i = 0
    n_size_files = len(size_file_list)
    if n_size_files == 0:
        return None
    logger.info("%s size files used to calculate growth rate data", n_size_files)

    for f in size_file_list:
        f = Path(f)
        lt_df = pd.read_csv(f)
        x_data = lt_df["time"]
        sim_num = int(re.findall(r"\d+", f.name)[-1])

        if directions is not None:
            logger.info("Directions passed in: %s", directions)
            lengths = directions
        if directions is None:
            lengths = []
            columns = lt_df.columns
            if i == 0:
                for col in columns:
                    if col.startswith(" ") or col.startswith("-1"):
                        lengths.append(col)
                logger.debug(
                    "Directions were read from CSV: %s",
                    lengths,
                )

        gr_list = [sim_num]
        for direction in lengths:
            y_data = np.array(lt_df[direction])
            model = np.polyfit(x_data, y_data, 1)
            gr_list.append(model[0])
            # growth_array = np.append(growth_array, gr_list)
        growth_list.append(gr_list)
        i += 1
        if signals:
            signals.progress.emit(int((i / n_size_files) * 100))
    logger.debug("Growth Rate data (list):  %s", growth_list)
    growth_array = np.asarray(growth_list)
    gr_df = pd.DataFrame(growth_array, columns=["Simulation Number"] + lengths)
    gr_df.insert(1, "Supersaturation", supersat_list)

    return gr_df
