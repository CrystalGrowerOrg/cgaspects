from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5.QtWidgets import QMainWindow
from CrystalAspects.GUI.load_GUI import Ui_MainWindow


class Sliders(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setupUi(self)

    def update_vis_sliders(self, value):
        print(value)
        self.fname_comboBox.setCurrentIndex(value)
        self.mainCrystal_slider.setValue(value)
        self.vis_simnum_spinBox.setValue(value)
