# Standard library imports
import logging
from pathlib import Path
from typing import List, Literal
import math

# Third-party library imports
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# PySide6 imports
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

matplotlib.use("QT5Agg")

logger = logging.getLogger("CA:Plotting")


class Plotting(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    def create_plots_folder(self, path):
        plots_folder = Path(path) / "CGPlots"
        plots_folder.mkdir(parents=True, exist_ok=True)
        return plots_folder

    def plot_zingg(self, csv="", df="", folderpath="./outputs"):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)
        savefolder = self.create_plots_folder(folderpath)

        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]
        x_data = df["S:M"]
        y_data = df["M:L"]

        plt.figure()
        plt.scatter(x_data, y_data, s=10)
        plt.axhline(y=0.66, color="black", linestyle="--")
        plt.axvline(x=0.66, color="black", linestyle="--")
        plt.xlim(0, 1)  # Adjust x-axis limits
        plt.ylim(0, 1)  # Adjust y-axis limits
        plt.xlabel("S:M")
        plt.ylabel("M:L")
        savepath = savefolder / "zingg"
        logger.info("Plotting ZINGG FIG")
        plt.savefig(savepath, dpi=900)
        plt.close()

        for interaction in interactions:
            plt.figure()
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S:M")
            plt.ylabel("M:L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            savepath = savefolder / f"zingg_{interaction}"
            logger.info("Plotting ZINGG FIG for %s", interaction)
            plt.savefig(savepath, dpi=300)
            plt.close()

    def plot_cda_extended(
        self, csv="", df="", folderpath="./outputs", selected="", i_plot=False
    ):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        savefolder = self.create_plots_folder(folderpath)
        extended_df = df

        i = 0
        plt.figure()
        x_data = extended_df[f"Ratio_{selected[i]}:{selected[i+1]}"]
        y_data = extended_df[f"Ratio_{selected[i+1]}:{selected[i+2]}"]
        plt.scatter(x_data, y_data, s=1.2)
        plt.xlabel(f"Ratio_{selected[i]}:{selected[i+1]}")
        plt.ylabel(f"Ratio_{selected[i+1]}:{selected[i+2]}")
        savepath = savefolder / f"ratio_{selected[i]}_{selected[i+1]}_[{selected[i+2]}"
        logger.info("Plotting CDA (extended) FIG")
        plt.savefig(savepath, dpi=300)
        plt.close()

        interactions = [
            col
            for col in extended_df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        for interaction in interactions:
            plt.figure()
            c_df = extended_df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.title(textstr)
            plt.xlabel(f"Ratio_{selected[i]}:{selected[i+1]}")
            plt.ylabel(f"Ratio_{selected[i+1]}:{selected[i+2]}")
            plt.xlim(0.0)
            plt.ylim(0.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            savepath = (
                savefolder
                / f"aspect_{selected[i]}_{selected[i+1]}_{selected[i+2]}_{interaction}"
            )
            logger.info("Plotting CDA (extended) FIG for %s", interaction)
            plt.savefig(savepath, dpi=300)
            plt.close()

    def plot_zingg_permuations(
        self, csv="", df="", folderpath="./outputs", i_plot=False
    ):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        zn_df = df
        savefolder = self.create_plots_folder(folderpath)

        permutations = set(zn_df["CDA_Permutation"])

        for permutation in permutations:
            plt.figure()
            textstr = permutation
            equation_df = zn_df[zn_df["CDA_Permutation"] == permutation]
            x_data = equation_df["S:M"]
            y_data = equation_df["M:L"]
            plt.figure()
            plt.scatter(x_data, y_data, s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S:M")
            plt.ylabel("M:L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            savepath = savefolder / f"pca_permutaion_{permutation}"
            logger.info("Plotting PCA/CDA FIG for equation %s", permutation)
            plt.savefig(savepath, dpi=300)
            plt.close()

    ####################################
    # Plotting Surface Area and Volume #
    ####################################

    def plot_sa_vol(self, csv="", df="", folderpath="./outputs", i_plot=False):
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)

        sa_vol_ratio_df = df

        savefolder = self.create_plots_folder(folderpath)
        interactions = [
            col
            for col in sa_vol_ratio_df.columns
            if col.startswith("interaction")
            or col.startswith("tile")
            or col.startswith("temperature")
        ]

        x_data = sa_vol_ratio_df["Volume"]
        y_data = sa_vol_ratio_df["Surface Area"]
        plt.figure()
        for interaction in interactions:
            c_df = sa_vol_ratio_df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            plt.xlabel(r"Volume ($nm^3$)")
            plt.ylabel(r"Surface Area ($nm^2$)")
            savepath = savefolder / f"sa_vol_{interaction}"
            logger.info("Plotting SA/VOL FIG for %s", interaction)
            plt.savefig(savepath, dpi=900)
        plt.close()

        plt.scatter(x_data, y_data, s=1.2)
        plt.xlabel(r"Volume ($nm^3$)")
        plt.ylabel(r"Surface Area ($nm^2$)")
        savepath = savefolder / "sa_vol"
        logger.info("Plotting SA/VOL FIG")
        plt.savefig(savepath, dpi=900)

    ################################
    # Plotting Growth Rates        #
    ################################

    def plot_growth_rates(self, gr_df, lengths, savepath):
        x_data = gr_df["Supersaturation"]
        for i in lengths:
            plt.scatter(x_data, gr_df[i], s=1.2)
            plt.plot(x_data, gr_df[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
        logger.info("Plotting growth/dissolution rates")
        plt.savefig(savepath / "growth_and_dissolution_rates", dpi=300)

        growth_data = gr_df[gr_df["Supersaturation"] >= 0]
        plt.clf()
        plt.figure(figsize=(5, 5))

        for i in lengths:
            plt.scatter(growth_data["Supersaturation"], growth_data[i], s=1.2)
            plt.plot(growth_data["Supersaturation"], growth_data[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
        logger.info("Plotting growth rates")
        plt.savefig(savepath / "growth_rates", dpi=300)

        plt.clf()
        plt.figure(figsize=(5, 5))
        for i in lengths:
            plt.scatter(growth_data["Supersaturation"], growth_data[i], s=1.2)
            plt.plot(growth_data["Supersaturation"], growth_data[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.xlim(0.0, 2.5)
            plt.ylim(0.0, 0.4)
            plt.tight_layout()
        logger.info("Plotting growth rates (zoomed)")
        plt.savefig(savepath / "growth_rates_zoomed", dpi=300)

        dissolution_data = gr_df[gr_df["Supersaturation"] <= 0]
        plt.clf()
        plt.figure(figsize=(7, 5))
        for i in lengths:
            plt.scatter(
                dissolution_data["Supersaturation"], dissolution_data[i], label=i, s=1.2
            )
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Dissolution Rate")
            plt.tight_layout()
        logger.info("Plotting dissolution rates")
        plt.savefig(savepath / "dissolution_rates", dpi=300)

        plt.clf()
        plt.figure(figsize=(5, 5))
        for i in lengths:
            plt.scatter(dissolution_data["Supersaturation"], dissolution_data[i], s=1.2)
            plt.plot(dissolution_data["Supersaturation"], dissolution_data[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.xlim(-2.5, 0.0)
            plt.ylim(-2.5, 0.0)
            plt.tight_layout()
        logger.info("Plotting dissolution rates (zoomed)")
        plt.savefig(savepath / "dissolution_rates_zoomed", dpi=300)

    ################################
    # Plotting Solvents            #
    ################################

    def plot_corr_matrix(
        df: pd.DataFrame,
        name="",
        selected: List[str] = None,
        *,
        savepath: str | Path = None,
        method: Literal["pearson", "spearman"] = "pearson",
        show=False,
    ):
        if name is None:
            name == "corr"
        if savepath is not None:
            savepath = Path(savepath)

        df = df.corr(method=method, numeric_only=True)

        logger.info(f"{method.upper()} CORRELATION MATRIX:\n%s", df.round(2))
        # Plotting the correlation matrix
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            df,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            square=True,
            cbar=True,
            linewidths=0.5,
        )
        plt.title(f"{method.capitalize()} Correlation Matrix")
        if savepath is not None:
            plt.savefig(savepath / f"corr_peason_{name}.png")
        plt.clf()

    def plot_solvent_zingg(
        df: pd.DataFrame,
        x_name: str = "ar1",
        y_name: str = "ar2",
        name: str = "",
        c: list = None,
        *,
        savepath: str | Path = None,
        show: bool = False,
    ):
        if c is None:
            c = [None]
            vmin = None
            cmap = None

        n_rows, n_cols = get_rows_cols(len(c))
        print(f"ROWS: {n_rows}, COLS: {n_cols}")
        # Create subplots
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 15))
        fig.suptitle(
            f"Zingg Plots Colored by Different Parameters [{name}]", fontsize=16
        )

        # Iterate through subplot axes and subplot titles
        for ax, param_title in zip(axes.flat, c):
            if param_title is not None:
                param_data = pd.to_numeric(df[param_title])
                # Handling the case of water
                vmin = 0 if param_data.min() == -1 else None
                cmap = "viridis"
                if param_title == "solubility":
                    param_title = "log[solubility (g/L)]"
                else:
                    param_title = param_title.capitalize()

                fig.colorbar(scatter, ax=ax, label=param_title)
                ax.set_title(f"{param_title.capitalize()}")

            scatter = ax.scatter(
                df["ar1"], df["ar2"], c=param_data, cmap=cmap, vmin=vmin
            )
            ax.axhline(y=2 / 3, color="blue", linestyle="--", label="2/3")
            ax.axvline(x=2 / 3, color="blue", linestyle="--", label="2/3")
            ax.set_xlim([0, 1])
            ax.set_ylim([0, 1])
            ax.set_xlabel("S:M")
            ax.set_ylabel("M:L")

        plt.tight_layout()
        if savepath is not None and Path(savepath).exists():
            plt.savefig(savepath / f"ZinggParams_{name}.png")

    def add_labels(
        solvents_to_show: List[str], ax, df: pd.DataFrame, x_name="ar1", y_name="ar2"
    ):
        # Add labels for selected solvents
        print("SOLVENTS TO SHOW: ", solvents_to_show)
        n = len(solvents_to_show)
        half = n // 2
        i = 0
        x = df[x_name]
        y = df[y_name]
        for index, row in df.iterrows():
            if not (solvents_to_show and row["solvent"] in solvents_to_show):
                continue

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

            i += 1

    def get_rows_cols(self, n):
        # Calculate the number of columns (n_cols) using square root of n
        n_cols = int(math.ceil(math.sqrt(n)))

        # Calculate the number of rows (n_rows)
        n_rows = int(math.ceil(n / n_cols))
        return n_rows, n_cols
