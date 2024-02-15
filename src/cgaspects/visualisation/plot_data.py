# Standard library imports
import logging
from pathlib import Path

# Third-party library imports
import matplotlib
import matplotlib.pyplot as plt
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

    # def plot_cda(self, csv="", df="", folderpath="./outputs", i_plot=False):
    #     if csv != "":
    #         folderpath = Path(csv).parents[0]
    #         df = pd.read_csv(csv)

    #     zn_df = df
    #     savefolder = self.create_plots_folder(folderpath)

    #     x_data = zn_df["S:M"]
    #     y_data = zn_df["M:L"]

    #     plt.figure()
    #     plt.scatter(x_data, y_data, s=1.2)
    #     plt.xlabel("S:M")
    #     plt.ylabel("M:L")
    #     savepath = savefolder / "cda_zingg"
    #     logger.info("Plotting CDA FIG")
    #     plt.savefig(savepath, dpi=300)
    #     plt.close()

    #     interactions = [
    #         col
    #         for col in df.columns
    #         if col.startswith("interaction") or col.startswith("tile")
    #     ]

    #     for interaction in interactions:
    #         plt.figure()
    #         c_df = df[interaction]
    #         colour = list(set(c_df))
    #         textstr = interaction
    #         props = dict(boxstyle="square", facecolor="white")

    #         plt.figure()
    #         plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
    #         plt.axhline(y=0.66, color="black", linestyle="--")
    #         plt.axvline(x=0.66, color="black", linestyle="--")
    #         plt.title(textstr)
    #         plt.xlabel("S:M")
    #         plt.ylabel("M:L")
    #         plt.xlim(0.0, 1.0)
    #         plt.ylim(0.0, 1.0)
    #         cbar = plt.colorbar(ticks=colour)
    #         cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
    #         savepath = savefolder / f"cda_zingg_{interaction}"
    #         logger.info("Plotting CDA FIG for %s", interaction)
    #         plt.savefig(savepath, dpi=300)
    #         plt.close()

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
