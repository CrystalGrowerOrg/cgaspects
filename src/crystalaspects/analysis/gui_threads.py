import logging
import os
import re
from collections import namedtuple
from itertools import permutations
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import crystalaspects.analysis.ar_dataframes as ar
import crystalaspects.analysis.gr_dataframes as gr
import crystalaspects.fileio.find_data as fd
from crystalaspects.analysis.shape_analysis import CrystalShape

logger = logging.getLogger("CA:Threads")


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals:
    finished
        No data
    error
        tuple (exctype, value, traceback.format_exc() )
    result
        object data returned from processing, anything
    progress
        int indicating % progress
    """

    started = Signal()
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    location = Signal(object)
    progress = Signal(int)
    message = Signal(str)


class WorkerXYZ(QRunnable):
    def __init__(self, xyz):
        super(WorkerXYZ, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.xyz = xyz
        self.signals = WorkerSignals()
        self.shape = CrystalShape()

    @Slot()
    def run(self):
        self.shape.set_xyz(xyz_array=self.xyz)
        shape_info = self.shape.get_all()
        self.signals.progress.emit(100)
        self.signals.result.emit(shape_info)
        self.signals.message.emit("Calculations Complete!")
        self.signals.finished.emit()


class WorkerAspectRatios(QRunnable):
    def __init__(self, information, options, input_folder, output_folder):
        super(WorkerAspectRatios, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.information = information
        self.options = options
        self.plotting_csv = None

        self.signals = WorkerSignals()

    def run(self):
        self.output_folder = fd.create_aspects_folder(self.input_folder)
        self.signals.location.emit(self.output_folder)
        summary_file = self.information.summary_file
        folders = self.information.folders

        if not (
            self.options.selected_ar
            or (
                self.options.selected_cda
                and self.options.checked_directions
                and self.options.selected_directions
            )
        ):
            logger.error(
                "Condtions not met: AR AND/OR CDA (with checked AND selected directions)"
            )
            return

        if self.options.selected_ar:
            xyz_df = ar.collect_all(folder=self.input_folder, signals=self.signals)
            xyz_combine = xyz_df
            if summary_file:
                xyz_df = fd.summary_compare(summary_csv=summary_file, aspect_df=xyz_df)
            xyz_df_final_csv = self.output_folder / "aspectratio.csv"
            xyz_df.to_csv(xyz_df_final_csv, index=None)
            ar.get_xyz_shape_percentage(df=xyz_df, savefolder=self.output_folder)
            logger.info("Plotting CSV created from: PCA/OBA")
            self.plotting_csv = xyz_df_final_csv

        if self.options.selected_cda and not self.options.checked_directions:
            logger.warning(
                "You have selected CDA option but have not checked any directions used to collect length information."
                "Please set this and try again!"
            )
            return
        if self.options.selected_cda and not self.options.selected_directions:
            logger.warning(
                "You have selected CDA option but have not set the three directions used for aspect ratio calculations."
                "Please set this and try again!"
            )
            return

        if self.options.selected_cda:
            cda_df = ar.build_cda(
                folderpath=self.input_folder,
                folders=folders,
                directions=self.options.checked_directions,
                selected=self.options.selected_directions,
                savefolder=self.output_folder,
            )
            zn_df = ar.build_ratio_equations(
                directions=self.options.selected_directions,
                ar_df=cda_df,
                filepath=self.output_folder,
            )
            if summary_file:
                zn_df = fd.summary_compare(summary_csv=summary_file, aspect_df=zn_df)

            zn_df_final_csv = self.output_folder / "cda.csv"
            zn_df.to_csv(zn_df_final_csv, index=None)
            logger.info("Plotting CSV created from: CDA")
            self.plotting_csv = zn_df_final_csv

            if self.options.selected_ar and self.options.selected_cda:
                combined_df = fd.combine_xyz_cda(CDA_df=zn_df, XYZ_df=xyz_combine)
                final_cda_xyz_csv = self.output_folder / "crystalaspects.csv"
                combined_df.to_csv(final_cda_xyz_csv, index=None)
                ar.get_cda_shape_percentage(
                    df=combined_df, savefolder=self.output_folder
                )
                logger.info("Plotting CSV created from: CDA + PCA/OBA")
                self.plotting_csv = final_cda_xyz_csv

        self.signals.result.emit(self.plotting_csv)


class WorkerGrowthRates(QRunnable):
    def __init__(self, information, selected_directions):
        super(WorkerGrowthRates, self).__init__()
        self.information = information
        self.selected_directions = selected_directions

        self.signals = WorkerSignals()

    def run(self):
        growth_rate_df = gr.build_growthrates(
            size_file_list=self.information.size_files,
            supersat_list=self.information.supersats,
            directions=self.selected_directions,
            signals=self.signals,
        )

        self.signals.result.emit(growth_rate_df)


class WorkerMovies(QRunnable):
    def __init__(self, filepath):
        super(WorkerMovies, self).__init__()
        self.filepath = filepath
        self.signals = WorkerSignals()

    def run(self):
        results = namedtuple("CrystalXYZ", ("xyz", "xyz_movie"))

        self.signals.message.emit("Reading XYZ file. Please wait...")
        xyz, xyz_movie, progress = CrystalShape.read_XYZ(self.filepath)
        print(progress, end="\r")
        self.signals.progress.emit(progress)

        result = results(xyz=xyz, xyz_movie=xyz_movie)

        self.signals.result.emit(result)
        self.signals.message.emit("Reading XYZ Complete!")
        self.signals.finished.emit()
