import ctypes

import numpy as np
import OpenGL.GL as gl  # python wrapping of OpenGL
import OpenGL.GLU as glu
from matplotlib import cm
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.GL import (GL_COMPILE, GL_RGBA, GL_TRIANGLES, GL_UNSIGNED_BYTE,
                       glBegin, glCallList, glEnd, glEndList, glGenLists,
                       glGetIntegerv, glNewList, glReadPixels, glVertex3f)
from OpenGL.GLU import gluNewQuadric, gluSphere
from OpenGL.GLUT import glutInit, glutSolidSphere, glutSwapBuffers
from PIL import Image
from PySide6 import QtCore, QtGui, QtOpenGL
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QFileDialog, QInputDialog

from crystalaspects.utils.shape_analysis import CrystalShape


class vis_GLWidget(QOpenGLWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rightMouseButtonPressed = False
        self.lastMousePosition = QtCore.QPoint()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.xyz_path_list = []
        self.sim_num = 0

        self.bg_colour = None
        self.xyz = None
        self.lastPos = None
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
        # self.object = 0
        self.zoomFactor = 0.5

        self.colour_picked = cm.viridis
        self.colour_type = 2

        self.point_size = 6.0
        self.bg_colours = ["#FFFFFF", "#000000", "#00000000"]
        self.point_types = ["Point", "Sphere"]
        self.point_type = "Point"
        self.texture = None
        self.tex_coords = None
        self.num_vertices = 8

        self.lattice_parameters = None

        """self.x_arrow_model = self.createArrow()
        self.y_arrow_model = self.createArrow()
        self.z_arrow_model = self.createArrow()"""

        self.cm_colourList = [
            cm.viridis,
            cm.plasma,
            cm.inferno,
            cm.magma,
            cm.cividis,
            cm.twilight,
            cm.twilight_shifted,
            cm.hsv,
        ]

    def createArrow(self):
        # Create a display list for the arrow
        arrow_model = gl.glGenLists(1)
        gl.glNewList(arrow_model, gl.GL_COMPILE)

        # Create a cone for the arrowhead
        gl.glPushMatrix()
        gl.glTranslate(0.0, 0.0, 1.0)
        GLU.gluCylinder(GLU.gluNewQuadric(), 0.5, 0.0, 1.0, 32, 1)
        gl.glPopMatrix()

        # Create a cylinder for the arrow shaft
        gl.glPushMatrix()
        gl.glTranslate(0.0, 0.0, 0.5)
        GLU.gluCylinder(GLU.gluNewQuadric(), 0.1, 0.1, 1.0, 32, 1)
        gl.glPopMatrix()

        # End the display list
        gl.glEndList()

        self.update()

        return arrow_model

    def pass_XYZ(self, xyz):
        self.xyz = xyz
        print("XYZ cordinates passed on OpenGL widget")

    def pass_XYZ_list(self, xyz_path_list):
        self.xyz_path_list = xyz_path_list
        print("XYZ file paths (list) passed to OpenGL widget")

    def get_XYZ_from_list(self, value):
        if self.sim_num != value:
            self.sim_num = value
            self.xyz, _, _ = CrystalShape.read_XYZ(self.xyz_path_list[value])
            self.initGeometry()

            self.update()

    def save_render_dialog(self):
        # Create a list of options for the dropdown menu
        options = ["640x480", "800x600", "1024x768", "1280x1024"]

        # Show the input dialog and get the index of the selected item
        resolution, ok = QInputDialog.getItem(
            self, "Select Resolution", "Resolution:", options, 0, False
        )

        file_name = None

        if ok:
            # User clicked "OK"
            # Show the save dialog and get the file name and path selected by the user
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save File", "", "Images (*.png)"
            )
        else:
            # User clicked "Cancel"
            return

        if file_name:
            # User selected a file name
            self.save_render(file_name, resolution)
        else:
            # User cancelled the save dialog
            pass

    def save_render(self, file_name, resolution):
        # Get the width and height of the viewport
        """viewport = ctypes.c_int * 4
        gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)
        viewport_width, viewport_height = viewport[2], viewport[3]
        width, height = map(
            int, resolution.split("x")
        )"""  # Split the resolution string and convert to integers

        # Calculate the x and y coordinates of the lower left corner of the region to read
        """x = (viewport_width - width) // 2
        y = (viewport_height - height) // 2

        # Read the pixel data from the framebuffer
        pixels = (ctypes.c_ubyte * (width * height * 4))()
        gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, pixels)

        # Create a QImage from the pixel data
        image = QImage(pixels, width, height, QImage.Format_RGBA8888)"""
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        viewport_width, viewport_height = viewport[2], viewport[3]
        width, height = map(int, resolution.split("x"))
        x = (viewport_width - width) // 2
        y = (viewport_height - height) // 2
        pixels = (ctypes.c_ubyte * (width * height * 4))()
        gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, pixels)
        image = Image.frombytes("RGBA", (width, height), pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # Save the QImage to a file
        image.save(file_name)

    def get_colour(self, value):
        self.colour_picked = self.cm_colourList[value]
        print(f" Colour selected: {self.colour_picked}")
        self.initGeometry()

        self.update()

    def get_bg_colour(self, value):
        self.bg_colour = self.bg_colours[value]
        print(f" Background Colour: {self.bg_colour}")
        self.qglClearColor(QtGui.QColor(self.bg_colour))

        self.update()

    def get_colour_type(self, value):
        self.colour_type = value
        print(f" Colour Mode: {value}")
        self.initGeometry()

        self.update()

    def get_point_type(self, value):
        pass
        # self.point_type = self.point_types[value]
        # print(f" Point Type: {self.point_types[value]}")
        # print(value)
        # self.initGeometry()
        # if value == 1:
        #     pcd_points = self.LoadVertices()
        #     self.draw_spheres(pcd_points)
        #     self.initGeometry()

        # self.update()

    def change_point_size(self, val):
        self.point_size = val
        print("point size", val)

        self.update()

    def zoomGL(self, val):
        print("zoom Factor", val)
        self.zoomFactor = val

        self.update()

    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def wheelEvent(self, event):
        scroll = event.angleDelta()
        if scroll.y() > 0:
            self.zoomFactor += 0.1
        else:
            self.zoomFactor -= 0.1
        self.update()

    def updateArrowModels(self, x1, y1, z1, x2, y2, z2):
        # Update the arrow models with the new coordinates
        glNewList(self.x_arrow_model, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        # Arrow base
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z2)
        glVertex3f(x2, y2, z2)
        # ...
        glEnd()
        glEndList()

        glNewList(self.y_arrow_model, GL_COMPILE)
        # ...

        glNewList(self.z_arrow_model, GL_COMPILE)
        # ...

    def mousePressEvent(self, event):
        self.lastMousePosition = event.pos()
        if event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressed = True

    def keyPressEvent(self, event):
        # print(f"Key pressed: {event.key()}")

        if event.key() == Qt.Key_W:
            self.rotX += 100
        if event.key() == Qt.Key_A:
            self.rotY -= 100
        if event.key() == Qt.Key_S:
            self.rotX -= 100
        if event.key() == Qt.Key_D:
            self.rotY -= 100

        if event.key() == Qt.Key_Up and Qt.KeyboardModifiers() & Qt.ShiftModifier:
            self.rotZ += 100
        if event.key() == Qt.Key_Down and Qt.KeyboardModifiers() & Qt.ShiftModifier:
            self.rotZ -= 100

        if event.key() == Qt.Key_Right:
            gl.glTranslate(100, 0.0, 0.0)
        if event.key() == Qt.Key_Left:
            gl.glTranslate(-100.0, 0.0, 0.0)
        if event.key() == Qt.Key_Down:
            gl.glTranslate(0.0, -100.0, 0.0)
        if event.key() == Qt.Key_Up:
            gl.glTranslate(0.0, 100.0, 0.0)

        self.update()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastMousePosition.x()
        dy = event.y() - self.lastMousePosition.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            # Rotation logic
            self.rotX += dy * 0.5  # Adjust these factors as needed
            self.rotY += dx * 0.5

        elif self.rightMouseButtonPressed:
            # Here we define the translation speed
            translationSpeed = 0.1
            self.translateScene(dx * translationSpeed, dy * translationSpeed)

        self.lastMousePosition = event.pos()
        self.update()

    def translateScene(self, dx, dy):
        print(f"Translating scene by dx: {dx}, dy: {dy}")  # Debugging print
        # Translation logic
        gl.glTranslatef(dx, dy, 0.0)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.rightMouseButtonPressed = False

    def initGeometry(self):
        vArrayv = self.LoadVertices()
        vArray = vArrayv.flatten()
        self.noPoints = len(vArray) // 6
        self.vbo = self.CreateBuffer(vArray)

        self.update()

    def setRotX(self, val):
        self.rotX = self.rotX + val

    def setRotY(self, val):
        self.rotY = self.rotY + val

    def setRotZ(self, val):
        self.rotZ = self.rotZ + val

    def LoadVertices(
        self,
    ):
        print("Loading Vertices")
        point_cloud = self.xyz
        print(".XYZ shape: ", point_cloud.shape[0])
        layers = point_cloud[:, 2]
        l_max = int(np.nanmax(layers[layers < 99]))

        # Loading the point cloud from file
        def vis_pc(xyz, color_axis=-1, C_Choice=self.colour_picked):
            pcd_points = xyz[:, 3:6]
            pcd_colors = None

            if color_axis >= 0:
                if color_axis == 3:
                    axis_vis = np.arange(0, xyz.shape[0], dtype=np.float32)
                else:
                    axis_vis = xyz[:, color_axis]

                pcd_colors = C_Choice(axis_vis / l_max)[:, 0:3]

            return (pcd_points, pcd_colors)

        points, colors = vis_pc(
            point_cloud, self.colour_type, C_Choice=self.colour_picked
        )

        points = np.asarray(points).astype("float32")
        colors = np.asarray(colors).astype("float32")

        attributes = np.concatenate((points, colors), axis=1)

        return attributes

    def create_sphere(self, radius, num_subdiv):
        quad = gluNewQuadric()
        glu.gluQuadricNormals(quad, glu.GLU_SMOOTH)
        glu.gluQuadricTexture(quad, gl.GL_TRUE)
        glu.gluSphere(quad, radius, num_subdiv, num_subdiv)

    def PointCloud(self):
        point_cloud = self.xyz
        points = point_cloud[:, 3:]

        return points

        # Drawing spheres

    def draw_spheres(self, points):
        print("Draw Spheres")
        print(points)
        radius = 0.1  # Sphere radius
        for p in points:
            gl.glTranslatef(p[0], p[1], p[2])
            glutSolidSphere(radius, 16, 16)
            gl.glTranslatef(-p[0], -p[1], -p[2])
        # gl.glPopMatrix()

    def CreateBuffer(self, attributes):
        bufferdata = (ctypes.c_float * len(attributes))(*attributes)  # float buffer
        buffersize = len(attributes) * 4  # buffer size in bytes

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, buffersize, bufferdata, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        return vbo

    def paintGL(self):
        # print("painting")
        # Clear the color and depth buffers
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Set up the transformations
        gl.glLoadIdentity()
        gl.glTranslate(0.0, 0.0, -50.0)
        gl.glScale(0.1 * self.zoomFactor, 0.1 * self.zoomFactor, 0.1 * self.zoomFactor)
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)

        # Set point size and enable point smoothing
        gl.glPointSize(self.point_size)
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Bind the VBO with the point cloud data
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        # Define the stride (size of each vertex in the VBO)
        stride = 6 * 4  # (24 bytes) : [x, y, z, r, g, b] * sizeof(float)

        # Enable and specify the vertex and color arrays
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(3, gl.GL_FLOAT, stride, None)

        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        offset = (
            3 * 4
        )  # (12 bytes) : the RGB color starts after the 3 coordinates x, y, z
        gl.glColorPointer(3, gl.GL_FLOAT, stride, ctypes.c_void_p(offset))

        # Draw the points
        noOfVertices = self.noPoints
        # print(noOfVertices)
        gl.glDrawArrays(gl.GL_POINTS, 0, noOfVertices)

        # Disable the arrays and unbind the VBO
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        if bool(glutSwapBuffers):
            glutSwapBuffers()
        else:
            print("glutSwapBuffers not available")
