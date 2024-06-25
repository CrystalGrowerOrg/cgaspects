import argparse
import json
import logging
import math
from collections import defaultdict
from pathlib import Path
from pprint import pprint as pp
from typing import List

import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd

# import plotly.express as px
import seaborn as sns

from ..analysis.shape_analysis import CrystalShape
from ..utils.cg_net import CGNet
from ..utils.data_structures import shape_info_tuple

LOG = logging.getLogger("SOL-MAP")

CRY = CrystalShape(l_max=50)

SAVE_FOLDER = None
PLT_SHOW = False


def get_rows_cols(n):
    # Calculate the number of columns (n_cols) using square root of n
    n_cols = int(math.ceil(math.sqrt(n)))

    # Calculate the number of rows (n_rows)
    n_rows = int(math.ceil(n / n_cols))
    return n_rows, n_cols


class SolventScreen:
    def __init__(self, folderpath: Path, solvent_dict: dict, lmax=20):
        self.read_shapes(folderpath)

        self.xyz_info = None
        self.wulff_info = None
        self.cda_info = None
        self.occ_info = None

        self.lmax = lmax
        self.crystal = CrystalShape(l_max=50)
        self.solvent_dict = solvent_dict

    def read_shapes(self, folderpath: Path):
        self.xyz_list = list(folderpath.rglob("*.XYZ"))
        self.wulff_list = list(folderpath.rglob("SHAPE*"))
        self.cda_list = list(folderpath.rglob("*simulation_parameters.txt"))
        self.occs_list = list(folderpath.rglob("*.*.stdout"))

        message = (
            f"Found:\n"
            f" {len(self.xyz_list)} XYZs\n"
            f" {len(self.wulff_list)} Wulff shapes\n"
            f" {len(self.cda_list)} CDA files\n"
            f" {len(self.occs_list)} OCC outputs\n"
            f" {len(self.shape_file_list)} shape files"
        )

        LOG.info(message)

    def set_occ_info(self):
        self.occ_info = defaultdict(list)

        for output in self.occs_list:
            solubility = []
            output = Path(output)
            solvent = output.name.split(".")[-2]
            LOG.debug("Checking: %s", solvent)
            with open(output, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                if line.startswith("solubility (g/L)"):
                    solubility.append(float(line.split()[-1]))

            if solubility:
                LOG.info("Solubility in %s: %s", solvent, solubility)
                self.occ_info[solvent].append(solubility)
            else:
                LOG.warning("Solubility was not found for %s!", solvent)

    def set_xyz_info(self):
        self.xyz_info = self.get_shape_info(
            self.xyz_list, self.solvent_dict, get_energy=True
        )

    def set_wulff_info(self):
        self.xyz_info = self.get_shape_info(self.wulff_list, self.solvent_dict)

    def set_cda_info(self, directions, get_energy=True):
        ar_dict = defaultdict(list)

        for cda in self.cda_list:
            solvent = str(Path(cda).parent).rsplit("_", maxsplit=1)[-1]
            add = True
            with open(cda, "r", encoding="utf-8") as sim_file:
                lines = sim_file.readlines()

            for line in lines:
                try:
                    if line.startswith("Size of crystal at frame output"):
                        frame = lines.index(line) + 1
                except NameError:
                    continue

            len_info_lines = lines[frame:]
            for len_line in len_info_lines:
                for direction in directions:
                    if len_line.startswith(direction):
                        ar_dict[direction].append(float(len_line.split(" ")[-2]))
                        if solvent not in list(ar_dict["solvent"]):
                            ar_dict["solvent"].append(solvent)

            if get_energy:

                netfile = Path(cda).parent / "net.txt"
                net = CGNet(netfile)
                net.parse()
                energies = net.unique_energies_arr

                print(f"{netfile.parent.name:>50s}  --> {len(energies)}")
                for i, energy in enumerate(energies):
                    if not add:
                        continue
                    i += 1
                    if np.isnan(energy):
                        continue

                    ar_dict[f"Int_{i}"].append(energy)

        LOG.debug("Selected Directions =", *directions)

        for key, value in ar_dict.items():
            _str = f"{key:>20s}:  {len(value)}"
            LOG.debug(_str)

        df = pd.DataFrame.from_dict(ar_dict)

        # aspect ratio calculation
        LOG.debug(df)
        for i in range(len(directions) - 1):
            print(f"PAIR {i} {directions[i]}    {directions[i + 1]}")

            df[f"AspectRatio_{directions[i]}/{directions[i+1]}"] = (
                df[directions[i]] / df[directions[i + 1]]
            )

        df.to_csv(SAVE_FOLDER / "cda_.csv", index=False)
        return df

    def get_shape_info(self, shapes, solvent_json, get_energy=False):
        shape_info = defaultdict(list)
        solvent = None
        with open(solvent_json, "r", encoding="utf-8") as f:
            sol_dict = json.load(f)

        for shape in shapes:
            shape = Path(shape)
            name_split = str(shape.parent).rsplit("_", maxsplit=1)
            solvent = name_split[-1] if name_split[0] == "solvent" else None
            if shape.name.startswith("SHAPE"):
                with open(shape, "r", encoding="utf-8") as s:
                    lines = s.readlines()

                if "water" in shape.name or "vacuum" in shape.name:
                    continue

                sol_line = lines[1]
                if sol_line.startswith("Solvent") and solvent is None:
                    solvent = (
                        sol_line.split(":")[-1]
                        .lstrip()
                        .replace("\n", "")
                        .replace("E-Z", "E/Z")
                        .replace("cis-trans", "cis/trans")
                    )

            if solvent not in sol_dict:
                LOG.debug("%s", sol_dict.keys())
                LOG.error(
                    "%s Couldn't find solvent! Please check your file structure.",
                    solvent,
                )
                continue

            LOG.info("%s : %s", solvent, shape)
            xyz = self.crystal.set_xyz(filepath=shape)

            analysis: shape_info_tuple = self.crystal.get_zingg_analysis(xyz_vals=xyz)
            shape_info["solvent"].append(solvent)
            shape_info["ar1"].append(analysis.aspect1)
            shape_info["ar2"].append(analysis.aspect2)
            shape_info["sa"].append(analysis.sa)
            shape_info["vol"].append(analysis.vol)
            shape_info["sa_vol"].append(analysis.sa_vol)

            params = sol_dict[solvent]
            shape_info["n"].append(params[0])
            shape_info["acidity"].append(params[1])
            shape_info["basicity"].append(params[2])
            shape_info["gamma"].append(params[3])
            shape_info["dielectric"].append(params[4])
            shape_info["aromatic"].append(params[5])
            shape_info["halogen"].append(params[6])

            if get_energy:
                netfile = shape.parent / "net.txt"
                net = CGNet(netfile)
                net.parse()
                energies = net.unique_energies_arr
                energies = np.array(energies.values()).flatten()

                print(f"{netfile.parent.name:>50s}  --> {len(energies)}")
                for i, energy in enumerate(energies):
                    i += 1
                    if np.isnan(energy):
                        continue

                    shape_info[f"Int_{i}"].append(energy)

        return shape_info


def get_zingg(df, name="", show=False):
    # Create scatter plot with tooltips
    fig, ax = plt.subplots()
    print("ZINGG FOR: ", name)
    print(df)

    if name == "cda":
        ar_cols = [col for col in df.columns if col.startswith("AspectRatio")]
        x = df[ar_cols[0]]
        y = df[ar_cols[1]]
        xlabel = ar_cols[0]
        ylabel = ar_cols[1]

    else:
        print("not cda")
        x = df["ar1"]
        y = df["ar2"]
        xlabel = "S:M"
        ylabel = "M:L"

    scatter = ax.scatter(x, y)

    ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
    ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_title(f"Zingg Plot [{name}]")

    # Add tooltips
    cursors = mplcursors.cursor(scatter, hover=True)
    cursors.connect(
        "add", lambda sel: sel.annotation.set_text(df["solvent"][sel.target.index])
    )
    plt.tight_layout()
    plt.savefig(SAVE_FOLDER / f"zingg_{name}.png")

    if show:
        plt.show()

    # figi = px.scatter(x=x, y=y, hover_name=df["solvent"])
    # figi.write_html(SAVE_FOLDER / f"zingg_{name}_interactive.html")


def plot_with_labels(df, name="", solvents_to_show=None, show=False):
    # Create scatter plot with tooltips
    fig, ax = plt.subplots()
    print("ZINGG FOR: ", name)
    print(df)

    if name == "cda":
        ar_cols = [col for col in df.columns if col.startswith("AspectRatio")]
        x = df[ar_cols[0]]
        y = df[ar_cols[1]]
        xlabel = ar_cols[0]
        ylabel = ar_cols[1]
    else:
        x = df["ar1"]
        y = df["ar2"]
        xlabel = "S:M"
        ylabel = "M:L"

    scatter = ax.scatter(x, y)

    ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
    ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.set_title(f"Zingg Plot [{name}]")

    # Add labels for selected solvents
    print("SOLVENTS TO SHOW: ", solvents_to_show)
    n = len(solvents_to_show)
    half = n // 2
    i = 0
    for index, row in df.iterrows():
        if solvents_to_show and row["solvent"] in solvents_to_show:
            if row["solvent"] in solvents_to_show[:half]:
                print("SHORT: ", row["solvent"])
                ax.annotate(
                    row["solvent"],
                    (x.iloc[index], y.iloc[index]),
                    xytext=(-100, -100),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.3),
                    arrowprops=dict(
                        arrowstyle="->",
                        connectionstyle="arc,angleA=90,angleB=0,armA=0,armB=-100,rad=0",
                        color="red",
                    ),
                )
            else:
                print("LONG: ", row["solvent"])
                ax.annotate(
                    row["solvent"],
                    (x.iloc[index], y.iloc[index]),
                    xytext=(-150, -5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.3),
                    arrowprops=dict(
                        arrowstyle="->",
                        connectionstyle="arc,angleA=-90,angleB=0,armA=0,armB=-160,rad=0",
                        color="red",
                    ),
                )
            i += 1
            # ax.annotate(row["solvent"], (x.iloc[index], y.iloc[index]),
            #             textcoords="offset points", xytext=(0, 10),
            #             ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(SAVE_FOLDER / f"zingg_{name}.png")

    if show:
        plt.show()


def plot_solvents(df: pd.DataFrame, name="", exclude: list = None, *, show=False):
    # Exclude specified solvents
    if exclude is not None:
        df = df[~df["solvent"].isin(exclude)]

    print("SOLVENT based data: ", name)
    print(df)

    if name == "cda":
        ar_cols = [col for col in df.columns if col.startswith("AspectRatio")]
        p = df[ar_cols[0]]
        q = df[ar_cols[1]]
    else:
        p = df["ar1"]
        q = df["ar2"]

    x = df["acidity"]
    # x = np.arange(len(df["solvent"]))

    sphericity = (12.8 * (p**2 * q) ** (1 / 3)) / (
        1 + p * (1 + q) + 6 * (1 + p**2 * (1 + q**2)) ** 0.5
    )

    common = ["solvent", "ar1", "ar2", "sa", "vol", "sa_vol"]
    int_cols = [col for col in df if col.startswith("Int")]
    common += int_cols

    subplot_titles = [col for col in df.columns if col not in common]

    n_rows, n_cols = get_rows_cols(len(subplot_titles))
    print(f"ROWS: {n_rows}, COLS: {n_cols}")
    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 15))
    fig.suptitle(f"Solvent Parameters vs Shape Descriptors [{name}]", fontsize=16)

    ## Iterate through subplot axes and subplot titles
    for i, (ax, param_title) in enumerate(zip(axes.flat, subplot_titles)):
        param_data = pd.to_numeric(df[param_title])
        # Filter non-zero and positive values
        if param_title != "solubility":
            valid_param_data = param_data[(param_data > 0)]
        else:
            valid_param_data = param_data

        x_max = valid_param_data.max()
        x_min = valid_param_data.min()

        # Create different scatter plots with different colors
        ax.scatter(param_data, p, label="Flatness Ratio", color="green")
        ax.scatter(param_data, q, label="Elongation Ratio", color="blue")
        ax.scatter(param_data, sphericity, label="Sphericity", color="red")
        print(
            f"{param_title}  p: {p.shape} q: {q.shape} sphericity: {sphericity.shape}| {x_min}->{x_max}"
        )
        ax.set_xlim([x_min, x_max])
        ax.set_ylim([0, 1])
        ax.set_xlabel(param_title)
        ax.set_ylabel("Ratio")

        # Add a legend to the subplot
        if i == 0:
            ax.legend()

    plt.tight_layout()

    plt.savefig(SAVE_FOLDER / f"ZinggSolvents_{name}.png")
    if show:
        plt.show()


def plot_interaction_energies(df, x_columns=None, name="", *, show=False):

    if x_columns is None:
        x_columns = [
            "solvent",
            "n",
            "gamma",
            "dielectric",
            "acidity",
            "basicity",
            "aromatic",
            "halogen",
        ]

    interaction_columns = [col for col in df.columns if col.startswith("Int_")]

    # Separate plot for solvents
    if "solvent" in x_columns:
        _, ax = plt.subplots(figsize=(10, 6))
        for interaction_column in interaction_columns:
            # Assuming df['solvent'] contains categorical/string data
            for i, solvent in enumerate(df["solvent"].unique()):
                subset = df[df["solvent"] == solvent]
                ax.scatter(
                    x=np.repeat(i, subset.shape[0]),
                    y=subset[interaction_column],
                    label=interaction_column if i == 0 else "",
                    alpha=0.7,
                )
        ax.set_xticks(range(len(df["solvent"].unique())))
        ax.set_xticklabels(df["solvent"].unique(), rotation=45)
        ax.set_ylabel("Interaction Energy")
        ax.legend(title="Interaction type")
        plt.tight_layout()
        plt.savefig(SAVE_FOLDER / f"energies_solvent_{name}.png")
        plt.close()

    # Subplots for other x_columns
    for x_axis_column in [x for x in x_columns if x != "solvent"]:
        fig, ax = plt.subplots(figsize=(10, 6))
        for interaction_column in interaction_columns:
            sorted_df = df.sort_values(by=x_axis_column)
            sorted_df = sorted_df[df[x_axis_column] > 0]
            ax.scatter(
                x=sorted_df[x_axis_column],
                y=sorted_df[interaction_column],
                label=interaction_column,
                alpha=0.7,
            )
        ax.set_xlabel(x_axis_column)
        ax.set_ylabel("Interaction Energy (kJ/mol)")
        ax.legend(title="Interaction type", loc="center left", bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        plt.savefig(SAVE_FOLDER / f"energies_{x_axis_column}_{name}.png")
        if show:
            plt.show
        plt.close()


def plot_corr_matrix(df: pd.DataFrame, name="", path=None, *, show=False):
    if name is None:
        name == "corr"
    if path is None:
        path = Path.cwd()

    df1 = df.corr(method="pearson", numeric_only=True)
    df2 = df.corr(method="spearman", numeric_only=True)
    LOG.info("PEARSON CORR MATRIX:\n%s", df1.round(2))
    LOG.info("SPEARMAN CORR MATRIX:\n%s", df2.round(2))
    # Plotting the correlation matrix
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        df1,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
        cbar=True,
        linewidths=0.5,
    )
    plt.title("Pearson Correlation Matrix")
    plt.savefig(path / f"corr_peason_{name}.png")
    plt.clf()
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        df2,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        square=True,
        cbar=True,
        linewidths=0.5,
    )
    plt.title("Spearman Correlation Matrix")
    plt.savefig(path / f"corr_spearman_{name}.png")
    if show:
        plt.show()
    plt.close()


def zinggs_with_params(df, name="", *, show=False):
    # Parameters for subplot arrangement
    common = ["solvent", "ar1", "ar2", "sa", "vol", "sa_vol"]
    int_cols = [col for col in df if col.startswith("Int")]
    common += int_cols
    subplot_titles = [col for col in df.columns if col not in common]

    n_rows, n_cols = get_rows_cols(len(subplot_titles))
    print(f"ROWS: {n_rows}, COLS: {n_cols}")
    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 15))
    fig.suptitle(f"Zingg Plots Colored by Different Parameters [{name}]", fontsize=16)

    # Iterate through subplot axes and subplot titles
    for ax, param_title in zip(axes.flat, subplot_titles):
        param_data = pd.to_numeric(df[param_title])
        # Handling the case of water
        vmin = 0 if param_data.min() == -1 else None
        scatter = ax.scatter(
            df["ar1"], df["ar2"], c=param_data, cmap="viridis", vmin=vmin
        )
        ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.set_xlabel("S:M")
        ax.set_ylabel("M:L")
        ax.set_title(f"{param_title.capitalize()}")
        if param_title == "solubility":
            param_title = "log[solubility (g/L)]"
        else:
            param_title = param_title.capitalize()

        fig.colorbar(scatter, ax=ax, label=param_title)

    plt.tight_layout()
    plt.savefig(SAVE_FOLDER / f"ZinggParams_{name}.png")


def zinggs_with_energies(df, name="", *, show=False):
    if not name:
        name = "cda"
    cols = df.columns

    int_cols = [col for col in cols if col.startswith("Int")]
    ar_cols = [
        col for col in cols if col.startswith("AspectRatio" if name == "cda" else "ar")
    ]

    print(int_cols)

    n_rows, n_cols = get_rows_cols(len(int_cols))
    print(f"ROWS: {n_rows}, COLS: {n_cols}")

    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 15))
    fig.suptitle(f"Zingg Plots Colored by Different Energies [{name}]", fontsize=16)

    # Iterate through subplot axes and subplot titles
    for ax, int_title in zip(axes.flat, int_cols):
        scatter = ax.scatter(
            df[ar_cols[0]],
            df[ar_cols[1]],
            c=pd.to_numeric(df[int_title]),
            cmap="viridis",
        )
        ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.set_xlabel(ar_cols[0])
        ax.set_ylabel(ar_cols[1])
        ax.set_title(f"{int_title.capitalize()}")
        fig.colorbar(scatter, ax=ax, label=int_title.capitalize())

    plt.tight_layout()
    plt.savefig(SAVE_FOLDER / f"ZinggEnergies_{name}.png")
    if PLT_SHOW:
        plt.show()


def zinggs_with_solvent_class(df, name=None, path=None, *, show=False):
    if name is None:
        name = "cg"
    if path is None:
        path = Path.cwd()

    cols = df.columns
    ar_cols = [
        col for col in cols if col.startswith("AspectRatio" if name == "cda" else "ar")
    ]
    int_cols = [
        "H-bond-donating with OH",
        "H-bond-accepting",
        "Polar - no OH",
        "Halogen containing",
        "Hydrocarbon",
    ]

    print(int_cols)

    n_rows, n_cols = get_rows_cols(len(int_cols))
    print(f"ROWS: {n_rows}, COLS: {n_cols}")

    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 10))
    fig.suptitle(f"Zingg Plots Colored by Solvent Class [{name}]", fontsize=16)

    # Iterate through subplot axes and subplot titles
    for ax, int_title in zip(axes.flat, int_cols):
        scatter = ax.scatter(
            df[ar_cols[0]],
            df[ar_cols[1]],
            c=pd.to_numeric(df[int_title]),
            cmap="viridis",
        )
        ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.set_xlabel(ar_cols[0])
        ax.set_ylabel(ar_cols[1])
        ax.set_title(f"{int_title.capitalize()}")
        fig.colorbar(scatter, ax=ax, label=int_title.capitalize())

    plt.tight_layout()
    plt.savefig(path / f"ZinggSolClass_{name}.png")
    if show:
        plt.show()


def zinggs_with_other(df, params=None, name="", *, show=False):
    if params is None:
        params = ["sa_vol"]
    if not name:
        name = "pca"

    if len(params) == 3:
        n_rows = 1
        n_cols = 3
    else:
        n_rows, n_cols = get_rows_cols(len(params))

    print(f"ROWS: {n_rows}, COLS: {n_cols}")
    # Create subplots
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 10))
    fig.suptitle(f"Zingg Plots Colored by Selected Parameters [{name}]", fontsize=16)

    if len(params) > 1:
        # Iterate through subplot axes and subplot titles
        for ax, int_title in zip(axes.flat, params):
            scatter = ax.scatter(
                df["ar1"], df["ar2"], c=pd.to_numeric(df[int_title]), cmap="viridis"
            )
            ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
            ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
            ax.set_xlim([0, 1])
            ax.set_ylim([0, 1])
            ax.set_xlabel("S:M")
            ax.set_ylabel("M:L")
            ax.set_title(f"{int_title.capitalize()}")
            fig.colorbar(scatter, ax=ax, label=int_title.capitalize())
    if len(params) == 1:
        fig, ax = plt.subplots()
        param = params[0]
        scatter = ax.scatter(
            df["ar1"], df["ar2"], c=pd.to_numeric(df[param]), cmap="viridis"
        )
        ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.set_xlabel("S:M")
        ax.set_ylabel("M:L")
        ax.set_title(f"Zingg Plot Colored by {param.upper()} [{name}]")
        fig.colorbar(scatter, ax=ax, label=param.upper())

    plt.tight_layout()
    plt.savefig(SAVE_FOLDER / f"ZinggSelected_{name}.png")
    if show:
        plt.show()


if __name__ == "__main__":
    pass
