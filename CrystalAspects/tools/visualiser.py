from CrystalAspects.GUI.load_GUI import Ui_MainWindow
from CrystalAspects.tools.openGL import vis_GLWidget


class Visualiser(Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(Visualiser, self).__init__(*args, **kwargs)

        self.xyz = None
        self.movie = None
        self.colour_list = []
        self.xyz_file_list = []
        self.frame_list = []

    def initGUI(self, xyz_file_list):

        self.xyz_file_list = [str(path) for path in xyz_file_list]
        tot_sims = "Unassigned"

        self.glWidget = vis_GLWidget()

        print(xyz_file_list)
        self.fname_comboBox.addItems(self.xyz_file_list)
        self.glWidget.pass_XYZ_list(xyz_file_list)
        self.fname_comboBox.currentIndexChanged.connect(self.glWidget.get_XYZ_from_list)
        self.saveFrame_button.clicked.connect(self.glWidget.save_render_dialog)
        self.fname_comboBox.currentIndexChanged.connect(self.update_vis_sliders)
        self.run_xyz_movie(xyz_file_list[0])
        #self.gl_vLayout.addWidget(self.glWidget)

        tot_sims = len(self.xyz_file_list)
        self.total_sims_label.setText(str(tot_sims))

        self.colour_list = [
            "Viridis",
            "Plasma",
            "Inferno",
            "Magma",
            "Cividis",
            "Twilight",
            "Twilight Shifted",
            "HSV",
        ]

        self.colourmode_comboBox.addItems(
            ["Atom/Molecule Type", "Atom/Molecule Number", "Layer", "Single Colour"]
        )
        self.pointtype_comboBox.addItems(["Points", "Spheres"])
        self.colourmode_comboBox.setCurrentIndex(2)
        self.colour_comboBox.addItems(self.colour_list)
        self.bgcolour_comboBox.addItems(["White", "Black", "Transparent"])
        self.bgcolour_comboBox.setCurrentIndex(1)

        self.colour_comboBox.currentIndexChanged.connect(self.glWidget.get_colour)
        self.bgcolour_comboBox.currentIndexChanged.connect(self.glWidget.get_bg_colour)
        self.pointtype_comboBox.currentIndexChanged.connect(
            self.glWidget.get_point_type
        )
        self.colourmode_comboBox.currentIndexChanged.connect(
            self.glWidget.get_colour_type
        )

        self.point_slider.setMinimum(1)
        self.point_slider.setMaximum(50)
        self.point_slider.setValue(10)
        self.point_slider.valueChanged.connect(self.glWidget.change_point_size)
        self.zoom_slider.valueChanged.connect(self.glWidget.zoomGL)
        self.mainCrystal_slider.setMinimum(0)
        self.mainCrystal_slider.setMaximum(tot_sims)
        self.mainCrystal_slider.setTickInterval(1)
        self.mainCrystal_slider.valueChanged.connect(self.glWidget.get_XYZ_from_list)
        self.mainCrystal_slider.valueChanged.connect(self.update_vis_sliders)
        self.vis_simnum_spinBox.setMinimum(0)
        self.vis_simnum_spinBox.setMaximum(tot_sims)
        self.vis_simnum_spinBox.valueChanged.connect(self.glWidget.get_XYZ_from_list)
        self.vis_simnum_spinBox.valueChanged.connect(self.update_vis_sliders)
        self.show_info_button.clicked.connect(lambda: self.update_XYZ_info(self.xyz))

    def init_crystal(self, result):
        self.xyz, self.movie = result
        self.glWidget.pass_XYZ(self.xyz)

        if self.movie:
            self.frame_list = self.movie.keys()
            print("Frames: ", self.frame_list)
            self.current_frame_comboBox.addItems(
                [f"frame_{frame + 1}" for frame in self.frame_list]
            )
            self.current_frame_spinBox.setMinimum(0)
            self.current_frame_spinBox.setMaximum(len(self.frame_list))
            self.frame_slider.setMinimum(0)
            self.frame_slider.setMaximum(len(self.frame_list))
            self.current_frame_comboBox.currentIndexChanged.connect(self.update_movie)
            self.current_frame_spinBox.valueChanged.connect(self.update_movie)
            self.frame_slider.valueChanged.connect(self.update_movie)
            self.play_button.clicked.connect(self.play_movie)

        try:
            self.glWidget.initGeometry()
        except AttributeError:
            print("No Crystal Data Found!")

    def update_frame(self, frame):
        self.xyz = self.movie[frame]
        self.glWidget.pass_XYZ(self.xyz)

        try:
            self.glWidget.initGeometry()
            self.glWidget.updateGL()
        except AttributeError:
            print("No Crystal Data Found!")

    def update_XYZ(self, XYZ_filepath):

        self.run_xyz_movie(XYZ_filepath)
        self.glWidget.pass_XYZ(self.xyz)

        try:
            self.glWidget.initGeometry()
            self.glWidget.updateGL()
        except AttributeError:
            print("No Crystal Data Found!")
