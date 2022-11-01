from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
import numpy as np
from collections import namedtuple
import logging

from CrystalAspects.data.find_data import Find
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.visualisation.plot_data import Plotting
from CrystalAspects.tools.shape_analysis import CrystalShape

logger = logging.getLogger("CrystalAspects_Logger")


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

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    message = pyqtSignal(str)


class Worker_XYZ(QRunnable):
    def __init__(self, xyz):
        super(Worker_XYZ, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.xyz = xyz
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):

        centered = self.xyz - np.mean(self.xyz, axis=0)
        norm = np.linalg.norm(centered, axis=1).max()
        centered /= norm

        pca = PCA(n_components=3)
        pca.fit(centered)
        pca_svalues = pca.singular_values_

        self.signals.progress.emit(15)
        self.signals.message.emit("PCA Calulcated! Please wait..")

        hull = ConvexHull(centered)
        vol_hull = hull.volume
        SA_hull = hull.area
        sa_vol = SA_hull / vol_hull

        self.signals.progress.emit(50)
        self.signals.message.emit("Surface Area and Volume done!")

        small, medium, long = sorted(pca_svalues)

        aspect1 = small / medium
        aspect2 = medium / long

        shape_info_tuple = namedtuple(
            "Shape_info", "aspect1, aspect2, surface_area, volume, sa_vol"
        )

        shape_info = shape_info_tuple(
            aspect1=aspect1,
            aspect2=aspect2,
            surface_area=SA_hull,
            volume=vol_hull,
            sa_vol=sa_vol,
        )
        self.signals.progress.emit(100)
        self.signals.result.emit(shape_info)
        self.signals.message.emit(
            "Calculations Complete! Please wait till the data is displayed!"
        )
        self.signals.finished.emit()


class Worker_Calc(QRunnable):
    def __init__(self, calc_info_tuple):
        super(Worker_Calc, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.folder_path = calc_info_tuple.folder_path
        self.checked_directions = calc_info_tuple.checked_directions
        self.summary_file = calc_info_tuple.summary_file
        self.aspectratio = calc_info_tuple.aspectratio
        self.cda = calc_info_tuple.cda
        self.pca = calc_info_tuple.pca
        self.growthrates = calc_info_tuple.growthrates
        self.sa_vol = calc_info_tuple.sa_vol
        self.plot = calc_info_tuple.plot

        self.signals = WorkerSignals()

    def run(self):

        logger.info("All Selected Directions: %s\n", self.checked_directions)

        find = Find()
        plotting = Plotting()

        save_folder = find.create_aspects_folder(self.folder_path)

        """Creating CrystalAspects folder"""
        logger.debug("Filepath read: %s", str(self.folder_path))
        logger.debug("CrystalAspects folder created: %s", str(save_folder))

        self.signals.message.emit("Calculations Initiated!")
        self.signals.progress.emit(10)

        if self.growthrates:
            growth = GrowthRate()
            growth.run_calc_growth(
                self.folder_path,
                directions=self.checked_directions,
                plotting=self.plot,
                savefolder=save_folder,
            )

            self.signals.message.emit("Growth Rate Calculations complete!")

        if self.sa_vol and self.pca is False:
            aspect_ratio = AspectRatio()
            savar_df = aspect_ratio.savar_calc(
                subfolder=self.folder_path, savefolder=save_folder
            )
            savar_df_final = find.summary_compare(
                summary_csv=self.summary_file,
                aspect_df=savar_df,
                savefolder=save_folder,
            )
            self.signals.message.emit("SA:Vol Calculations complete!")
            if self.plot:
                plotting.SAVAR_plot(df=savar_df_final, folderpath=save_folder)
                self.signals.message.emit("Plotting SA:Vol Results!")

        if self.pca and self.sa_vol:
            aspect_ratio = AspectRatio()
            pca_df = aspect_ratio.shape_all(
                subfolder=self.folder_path, savefolder=save_folder
            )
            plot_df = find.summary_compare(
                summary_csv=self.summary_file, aspect_df=pca_df, savefolder=save_folder
            )
            self.signals.message.emit("PCA & SA:Vol Calculations complete!")

            if self.plot:
                plotting.SAVAR_plot(df=plot_df, folderpath=save_folder)
                plotting.build_PCAZingg(df=plot_df, folderpath=save_folder)
                self.signals.message.emit("Plotting PCA & SA:Vol Results!")

        if self.aspectratio:
            aspect_ratio = AspectRatio()

            if self.cda:

                long = self.long_facet.currentText()
                medium = self.medium_facet.currentText()
                short = self.short_facet.currentText()

                selected_directions = [short, medium, long]

                logger.info(
                    "Selected Directions (for CDA): %s, %s, %s\n", short, medium, long
                )

                cda_df = aspect_ratio.build_AR_CDA(
                    folderpath=self.folder_path,
                    folders=self.folders,
                    directions=self.checked_directions,
                    selected=selected_directions,
                    savefolder=save_folder,
                )

                zn_df = aspect_ratio.defining_equation(
                    directions=selected_directions, ar_df=cda_df, filepath=save_folder
                )
                zn_df_final = find.summary_compare(
                    summary_csv=self.summary_file,
                    aspect_df=zn_df,
                    savefolder=save_folder,
                )
                self.signals.message.emit("CDA Calculations complete!")

                if self.plot:
                    plotting.CDA_Plot(df=zn_df_final, folderpath=save_folder)
                    plotting.build_zingg_seperated_i(
                        df=zn_df_final, folderpath=save_folder
                    )
                    plotting.Aspect_Extended_Plot(
                        df=zn_df_final,
                        selected=selected_directions,
                        folderpath=save_folder,
                    )
                    self.signals.message.emit("Plotting CDA Results!")

            if self.pca and self.sa_vol:
                aspect_ratio.PCA_shape_percentage(pca_df=pca_df, folderpath=save_folder)

            if self.pca and self.sa_vol is False:
                pca_df = aspect_ratio.build_AR_PCA(
                    subfolder=self.folder_path, savefolder=save_folder
                )
                self.signals.message.emit("PCA Calculations complete!")

                aspect_ratio.PCA_shape_percentage(pca_df=pca_df, folderpath=save_folder)
                if self.plot:
                    self.signals.message.emit("Plotting PCA Results!")
                    plotting.build_PCAZingg(df=pca_df, folderpath=save_folder)

            if self.pca and self.cda:
                pca_cda_df = aspect_ratio.Zingg_CDA_shape_percentage(
                    pca_df=pca_df, cda_df=zn_df, folderpath=save_folder
                self.signals.message.emit("PCA & CDA Calculations complete!")
                )
                if self.plot:
                    self.signals.message.emit("Plotting PCA & CDA Results!")
                    plotting.PCA_CDA_Plot(df=pca_cda_df, folderpath=save_folder)
                    plotting.build_PCAZingg(df=pca_df, folderpath=save_folder)

        self.signals.progress.emit(100)
        self.signals.message.emit(
            "Complete! Please open the output folder at {}".format(str(save_folder))
        )
        self.signals.finished.emit()


class Worker_Movies(QRunnable):
    def __init__(self, filepath):
        super(Worker_XYZ, self).__init__()
        self.filepath = filepath
        self.signals = WorkerSignals()

    def run(self):


        results = namedtuple("CrystalXYZ",
            "xyz",
            "xyz_movie"
        )

        self.signals.message.emit("Reading XYZ file. Please wait...")
        xyz, xyz_movie = CrystalShape.read_XYZ(self.filepath)
        result = results(xyz=xyz, xyz_movie=xyz_movie)

        self.signals.result.emit(result)
        self.signals.message.emit("Reading XYZ Complete!")
        self.signals.progress.emit(100)
        self.signals.finished.emit()

class Run_Thread:
    def __init__(self) -> None:
        pass
    def run_xyz(self, filepath):
        worker = Worker_Movies()

        worker_xyz_movie = worker(filepath)
        worker_xyz_movie.signals.result.connect(self.get_result)
        worker_xyz_movie.signals.progress.connect(self.update_progress)
        worker_xyz_movie.signals.message.connect(self.update_statusbar)
        self.threadpool.start(worker_xyz_movie)

    def get_result(self, result):
        return result





