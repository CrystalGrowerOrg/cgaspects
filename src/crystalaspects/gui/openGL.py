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
from crystalaspects.gui.point_cloud_renderer import SimplePointRenderer
from crystalaspects.gui.axes_renderer import AxesRenderer
# from crystalaspects.gui.sphere_renderer import SphereRenderer

from crystalaspects.gui.camera import Camera
from crystalaspects.gui.widgets.overlay_widget import TransparentOverlay

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
        self.point_cloud_renderer = None
        self.sphere_renderer = None
        self.axes_renderer = None

        self.xyz = None
        # self.object = 0

        self.colormap = "Viridis"
        self.color_by = "Layer"

        self.viewInitialized = False
        self.point_size = 6.0
        self.point_type = "Point"
        self.backgroundColor = QColor(Qt.white)

        self.overlay = TransparentOverlay(self)
        self.overlay.setGeometry(self.geometry())

        self.lattice_parameters = None

        self.availableColormaps = {
            "Viridis": cm.viridis,
            "Cividis": cm.cividis,
            "Plasma": cm.plasma,
            "Inferno": cm.inferno,
            "Magma": cm.magma,
            "Twilight": cm.twilight,
            "HSV": cm.hsv,
        }

        self.columnLabelToIndex = {
            "Atom/Molecule Type": 0,
            "Atom/Molecule Number": 1,
            "Layer": 2,
            "Single Colour": 3,
            "Site Number": 6,
            "Particle Energy": 7,
        }

        self.availableColumns = {}

    def pass_XYZ(self, xyz):
        self.xyz = xyz
        logger.debug("XYZ coordinates passed on OpenGL widget")

    def pass_XYZ_list(self, xyz_path_list):
        self.xyz_path_list = xyz_path_list
        logger.info("XYZ file paths (list) passed to OpenGL widget")

    def get_XYZ_from_list(self, value):
        if self.sim_num != value:
            self.sim_num = value
            self.xyz, _, _ = CrystalShape.read_XYZ(self.xyz_path_list[value])
            self.initGeometry()

            self.update()

    def saveRenderDialog(self):
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
                self.saveRender(file_name, resolution)

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

    def saveRender(self, file_name, resolution):
        image = self.renderToImage(float(resolution[0]))
        image.save(file_name)

    def setBackgroundColor(self, color):
        self.backgroundColor = QColor(color)
        self.makeCurrent()
        gl = self.context().functions()
        gl.glClearColor(color.redF(), color.greenF(), color.blueF(), 1)
        self.doneCurrent()

    def updateSettings(self, **kwargs):
        if not kwargs:
            return

        def present_and_changed(key, prev_val):
            return (key in kwargs) and (prev_val != kwargs[key])

        needs_reinit = False
        if present_and_changed("Color Map", self.colormap):
            self.colormap = kwargs["Color Map"]
            needs_reinit = True

        if present_and_changed("Background Color", self.backgroundColor):
            color = kwargs["Background Color"]
            self.setBackgroundColor(color)

        if present_and_changed("Color By", self.color_by):
            self.color_by = kwargs.get("Color By", self.color_by)
            needs_reinit = True

        if present_and_changed("Point Size", self.point_size):
            self.point_size = float(kwargs["Point Size"])

        if present_and_changed("Projection", self.camera.projectionMode()):
            self.camera.setProjectionMode(kwargs["Projection"])

        if needs_reinit:
            self.initGeometry()

        self.update()

    def resizeGL(self, width, height):
        super().resizeGL(width, height)
        self.aspect_ratio = width / float(height)
        self.screen_size = width, height

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.geometry())

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
        if self.point_cloud_renderer is None:
            return

        varray = self.updatePointCloudVertices()
        self.point_cloud_renderer.setPoints(varray)
        # self.sphere_renderer.setPoints(varray)
        self.update()

    def updatePointCloudVertices(self):
        logger.debug("Loading Vertices")
        logger.debug(".XYZ shape: %s", self.xyz.shape[0])
        layers = self.xyz[:, 2]
        max_layers = int(np.nanmax(layers[layers < 99]))

        # Loading the point cloud from file
        def vis_pc(xyz, color_axis=-1):
            pcd_points = xyz[:, 3:6]
            pcd_colors = None

            if color_axis >= 0:
                
                if color_axis == 3:
                    axis_vis = np.arange(0, xyz.shape[0], dtype=np.float32)
                else:
                    axis_vis = xyz[:, color_axis]

                if color_axis == 2:
                    min_val = 1
                    max_val = max_layers
                else:
                    min_val = np.nanmin(axis_vis)
                    max_val = np.nanmax(axis_vis)
                
                # Avoid division by zero in case all values are the same
                range_val = max_val - min_val if max_val != min_val else 1
                
                normalized_axis_vis = (axis_vis - min_val) / range_val

                pcd_colors = self.availableColormaps[self.colormap](
                    normalized_axis_vis
                )[:, 0:3]

            return (pcd_points, pcd_colors)

        points, colors = vis_pc(self.xyz, self.columnLabelToIndex[self.color_by])

        if not self.viewInitialized:
            self.camera.fitToObject(points)
            self.viewInitialized = True

        points = np.asarray(points).astype("float32")
        colors = np.asarray(colors).astype("float32")

        try:
            attributes = np.concatenate((points, colors), axis=1)

            return attributes
        except ValueError as exc:
            logger.error(
                "%s\n XYZ %s POINTS %s COLORS %s TYPE %s",
                exc,
                self.xyz.shape,
                points.shape,
                colors.shape,
                self.color_by,
            )
            return

    def initializeGL(self):
        logger.debug(
            "Initialized OpenGL, version info: %s", self.context().format().version()
        )
        debug = False
        if debug:
            self.logger = QOpenGLDebugLogger(self.context())
            if self.logger.initialize():
                self.logger.messageLogged.connect(self.handleLoggedMessage)
            else:
                ext = self.context().hasExtension(QtCore.QByteArray("GL_KHR_debug"))
                logger.debug(
                    "Debug logger not initialized, have extension GL_KHR_debug: %s", ext
                )

        color = self.backgroundColor
        gl = self.context().extraFunctions()
        self.point_cloud_renderer = SimplePointRenderer()
        # self.sphere_renderer = SphereRenderer(gl)
        self.axes_renderer = AxesRenderer()
        gl.glEnable(GL_DEPTH_TEST)
        gl.glClearColor(color.redF(), color.greenF(), color.blueF(), 1)

    def handleLoggedMessage(self, message):
        logger.debug(
            "Source: %s, Type: %s, Message: %s",
            message.source(),
            message.type(),
            message.message(),
        )

    def draw(self, gl):
        from PySide6.QtGui import QMatrix4x4, QVector2D

        mvp = self.camera.modelViewProjectionMatrix(self.aspect_ratio)
        view = self.camera.viewMatrix()
        axes = QMatrix4x4()
        screen_size = QVector2D(*self.screen_size)

        if self.point_cloud_renderer.numberOfPoints() > 0:
            self.point_cloud_renderer.bind()
            self.point_cloud_renderer.setUniforms(
                **{
                    "u_modelViewProjectionMat": mvp,
                    "u_pointSize": self.point_size,
                    "u_axesMat": axes,
                }
            )

            self.point_cloud_renderer.draw(gl)
            self.point_cloud_renderer.release()

        self.axes_renderer.bind()
        self.axes_renderer.setUniforms(
            **{
                "u_viewMat": view,
                "u_axesMat": axes,
                "u_screenSize": screen_size,
            }
        )

        self.axes_renderer.draw(gl)
        self.axes_renderer.release()

    def paintGL(self):
        gl = self.context().extraFunctions()
        gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw(gl)
