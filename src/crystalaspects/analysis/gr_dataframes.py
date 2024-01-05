import logging
import pandas as pd
import numpy as np

logger = logging.getLogger("CA:GR-Dataframes")

def build_growthrates(size_file_list, supersat_list, directions=[], signals=None):
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
        lt_df = pd.read_csv(f)
        x_data = lt_df["time"]

        if directions:
            lengths = directions
        if directions is False:
            columns = lt_df.columns
            if i == 0:
                for col in columns:
                    if col.startswith(" ") or col.startwith("-1"):
                        lengths.append(col)

        gr_list = []
        for direction in lengths:
            y_data = np.array(lt_df[direction])
            model = np.polyfit(x_data, y_data, 1)
            gr_list.append(model[0])
            # growth_array = np.append(growth_array, gr_list)
        growth_list.append(gr_list)
        i += 1
        if signals:
            signals.progress.emit(int((i / n_size_files) * 100))
    growth_array = np.array(growth_list)
    gr_df = pd.DataFrame(growth_array, columns=lengths)
    gr_df.insert(0, "Supersaturation", supersat_list)

    return gr_df
