import logging

from crystalaspects.gui.load_ui import Ui_MainWindow
from crystalaspects.gui.dialogs import settings_ui
from crystalaspects.gui.openGL import vis_GLWidget
from crystalaspects.gui.dialogs.settings import SettingsDialog

logger = logging.getLogger("CA:Visualiser")


class Visualiser(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.xyz = None
        self.movie = None
        self.colour_list = []
        self.xyz_file_list = []
        self.frame_list = []
        self.settings_dialog = SettingsDialog()


    
