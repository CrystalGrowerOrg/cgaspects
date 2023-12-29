from collections import namedtuple

from PySide6.QtCore import QObject, QRunnable, Signal, Slot
from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA

from crystalaspects.analysis.aspect_ratios import AspectRatio
from crystalaspects.analysis.growth_rates import GrowthRate
from crystalaspects.visualisation.plot_data import Plotting
from crystalaspects.fileio.find_data import *
from crystalaspects.analysis.shape_analysis import CrystalShape


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

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
    message = Signal(str)


class Worker_XYZ(QRunnable):
    def __init__(self, xyz):
        super(Worker_XYZ, self).__init__()
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


class Worker_Calc(QRunnable):
    def __init__(self, calc_info_tuple):
        super(Worker_Calc, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.folder_path = calc_info_tuple.folder_path
        self.checked_directions = calc_info_tuple.checked_directions
        self.selected_directions = calc_info_tuple.selected_directions
        self.summary_file = calc_info_tuple.summary_file
        self.folders = calc_info_tuple.folders
        self.aspectratio = calc_info_tuple.aspectratio
        self.cda = calc_info_tuple.cda
        self.pca = calc_info_tuple.pca
        self.growthrates = calc_info_tuple.growthrates
        self.sa_vol = calc_info_tuple.sa_vol
        # self.plot = calc_info_tuple.plot

        self.signals = WorkerSignals()

    def run(self):
        plotting = Plotting()

        save_folder = create_aspects_folder(self.folder_path)

        """Creating crystalaspects folder"""

        self.signals.message.emit("Calculations Initiated!")
        self.signals.progress.emit(10)

        if self.growthrates:
            growth = GrowthRate()
            growth_df = growth.run_calc_growth(
                self.folder_path,
                directions=self.checked_directions,
                savefolder=save_folder,
            )

            self.signals.message.emit("Growth Rate Calculations complete!")

        if self.sa_vol and self.pca is False:
            aspect_ratio = AspectRatio()
            sa_vol_ratio_df = aspect_ratio.sa_vol_ratio_calc(
                subfolder=self.folder_path, savefolder=save_folder
            )
            sa_vol_ratio_df_final = summary_compare(
                summary_csv=self.summary_file,
                aspect_df=sa_vol_ratio_df,
                savefolder=save_folder,
            )
            self.signals.message.emit("SA:Vol Calculations complete!")
            """if self.plot:
                plotting.SAVAR_plot(df=sa_vol_ratio_df_final, folderpath=save_folder)
                self.signals.message.emit("Plotting SA:Vol Results!")"""

        if self.pca and self.sa_vol:
            aspect_ratio = AspectRatio()
            pca_df = aspect_ratio.shape_all(
                subfolder=self.folder_path, savefolder=save_folder
            )
            plot_df = summary_compare(
                summary_csv=self.summary_file, aspect_df=pca_df, savefolder=save_folder
            )
            final_df = plot_df
            self.signals.message.emit("PCA & SA:Vol Calculations complete!")

            if self.plot:
                plotting.SAVAR_plot(df=plot_df, folderpath=save_folder)
                plotting.build_PCAZingg(df=plot_df, folderpath=save_folder)
                self.signals.message.emit("Plotting PCA & SA:Vol Results!")

        if self.aspectratio:
            aspect_ratio = AspectRatio()
            print(self.checked_directions)

            if self.cda:
                cda_df = aspect_ratio.build_AR_CDA(
                    folderpath=self.folder_path,
                    folders=self.folders,
                    directions=self.checked_directions,
                    selected=self.selected_directions,
                    savefolder=save_folder,
                )

                zn_df = aspect_ratio.defining_equation(
                    directions=self.selected_directions,
                    ar_df=cda_df,
                    filepath=save_folder,
                )
                zn_df_final = summary_compare(
                    summary_csv=self.summary_file,
                    aspect_df=zn_df,
                    savefolder=save_folder,
                )
                final_df = zn_df_final
                self.signals.message.emit("CDA Calculations complete!")

                """if self.plot:
                    plotting.CDA_Plot(df=zn_df_final, folderpath=save_folder)
                    plotting.build_zingg_seperated_i(
                        df=zn_df_final, folderpath=save_folder
                    )
                    plotting.Aspect_Extended_Plot(
                        df=zn_df_final,
                        selected=self.selected_directions,
                        folderpath=save_folder,
                    )
                    self.signals.message.emit("Plotting CDA Results!")"""

            if self.pca and self.sa_vol:
                aspect_ratio.PCA_shape_percentage(pca_df=pca_df, folderpath=save_folder)

            if self.pca and self.sa_vol is False:
                pca_df = aspect_ratio.build_AR_PCA(
                    subfolder=self.folder_path, savefolder=save_folder
                )
                final_df = pca_df
                self.signals.message.emit("PCA Calculations complete!")

                aspect_ratio.PCA_shape_percentage(pca_df=pca_df, folderpath=save_folder)
                """if self.plot:
                    self.signals.message.emit("Plotting PCA Results!")
                    plotting.build_PCAZingg(df=pca_df, folderpath=save_folder)"""

            if self.pca and self.cda:
                pca_cda_df = aspect_ratio.Zingg_CDA_shape_percentage(
                    pca_df=pca_df, cda_df=zn_df, folderpath=save_folder
                )
                self.signals.message.emit("PCA & CDA Calculations complete!")
                """if self.plot:
                    self.signals.message.emit("Plotting PCA & CDA Results!")
                    plotting.PCA_CDA_Plot(df=pca_cda_df, folderpath=save_folder)
                    plotting.build_PCAZingg(df=pca_df, folderpath=save_folder)"""

        self.signals.progress.emit(100)
        self.signals.message.emit(
            "Complete! Please open the output folder at {}".format(str(save_folder))
        )
        self.signals.finished.emit()


class Worker_Movies(QRunnable):
    def __init__(self, filepath):
        super(Worker_Movies, self).__init__()
        self.filepath = filepath
        self.signals = WorkerSignals()

    def run(self):
        results = namedtuple("CrystalXYZ", ("xyz", "xyz_movie"))

        self.signals.message.emit("Reading XYZ file. Please wait...")
        xyz, xyz_movie, progress = CrystalShape.read_XYZ(self.filepath)
        print(progress)
        self.signals.progress.emit(progress)

        result = results(xyz=xyz, xyz_movie=xyz_movie)

        self.signals.result.emit(result)
        self.signals.message.emit("Reading XYZ Complete!")
        self.signals.finished.emit()
