import imp
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

from scipy.spatial import ConvexHull
from sklearn.decomposition import PCA
from collections import namedtuple

from CrystalAspects.data.find_data import Find
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.data.growth_rates import GrowthRate

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker_XYZ(QRunnable):
    def __init__(self, xyz):
        super(Worker_XYZ, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.xyz = xyz
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        pca = PCA(n_components=3)
        pca.fit(self.xyz)
        pca_svalues = pca.singular_values_

        self.signals.progress.emit(15)

        hull = ConvexHull(self.xyz)
        vol_hull = hull.volume
        SA_hull = hull.area
        sa_vol = SA_hull / vol_hull

        self.signals.progress.emit(50)

        small, medium, long = sorted(pca_svalues)

        aspect1 = small / medium
        aspect2 = medium / long

        shape_info_tuple = namedtuple('Shape_info', 'aspect1, aspect2, surface_area, volume, sa_vol')
        
        shape_info = shape_info_tuple(
            aspect1=aspect1,
            aspect2=aspect2,
            surface_area=SA_hull,
            volume=vol_hull,
            sa_vol=sa_vol
        )
        self.signals.progress.emit(100)
        
        self.signals.result.emit(shape_info)
        self.signals.finished.emit()

    
class Worker_Calc(QRunnable):
    def __init__(self, calc_info_tuple):
        super(Worker_Calc, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.folder_path = calc_info_tuple.folder_path
        self.checked_directions = calc_info_tuple.checked_directions
        self.summary_file = calc_info_tuple.summary_file
        self.cda = calc_info_tuple.cda
        self.pca = calc_info_tuple.pca
        self.growthrates = calc_info_tuple.growthrates
        self.sa_vol = calc_info_tuple.sa_vol
        self.plot = calc_info_tuple.plot

        self.signals = WorkerSignals()

        


