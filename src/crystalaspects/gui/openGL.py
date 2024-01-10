import ctypes
import logging

import numpy as np
from matplotlib import cm
from OpenGL.GL import GL_DEPTH_TEST, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT
from PIL import Image
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtOpenGL import QOpenGLDebugLogger, QOpenGLFramebufferObject
from PySide6.QtWidgets import QFileDialog, QInputDialog

from crystalaspects.analysis.shape_analysis import CrystalShape
from crystalaspects.gui.point_cloud_renderer import (
    SimplePointRenderer,
)
from crystalaspects.gui.camera import Camera

logger = logging.getLogger("CA:OpenGL")


class VisualisationWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rightMouseButtonPressed = False
        self.lastMousePosition = QtCore.QPoint()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.camera = Camera()

        self.xyz_path_list = []
        self.sim_num = 0
        self.vbo = None
        self.point_cloud_renderer = SimplePointRenderer()

        self.xyz = None
        self.lastPos = None
        # self.object = 0

        self.colormap = cm.viridis
        self.colour_type = 2

        self.point_size = 6.0
        self.backgroundColors = ["#FFFFFF", "#000000", "#000000"]
        self.backgroundColor = QColor(self.backgroundColors[0])
        self.point_types = ["Point", "Sphere"]
        self.point_type = "Point"
        self.texture = None
        self.tex_coords = None
        self.num_vertices = 8

        self.lattice_parameters = None

        self.availableColormaps = [
            cm.viridis,
            cm.plasma,
            cm.inferno,
            cm.magma,
            cm.cividis,
            cm.twilight,
            cm.twilight_shifted,
            cm.hsv,
        ]

    def pass_XYZ(self, xyz):
        self.xyz = xyz
        logger.info("XYZ cordinates passed on OpenGL widget")

    def pass_XYZ_list(self, xyz_path_list):
        self.xyz_path_list = xyz_path_list
        logger.info("XYZ file paths (list) passed to OpenGL widget")

    def get_XYZ_from_list(self, value):
        if self.sim_num != value:
            self.sim_num = value
            self.xyz, _, _ = CrystalShape.read_XYZ(self.xyz_path_list[value])
            self.initGeometry()

            self.update()

    def save_render_dialog(self):
        # Create a list of options for the dropdown menu
        options = ["1x", "2x", "4x"]

        # Show the input dialog and get the index of the selected item
        resolution, ok = QInputDialog.getItem(
            self, "Select Resolution", "Resolution:", options, 0, False
        )

        file_name = None

        if ok:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "Images (*.png)"
            )
            if file_name:
                self.save_render(file_name, resolution)

    def renderToImage(self, scale):
        self.makeCurrent()
        w = self.width() * scale
        h = self.height() * scale
        gl = self.context().functions()
        gl.glViewport(0, 0, w, h)
        fbo = QOpenGLFramebufferObject(
            w, h, QOpenGLFramebufferObject.CombinedDepthStencil
        )

        fbo.bind()
        gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(gl)
        fbo.release()
        result = fbo.toImage()
        self.doneCurrent()
        return result

    def save_render(self, file_name, resolution):
        image = self.renderToImage(float(resolution[0]))
        image.save(file_name)

    def updateSelectedColormap(self, value):
        self.colormap = self.availableColormaps[value]
        logger.debug("Colour selected: %s", self.colormap)
        self.initGeometry()

        self.update()

    def updateBackgroundColor(self, value=0):
        self.backgroundColor = self.backgroundColors[value]
        logger.debug("Background Colour: %s", self.backgroundColor)

        color = QColor(self.backgroundColor)
        if not color.isValid():
            logger.warning("Error: Invalid color code")
            return
        gl = self.context().functions()
        gl.glClearColor(color.redF(), color.greenF(), color.blueF(), 1)
        self.update()

    def updateColorType(self, value):
        self.colour_type = value
        logger.debug("Colour Mode: %s", value)
        self.initGeometry()

        self.update()

    def get_point_type(self, value):
        pass

    def updatePointSize(self, val):
        self.point_size = float(val)
        logger.debug("point size, %s", self.point_size)
        self.update()

    def resizeGL(self, width, height):
        super().resizeGL(width, height)
        self.aspect_ratio = width / float(height)

    def wheelEvent(self, event):
        degrees = event.angleDelta() / 8

        steps = degrees.y() / 15

        self.camera.zoom(steps)
        self.update()

    def mousePressEvent(self, event):
        self.lastMousePosition = event.pos()
        if event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressed = True

    def keyPressEvent(self, event):
        # print(f"Key pressed: {event.key()}")

        dx, dy = 0, 0

        if event.key() == Qt.Key_W:
            dy -= 10
        if event.key() == Qt.Key_S:
            dy += 10

        if event.key() == Qt.Key_A:
            dx -= 10
        if event.key() == Qt.Key_D:
            dx += 10

        self.camera.orbit(dx, dy)
        self.update()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastMousePosition.x()
        dy = event.y() - self.lastMousePosition.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            # Rotation logic
            self.camera.orbit(dx, dy)

        elif self.rightMouseButtonPressed:
            self.camera.pan(-dx, dy)  # Negate dx to get correct direction

        self.lastMousePosition = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressed = False

    def initGeometry(self):
        varray = self.updatePointCloudVertices()
        self.point_cloud_renderer.setPoints(varray)
        self.update()

    def updatePointCloudVertices(self):
        logger.debug("Loading Vertices")
        point_cloud = self.xyz
        logger.debug(".XYZ shape: %s", point_cloud.shape[0])
        layers = point_cloud[:, 2]
        l_max = int(np.nanmax(layers[layers < 99]))

        # Loading the point cloud from file
        def vis_pc(xyz, color_axis=-1):
            pcd_points = xyz[:, 3:6]
            pcd_colors = None

            if color_axis >= 0:
                if color_axis == 3:
                    axis_vis = np.arange(0, xyz.shape[0], dtype=np.float32)
                else:
                    axis_vis = xyz[:, color_axis]

                pcd_colors = self.colormap(axis_vis / l_max)[:, 0:3]

            return (pcd_points, pcd_colors)

        points, colors = vis_pc(point_cloud, self.colour_type)

        points = np.asarray(points).astype("float32")
        colors = np.asarray(colors).astype("float32")

        attributes = np.concatenate((points, colors), axis=1)

        return attributes

    def initializeGL(self):
        print(f"Initialized OpenGL: {self.context().format().version()}")
        self.logger = QOpenGLDebugLogger(self.context())
        if self.logger.initialize():
            self.logger.startLogging(QOpenGLDebugLogger.DebugLogging)
            self.logger.messageLogged.connect(self.handleLoggedMessage)
        else:
            ext = self.context().hasExtension(QtCore.QByteArray("GL_KHR_debug"))
            print(f"Debug logger not initialized, have extension: {ext}")

        color = self.backgroundColor
        gl = self.context().functions()
        gl.glEnable(GL_DEPTH_TEST)
        gl.glClearColor(color.redF(), color.greenF(), color.blueF(), 1)

    def handleLoggedMessage(self, message):
        print(
            f"Source: {message.source()}, Type: {message.type()}, Message: {message.message()}"
        )

    def draw(self, gl):
        mvp = self.camera.modelViewProjectionMatrix(self.aspect_ratio)
        if self.point_cloud_renderer.numberOfPoints() > 0:
            self.point_cloud_renderer.bind()
            self.point_cloud_renderer.setUniforms(
                **{"u_modelViewProjectionMat": mvp, "u_pointSize": self.point_size}
            )

            self.point_cloud_renderer.draw(gl)
            self.point_cloud_renderer.release()

            self.point_cloud_renderer.bind()

    def paintGL(self):
        gl = self.context().functions()
        gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(gl)
