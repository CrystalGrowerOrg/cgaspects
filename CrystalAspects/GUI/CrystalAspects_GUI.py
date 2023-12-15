# PyQT5 imports
from PyQt5 import QtGui, QtWidgets, QtOpenGL
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, \
    QShortcut, QAction, \
    QMenu, QFileDialog, QDialog
from PyQt5.QtCore import Qt, QThreadPool, QTimer
from PyQt5.QtGui import QKeySequence
from qt_material import apply_stylesheet

# General imports
import os, sys
from natsort import natsorted
from collections import namedtuple

# Project Module imports
from CrystalAspects.GUI.load_GUI import Ui_MainWindow
from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.tools.shape_analysis import AspectRatioCalc, CrystalShape
from CrystalAspects.tools.visualiser import Visualiser
from CrystalAspects.tools.crystal_slider import create_slider
from CrystalAspects.GUI.gui_threads import Worker_XYZ, Worker_Movies
from CrystalAspects.visualisation.plot_data import Plotting
from CrystalAspects.visualisation.replotting import PlottingDialogue
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.data.CalculateAspectRatios import AnalysisOptionsDialog
from CrystalAspects.data.GrowthRateCalc import GrowthRateAnalysisDialogue

basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        apply_stylesheet(app, theme="dark_cyan.xml")

        self.setupUi(self)
        self.statusBar().showMessage("CrystalGrower Data Processor v1.0")

        self.threadpool = QThreadPool()
        self.change_style(theme_main="dark", theme_colour="teal")

        self.welcome_message()
        self.key_shortcuts()
        self.connect_buttons()
        self.init_parameters()
        self.MenuBar()

    def MenuBar(self):
        # Create a menu bar
        menu_bar = self.menuBar()

        # Create two menus
        file_menu = QMenu("File", self)
        edit_menu = QMenu("Edit", self)
        CrystalAspects_menu = QMenu('CrystalAspects', self)
        CrystalClear_menu = QMenu("CrystalClear", self)
        Calculations_menu = QMenu('Calculations', self)

        # Add menus to the menu bar
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(CrystalAspects_menu)
        menu_bar.addMenu(CrystalClear_menu)

        # Create actions for the File menu
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        import_action = QAction("Import", self)
        exit_action = QAction("Exit", self)

        # Add actions to the File menu
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(import_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Connect actions from the File menu
        import_action.triggered.connect(self.import_XYZ)

        # Create actions for the Edit menu
        cut_action = QAction("Cut", self)
        copy_action = QAction("Copy", self)
        paste_action = QAction("Paste", self)

        # Add actions to the Edit menu
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)

        # Create actions to the CrystalAspects menu
        aspect_ratio_action = QAction("Aspect Ratio", self)
        growth_rate_action = QAction("Growth Rates", self)
        #plotting_action = QAction("Plotting", self)
        particle_swarm_action = QAction("Particle Swarm Analysis", self)
        #docking_calc_action = QAction("Docking Calculation", self)

        # Add actions and Submenu to CrystalAspects menu
        calculate_menu = CrystalAspects_menu.addMenu("Calculate")
        calculate_menu.addAction(aspect_ratio_action)
        calculate_menu.addAction(growth_rate_action)
        CrystalAspects_menu.addAction(particle_swarm_action)
        #CrystalAspects_menu.addAction(plotting_action)
        #CrystalAspects_menu.addAction(docking_calc_action)

        # Connect the CrystalAspects actions
        aspect_ratio_action.triggered.connect(self.calculate_aspect_ratio)
        growth_rate_action.triggered.connect(self.calculate_growth_rates)
        particle_swarm_action.triggered.connect(self.particle_swarm_analysis)
        #docking_calc_action.triggered.connect(self.docking_calc)

        # Create the CrystalClear actions
        generate_structure_action = QAction("Generate Structure", self)
        generate_net_action = QAction("Generate Net", self)
        solvent_screen_action = QAction("Solvent Screening", self)

        # Add action and Submenu to CrystalClear menu
        CrystalClear_menu.addAction(generate_structure_action)
        CrystalClear_menu.addAction(generate_net_action)
        CrystalClear_menu.addAction(solvent_screen_action)

        # Connect the CrystalClear actions
        generate_structure_action.triggered.connect(self.generate_structure_file)
        generate_net_action.triggered.connect(self.generate_net_file)
        solvent_screen_action.triggered.connect(self.solvent_screening)

    def change_style(self, theme_main, theme_colour, density=-1):

        extra = {
            # Font
            "font_family": "Roboto",
            # Density Scale
            "density_scale": str(density),
        }

        apply_stylesheet(
            app, f"{theme_main}_{theme_colour}.xml", invert_secondary=False, extra=extra
        )

    def init_parameters(self):
        # Initialise CrystalViewer and Widget
        '''self.viewer = Visualiser()
        self.gl_vLayout.addWidget(self.viewer)'''

        # Set up a timer to refresh the OpenGL widget at regular intervals
        timer = QTimer(self)
        #timer.timeout.connect(self.viewer.update)
        timer.start(16)  # About 60 FPS

    def key_shortcuts(self):
        # Create a QShortcut with the specified key sequence
        close = QShortcut(QKeySequence("Ctrl+Q"), self)
        # Create a QShortcut with Command+Q as the key sequence (for macOS)
        close_shortcut = QShortcut(QKeySequence(Qt.MetaModifier + Qt.Key_Q), self)
        close_shortcut.activated.connect(self.close_application)
        # Open read folder
        self.openKS = QShortcut(QKeySequence("Ctrl+O"), self)
        '''try:
            self.openKS.activated.connect(lambda: self.read_folder(self.mode))
        except IndexError:
            pass
        # Open output folder'''
        self.open_outKS = QShortcut(QKeySequence("Ctrl+Shift+O"), self)
        '''try:
            self.open_outKS.activated.connect(self.output_folder_button)
        except IndexError:
            pass'''
        # Import XYZ file
        importXYZ = QShortcut(QKeySequence("Ctrl+I"), self)
        importXYZ.activated.connect(self.import_XYZ)

    def welcome_message(self):
        print("############################################")
        print("####        CrystalAspects v1.00        ####")
        print("############################################")
        print("Created by Nathan de Bruyn & Alvin J. Walisinghe")

    def import_XYZ(self):
        ''' Import XYZ file(s) by first opening the folder
        and then opening them via an OpenGL widget'''
        self.folder = None
        self.xyz_files = []
        # Prompt the user to select the folder
        slider = create_slider()
        folder, xyz_files = slider.read_crystals()
        self.folder = folder
        print(f"Initial XYZ list: {xyz_files}")
        # Check if the user opened a folder
        if folder:
            self.xyz_files = natsorted(xyz_files)  # Use natsort to sort naturally, this is a list of all paths

            # Generate a complete list of the number of .xyz files and/or frames in the movie
            self.xyz_info_list = slider.get_xyz_info_for_all_files(folder, xyz_files)
            xyz_info_list = self.xyz_info_list
            print("xyz_info_list", xyz_info_list)

            Visualiser.initGUI(self, self.xyz_files) # Load the info into init_GUI

            # Shape analysis to determine xyz, or xyz movie
            result = self.movie_or_single_frame(0)

            # Adjust the slider range based on the number of XYZ files in the list
            self.mainCrystal_slider.setRange(0, len(xyz_files) - 1)
            self.mainCrystal_slider.setValue(0)

            Visualiser.init_crystal(self, result)

            # self.xyz, _, _ = XYZ_data.read_XYZ(folder)

            # self.run_xyz_movie(self.xyz)
            #CrystalViewer.init_crystal(self, crystal_results)
            # Enable the slider
            self.select_summary_slider_button.setEnabled(True)

            print("importing XYZ files")

    def run_xyz_movie(self, filepath):
        worker_xyz_movie = Worker_Movies(filepath)
        worker_xyz_movie.signals.result.connect(self.get_xyz_movie)
        worker_xyz_movie.signals.progress.connect(self.update_progress)
        worker_xyz_movie.signals.message.connect(self.update_statusbar)
        worker_xyz_movie.signals.finished.connect(
            lambda: Visualiser.init_crystal(self, result=self.xyz_result)
        )
        self.threadpool.start(worker_xyz_movie)

    def get_xyz_movie(self, result):
        self.xyz_result = result

    def update_movie(self, frame):
        Visualiser.update_frame(self, frame)
        self.current_frame_comboBox.setCurrentIndex(frame)
        self.current_frame_spinBox.setValue(frame)
        self.frame_slider.setValue(frame)

    def play_movie(self, frames):
        for frame in range(frames):
            Visualiser.update_frame(self, frame)
            self.current_frame_comboBox.setCurrentIndex(frame)
            self.current_frame_spinBox.setValue(frame)
            self.frame_slider.setValue(frame)

    def update_XYZ_info(self, xyz):

        worker_xyz = Worker_XYZ(xyz)
        worker_xyz.signals.result.connect(self.insert_info)
        worker_xyz.signals.progress.connect(self.update_progress)
        worker_xyz.signals.message.connect(self.update_statusbar)
        self.threadpool.start(worker_xyz)

    def movie_or_single_frame(self, index):
        folder = self.folder
        if 0 <= index < len(self.xyz_files):
            file_name = self.xyz_files[index]
            full_file_path = os.path.join(folder, file_name)
            results = namedtuple("CrystalXYZ", ("xyz", "xyz_movie"))
            xyz, xyz_movie, progress = CrystalShape.read_XYZ(full_file_path)
            result = results(xyz=xyz, xyz_movie=xyz_movie)

            return result

    def load_crystal(self, index):
        aspect = AspectRatioCalc()
        crystalshape = CrystalShape()
        folder = self.folder
        print(folder)
        if 0 <= index < len(self.xyz_files):
            file_name = self.xyz_files[index]
            full_file_path = os.path.join(folder, file_name)
            atoms = crystalshape.read_XYZ(full_file_path)  # Assuming read_XYZ is in MainWindow
            print(atoms)
            self.viewer.atoms = atoms
            self.viewer.update()

            return atoms

    def on_slider_value_changed(self, value):
        # Check if the selected index is within the range of available XYZ files
        if 0 <= value < len(self.crystals_data):
            self.current_crystal_index = value
            self.viewer.atoms = self.crystals_data[self.current_crystal_index]
            self.viewer.update()

    def close_application(self):
        print("Closing Application")
        self.close()

    def connect_buttons(self):
        # Visualisation Buttons
        self.select_summary_slider_button.clicked.connect(lambda: self.read_summary_vis())
        self.play_button.clicked.connect(self.play_movie)

    def calculate_aspect_ratio(self):
        # Prompt the user to select the folder
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "./", QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        find = Find()
        # Check if the user selected a folder

        if folder:
            # Perform calculations using the selected folder

            # Read the information from the selected folder
            information = find.find_info(folder)

            # Get the directions from the information
            checked_directions = information.directions
            print(checked_directions)

            # Create the analysis options dialog
            dialog = AnalysisOptionsDialog(checked_directions)
            if dialog.exec_() == QDialog.Accepted:
                # Retrieve the selected options
                selected_aspect_ratio, selected_cda, selected_directions, selected_direction_aspect_ratio, auto_plotting = dialog.get_options()

                # Display the information in a QMessageBox
                QMessageBox.information(self, "Options",
                                        f"Selected Aspect Ratio: {selected_aspect_ratio}\n"
                                        f"Selected CDA: {selected_cda}\n"
                                        f"Selected Directions: {selected_directions}\n"
                                        f"Selected Direction Aspect Ratio: {selected_direction_aspect_ratio}\n"
                                        f"Auto Plotting: {auto_plotting}")
                print('selected aspect ratio:', selected_direction_aspect_ratio)
                AspectXYZ = AspectRatioCalc()
                aspect_ratio = AspectRatio()
                plotting = Plotting()
                save_folder = find.create_aspects_folder(folder)
                file_info = find.find_info(folder)
                summary_file = file_info.summary_file
                folders = file_info.folders

                if selected_aspect_ratio:
                    xyz_df = AspectXYZ.collect_all(folder=folder)
                    xyz_combine = xyz_df
                    if summary_file:
                        xyz_df = find.summary_compare(
                            summary_csv=summary_file,
                            aspect_df=xyz_df
                        )
                    xyz_df_final_csv = f"{save_folder}/AspectRatio.csv"
                    xyz_df.to_csv(xyz_df_final_csv, index=None)
                    AspectXYZ.shape_number_percentage(
                        df=xyz_df,
                        savefolder=save_folder
                    )
                    plotting_csv = xyz_df_final_csv
                    if auto_plotting is True:
                        plotting.build_PCAZingg(csv=xyz_df_final_csv,
                                                folderpath=save_folder)
                        plotting.plot_OBA(csv=xyz_df_final_csv,
                                          folderpath=save_folder)
                        plotting.SAVAR_plot(csv=xyz_df_final_csv,
                                            folderpath=save_folder)

                if selected_cda:
                    cda_df = aspect_ratio.build_AR_CDA(
                        folderpath=folder,
                        folders=folders,
                        directions=selected_directions,
                        selected=selected_direction_aspect_ratio,
                        savefolder=save_folder,
                    )
                    zn_df = aspect_ratio.defining_equation(
                        directions=selected_direction_aspect_ratio,
                        ar_df=cda_df,
                        filepath=save_folder,
                    )
                    if summary_file:
                        zn_df = find.summary_compare(
                            summary_csv=summary_file,
                            aspect_df=zn_df
                        )
                    zn_df_final_csv = f"{save_folder}/CDA.csv"
                    zn_df.to_csv(zn_df_final_csv, index=None)
                    plotting_csv = zn_df_final_csv
                    if auto_plotting is True:
                        plotting.Aspect_Extended_Plot(csv=zn_df_final_csv,
                                                      folderpath=save_folder,
                                                      selected=selected_direction_aspect_ratio)
                        plotting.CDA_Plot(csv=zn_df_final_csv,
                                          folderpath=save_folder)

                    if selected_aspect_ratio and selected_cda:
                        combined_df = find.combine_XYZ_CDA(
                            CDA_df=zn_df,
                            XYZ_df=xyz_combine
                        )
                        '''if summary_file:
                            combined_df = find.summary_compare(
                                summary_csv=summary_file,
                                aspect_df=combined_df
                            )'''
                        final_cda_xyz_csv = f"{save_folder}/CrystalAspects.csv"
                        combined_df.to_csv(final_cda_xyz_csv, index=None)
                        #self.ShowData(final_cda_xyz)
                        aspect_ratio.CDA_Shape_Percentage(
                            df=combined_df,
                            savefolder=save_folder
                        )
                        plotting_csv = final_cda_xyz_csv
                        if auto_plotting is True:
                            plotting.PCA_CDA_Plot(csv=final_cda_xyz_csv,
                                                  folderpath=save_folder)
                            plotting.build_CDA_OBA(csv=final_cda_xyz_csv,
                                                   folderpath=save_folder)

                PlottingDialogues = PlottingDialogue(self)
                PlottingDialogues.plotting_info(
                    csv=plotting_csv,
                    plotting=''
                )
                PlottingDialogues.exec_()

    def calculate_growth_rates(self):
        ''' Activate calculate growth rates from the CrystalAspects
        menubar after growth rates has been selected'''
        # Prompt the user to select the folder
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "./", QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        find = Find()

        # Check if the user selected a folder
        if folder:
            # Perform calculations using the selected folder
            QMessageBox.information(self, "Result", f"Growth rates calculated for the folder: {folder}")

            # Read the information from the selected folder
            information = find.find_info(folder)

            # Get the directions from the information
            checked_directions = information.directions

            growth_rate_dialog = GrowthRateAnalysisDialogue(checked_directions)
            if growth_rate_dialog.exec_() == QDialog.Accepted:
                selected_directions = growth_rate_dialog.selected_directions
                auto_plotting = growth_rate_dialog.plotting_checkbox.isChecked()

                save_folder = find.create_aspects_folder(folder)
                size_files = information.size_files
                supersats = information.supersats
                directions = selected_directions

                growth_rate = GrowthRate()

                growth_rate_df = growth_rate.calc_growth_rate(
                    size_file_list=size_files, supersat_list=supersats, directions=directions
                )
                print(growth_rate_df)
                growth_rate_csv = f"{save_folder}/GrowthRates.csv"
                growth_rate_df.to_csv(growth_rate_csv, index=None)
                PlottingDialogues = PlottingDialogue(self)
                PlottingDialogues.plotting_info(
                    csv=growth_rate_csv,
                    plotting='Growth Rates'
                )
                PlottingDialogues.exec_()
                if auto_plotting:
                    plot = Plotting()
                    plot.plot_growth_rates(growth_rate_df, directions, save_folder)

    def particle_swarm_analysis(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Particle Swarm Analysis")
        msg_box.setText("Particle Swarm Analysis is coming soon!")
        msg_box.exec_()

    def generate_structure_file(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("CrystalClear is coming soon!")
        msg_box.exec_()

    def generate_net_file(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("CrystalClear is coming soon!")
        msg_box.exec_()

    def solvent_screening(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("CrystalClear is coming soon!")
        msg_box.exec_()

    def docking_calc(self):
        # Create a message box
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Docking for growth modifier and impurities is coming soon!")
        msg_box.exec_()

    def read_summary_vis(self):
        print('Entering Reading Summary file')
        create_slider.read_summary(self)

    def get_xyz_movie(self, result):
        self.xyz_result = result

    def slider_change(self, var, slider_list, dspinbox_list, summ_df, crystals):
        slider = self.sender()
        i = 0
        for name in slider_list:
            if name == slider:
                slider_value = name.value()
                print(slider_value)
                dspinbox_list[i].setValue(slider_value / 100)
            i += 1
        value_list = []
        filter_df = summ_df
        for i in range(var):
            value = slider_list[i].value() / 100
            print(f"locking for: {value}")
            filter_df = filter_df[(summ_df.iloc[:, i] == value)]
            value_list.append(value)
        print("Combination: ", value_list)
        print(filter_df)
        for row in filter_df.index:
            XYZ_file = crystals[row]
            self.output_textBox_3.append(f"Row Number: {row}")
            self.update_progress(0)
            Visualiser.update_XYZ(self, XYZ_file)

    def dspinbox_change(self, var, dspinbox_list, slider_list):
        dspinbox = self.sender()
        i = 0
        for name in dspinbox_list:
            if name == dspinbox:
                dspinbox_value = name.value()
                print(dspinbox_value)
                slider_list[i].setValue(int(dspinbox_value * 100))
            i += 1
        value_list = []
        for i in range(var):
            value = dspinbox_list[i].value()
            value_list.append(value)
        print(value_list)

    def update_vis_sliders(self, value):
        print(value)
        self.fname_comboBox.setCurrentIndex(value)
        self.mainCrystal_slider.setValue(value)
        self.vis_simnum_spinBox.setValue(value)
        self.frame_slider.setValue(value)

    def insert_info(self, result):

        print("Inserting data to GUI!")
        aspect1 = result.aspect1
        aspect2 = result.aspect2
        shape_class = "Unassigned"

        if aspect1 >= 2 / 3:
            if aspect2 >= 2 / 3:
                shape_class = "Block"
            else:
                shape_class = "Needle"
        if aspect1 <= 2 / 3:
            if aspect2 <= 2 / 3:
                shape_class = "Lath"
            else:
                shape_class = "Plate"

        self.sm_label.setText("Small/Medium: {:.2f}".format(aspect1))
        self.ml_label.setText("Medium/Long: {:.2f}".format(aspect2))
        self.shape_label.setText(f"General Shape: {shape_class}")
        self.crystal_sa_label.setText(
            "Crystal Surface Area (nm^2): {:2g}".format(result.surface_area)
        )
        self.crystal_vol_label.setText(
            "Crystal Volume (nm^3): {:2g}".format(result.volume)
        )
        self.crystal_savol_label.setText(
            "Surface Area/Volume: {:2g}".format(result.sa_vol)
        )

    def update_progress(self, progress):
        self.progressBar.setValue(progress)

    def update_statusbar(self, status):
        self.statusBar().showMessage(status)

    def thread_finished(self):
        print("THREAD COMPLETED!")

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    # Override sys excepthook to prevent app abortion upon any error
    sys.excepthook = except_hook

    # Setting taskbar icon permissions - windows
    try:
        import ctypes

        appid = "CNM.CrystalGrower.DataProcessor.v1.0"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except:
        pass

    # Set up OpenGL format with the necessary attributes
    gl_format = QtOpenGL.QGLFormat()
    gl_format.setVersion(3, 3)  # Use OpenGL 3.3 or higher
    gl_format.setProfile(QtOpenGL.QGLFormat.CoreProfile)
    gl_format.setSampleBuffers(True)

    # Create the OpenGL context and make it current
    gl_context = QtOpenGL.QGLContext(gl_format)
    gl_context.create()
    gl_context.makeCurrent()

    # ############# Runs the application ############## #
    QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "icon.png")))
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

