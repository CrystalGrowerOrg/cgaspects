import numpy as np
import pandas as pd
from pathlib import Path
import os
from CrystalAspects.data.find_data import Run
from CrystalAspects.visualisation.plot_data import Plotting

r = Run()
#R.aspect_ratio_csv("G:/Nathan/Paracetamol/SeriesLarge/20220310_145918_XYZ_files")

p = Plotting()
p.create_plots_folder(path='G:/Nathan/Paracetamol/SeriesLarge/20220310_145918/CrystalAspects')
p.build_PCAZinng(csv='G:/Nathan/Paracetamol/SeriesLarge/20220310_145918/CrystalAspects/aspectratio_energy.csv',
                 df='', i_plot=True)


def summary_compare(summary_csv, aspect_csv='',
                    aspect_df='', cg_version='new'):
    summary_df = pd.read_csv(summary_csv)

    if aspect_df == '':
        aspect_df = pd.read_csv(aspect_csv)

    summary_cols = summary_df.columns
    aspect_cols = aspect_df.columns[1:]

    if cg_version == 'new':
        '''This allows the user to pick the two different 
        summary file verions from CrystalGrower'''

        search = summary_df.iloc[0, 0]
        search = search.split('_')
        search_string = '_'.join(search[:-1])

        int_cols = summary_cols[1:]
        summary_df = summary_df.set_index(summary_cols[0])
        compare_array = np.empty((0, 7 + len(int_cols)))

        for index, row in aspect_df.iterrows():
            sim_num = int(row['Simulation Number'] - 1)
            num_string = f'{search_string}_{sim_num}'
            print(num_string)
            aspect_row = row.values
            aspect_row = np.array([aspect_row])
            collect_row = summary_df.filter(items=[num_string],
                                            axis=0).values
            print(collect_row)
            collect_row = np.concatenate([aspect_row, collect_row], axis=1)
            compare_array = np.append(compare_array, collect_row, axis=0)
            print(compare_array.shape)

    if cg_version == 'old':
        int_cols = summary_cols[1:]
        compare_array = np.empty((0, 6 + len(int_cols)))

        for index, row in aspect_df.iterrows():
            sim_num = int(row['Simulation Number'] - 1)
            aspect_row = row.values[1:]
            aspect_row = np.array([aspect_row])
            #print(aspect_row)
            collect_row = [summary_df.iloc[sim_num].values[1:]]
            #print(collect_row)
            collect_row = np.concatenate([aspect_row, collect_row], axis=1)
            compare_array = np.append(compare_array, collect_row, axis=0)
            #print(compare_array.shape)

    #print(aspect_cols, int_cols)
    cols = aspect_cols.append(int_cols)
    #print(f'COLS:::: {cols}')
    compare_df = pd.DataFrame(compare_array[:, :], columns=cols)
    #print(compare_df)
    full_df = compare_df.sort_values(by=['Simulation Number'],
                                     ignore_index=True)

    filepath = Path(summary_csv)
    aspects_folder = Path(filepath.parents[0]) / 'CrystalAspects'
    if not os.path.exists(aspects_folder):
        os.makedirs(aspects_folder)

    aspect_energy_csv = f'{aspects_folder}/aspectratio_energy.csv'
    failed_sims_csv = f'{aspects_folder}/failed_sims.csv'

    full_df.to_csv(aspect_energy_csv)
    summary_df.to_csv(failed_sims_csv)

    #print(full_df)
    #print(summary_df)

#summary_compare(aspect_csv='G:/Nathan/Paracetamol/SeriesLarge/20220310_145918_XYZ_files/CrystalAspects/PCA_aspectratio.csv',
#                  summary_csv='G:/Nathan/Paracetamol/SeriesLarge/20220310_145918/20220310_145918_summary.csv',
#                  cg_version='old')