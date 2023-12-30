from crystalaspects.gui.load_ui import Ui_MainWindow
from crystalaspects.gui.openGL import vis_GLWidget


class Visualiser(Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xyz = None
        self.movie = None
        self.colour_list = []
        self.xyz_file_list = []
        self.frame_list = []

    def initGUI(self, xyz_file_list):
        self.openglwidget = vis_GLWidget()
        self.xyz_file_list = [str(path) for path in xyz_file_list]
        tot_sims = "Unassigned"

        # Check if the layout has any widgets
        if self.gl_vLayout.count() > 0:
            # Get the item at index 0 (the first and only widget in this case)
            widget_item = self.gl_vLayout.itemAt(0)
            # Check if the widget_item is valid
            if widget_item:
                widget = widget_item.widget()
                # Check if the widget is valid
                if widget:
                    # Remove the widget from the layout
                    self.gl_vLayout.removeWidget(widget)
                    # Delete the widget
                    widget.deleteLater()

        # Clear all lists
        self.colour_list = []
        self.colourmode_comboBox.clear()
        self.pointtype_comboBox.clear()
        self.bgcolour_comboBox.clear()

        print(xyz_file_list)

        # self.run_xyz_movie(xyz_file_list[0])
        self.gl_vLayout.addWidget(self.openglwidget)
        tot_sims = len(self.xyz_file_list)

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
            [
                "Atom/Molecule Type",
                "Atom/Molecule Number",
                "Layer",
                "Single Colour",
                "Site Number",
                "Particle Energy",
            ]
        )
        self.pointtype_comboBox.addItems(["Points", "Spheres"])
        self.colourmode_comboBox.setCurrentIndex(2)
        self.colour_comboBox.addItems(self.colour_list)
        self.bgcolour_comboBox.addItems(["White", "Black", "Transparent"])
        self.bgcolour_comboBox.setCurrentIndex(1)

        self.colour_comboBox.currentIndexChanged.connect(self.openglwidget.get_colour)
        self.bgcolour_comboBox.currentIndexChanged.connect(
            self.openglwidget.get_bg_colour
        )
        self.pointtype_comboBox.currentIndexChanged.connect(
            self.openglwidget.get_point_type
        )
        self.colourmode_comboBox.currentIndexChanged.connect(
            self.openglwidget.get_colour_type
        )

        self.fname_comboBox.addItems(self.xyz_file_list)
        self.openglwidget.pass_XYZ_list(xyz_file_list)
        self.fname_comboBox.currentIndexChanged.connect(
            self.openglwidget.get_XYZ_from_list
        )
        self.fname_comboBox.currentIndexChanged.connect(self.update_xyz_slider)
        self.saveFrame_button.clicked.connect(self.openglwidget.save_render_dialog)
        self.point_slider.setMinimum(1)
        self.point_slider.setMaximum(50)
        self.point_slider.setValue(10)
        self.point_slider.valueChanged.connect(self.openglwidget.change_point_size)
        self.zoom_slider.valueChanged.connect(self.openglwidget.zoomGL)
        self.xyz_horizontalSlider.setMinimum(0)
        self.xyz_horizontalSlider.setMaximum(tot_sims - 1)
        self.xyz_horizontalSlider.setTickInterval(1)
        self.xyz_horizontalSlider.valueChanged.connect(
            self.openglwidget.get_XYZ_from_list
        )
        self.xyz_horizontalSlider.valueChanged.connect(self.update_xyz_slider)
        self.xyz_spinBox.setMinimum(0)
        self.xyz_spinBox.setMaximum(tot_sims - 1)
        self.xyz_spinBox.valueChanged.connect(self.openglwidget.get_XYZ_from_list)
        self.xyz_spinBox.valueChanged.connect(self.update_xyz_slider)
        self.show_info_button.clicked.connect(lambda: self.update_XYZ_info(self.openglwidget.xyz))

    def init_crystal(self, result):
        print("INIT CRYSTAL", result)
        self.xyz, self.movie = result
        self.openglwidget.pass_XYZ(self.xyz)

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
            self.play_button.clicked.connect(lambda: self.play_movie(self.frame_list))

        try:
            self.openglwidget.initGeometry()
        except AttributeError:
            print("No Crystal Data Found!")

    def update_frame(self, frame):
        self.xyz = self.movie[frame]
        self.openglwidget.pass_XYZ(self.xyz)

        try:
            self.openglwidget.initGeometry()
            self.openglwidget.update()
        except AttributeError:
            print("No Crystal Data Found!")

    def update_XYZ(self):
        self.openglwidget.pass_XYZ(self.xyz)

        try:
            self.openglwidget.initGeometry()
        except AttributeError:
            print("No Crystal Data Found!")

    def close_opengl_widget(self):
        if self.current_viewer:
            # Remove the OpenGL widget from its parent layout
            self.viewer_container_layout.removeWidget(self.current_viewer)

            # Delete the widget from memory
            self.current_viewer.deleteLater()
            self.current_viewer = None  # Reset the active viewer
