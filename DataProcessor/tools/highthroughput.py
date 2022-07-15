import numpy as np
import pandas as pd
import os
import re
from pathlib import Path

class Highthroughput:

    def energy_from_sph(self, csv_path, solvents=['water']):
        
        csv = Path(csv_path)
        df = pd.read_csv(csv)

        interactions = [col for col in df.columns
                        if col.startswith('interaction')]

        solvents_found = [col for col in df.columns
                    if col.startswith('distance')]
        solvents_matched = []
        for sol in solvents:
            for sol_found in solvents_found:
                if sol in sol_found:
                    solvents_matched.append(sol_found)
        
        print(solvents_matched)



        for sol in solvents_matched:
            print(sol)

            df = df.sort_values(by=[sol])

            for i in interactions:
                int_label = i.split('_')
                mean_col = f'mean_{int_label[-1]}'
                df[mean_col] = df[i].expanding().mean()

            energy_solvent_csv = f'{csv.parents[0]}/mean_energies_{sol}.csv'

            df.to_csv(energy_solvent_csv)

           
