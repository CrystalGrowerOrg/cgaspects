from unittest import skip
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QKeySequence

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality
from OpenGL.arrays import vbo
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import ctypes
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from colorsys import hls_to_rgb

from CrystalAspects.GUI.load_GUI import Ui_MainWindow
from CrystalAspects.tools.shape_analysis import CrystalShape


class Visualiser(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the init for the parent class
        self.setupUi(self)
        # self.initGUI
        self.xyz = None
        self.xyz_file_list = None

    def initGUI(self, xyz_file_list, xyz_list=[]):

        if xyz_file_list:
            self.xyz_file_list = xyz_file_list

            self.xyz = np.loadtxt(Path(self.xyz_file_list[0]), skiprows=2)
            print(self.xyz)

        self.glWidget = vis_GLWidget(self)
        self.glWidget.pass_XYZ(self.xyz)
        self.glWidget.updateGL
        self.gl_vLayout.addWidget(self.glWidget)
        self.colourList = [
            "Viridis",
            "Plasma",
            "Inferno",
            "Magma",
            "Cividis",
            "Twilight",
            "Twilight Shifted",
            "HSV",
        ]

        self.pointtype_comboBox.addItems([])
        self.colourmode_comboBox.addItems(
            ["Atom/Molecule Type", "Atom/Molecule Number", "Layer", "Single Colour"]
        )
        self.colourmode_comboBox.setCurrentIndex(2)
        self.colour_comboBox.addItems(self.colourList)
        self.bgcolour_comboBox.addItems(["White", "Black"])
        self.bgcolour_comboBox.setCurrentIndex(1)

        self.colour_comboBox.currentIndexChanged.connect(self.glWidget.get_colour)
        self.bgcolour_comboBox.currentIndexChanged.connect(self.glWidget.get_bg_colour)
        self.colourmode_comboBox.currentIndexChanged.connect(
            self.glWidget.get_colour_type
        )

        '''self.point_slider.setMinimum(1)
        self.point_slider.setMaximum(50)
        self.point_slider.setTickInterval(0.5)
        self.point_slider.valueChanged.connect(self.glWidget.change_point_size)'''
           
    def get_colour(self, value):
        print(value)

    def update_XYZ(self, XYZ_filepath):

        self.xyz = np.loadtxt(Path(XYZ_filepath), skiprows=2)
        self.glWidget.pass_XYZ(self.xyz)
        self.glWidget.initGeometry()
        self.glWidget.updateGL()


class vis_GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

        self.bg_colour = None
        self.xyz = None
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
        # self.object = 0
        self.zoomFactor = 1.0

        self.colour_picked = cm.viridis
        self.colour_type = 1

        self.point_size = 10
        self.bg_colours = ["#FFFFFF", "#000000"]
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

    def pass_XYZ(self, xyz):
        self.xyz = xyz
        print('XYZ cordinates passed on OpenGL widget(class)')
        print(self.xyz)

    def get_colour(self, value):

        self.colour_picked = self.cm_colourList[value]
        print(f" Colour selected: {self.colour_picked}")
        self.initGeometry()
        self.updateGL()

    def get_bg_colour(self, value):

        self.bg_colour = self.bg_colours[value]
        print(f" Background Colour: {self.bg_colour}")
        self.qglClearColor(QtGui.QColor(self.bg_colour))
        self.updateGL()

    def get_colour_type(self, value):

        self.colour_type = value
        print(f" Colour Mode: {value}")
        self.initGeometry()
        self.updateGL()

    def change_point_size(self, val):
        self.point_size = val
        print("connected", val)
        self.updateGL()

    def initializeGL(self):

        self.qglClearColor(QtGui.QColor("#000000"))  # initialize the screen to white
        gl.glEnable(gl.GL_DEPTH_TEST)  # enable depth testing

        self.initGeometry()

    def setRotX(self, val):
        self.rotX = self.rotX + val

    def setRotY(self, val):
        self.rotY = self.rotY + val

    def setRotZ(self, val):
        self.rotZ = val

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
            self.update()
        else:
            self.zoomFactor -= 0.1
            self.update()

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Adding Light

        # gl.glEnable(gl.GL_LIGHTING)
        """gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)"""

        # pushing matrix
        gl.glPushMatrix()  # push the current matrix to the current stack
        gl.glLoadIdentity()
        gl.glTranslate(
            0.0, 0.0, -50.0
        )  # third, translate cube to specified depth. Starting depth
        gl.glScale(0.1 * self.zoomFactor, 0.1 * self.zoomFactor, 0.1 * self.zoomFactor)
        # gl.glScale(20.0, 20.0, 20.0)       # second, scale cube
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)  # first, translate cube center to origin
        # gl.glCallList(self.object)

        # self.lastPos = QtCore.QtPoint()

        # Point size
        gl.glPointSize(
            self.point_size
        )
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_POINTS)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        stride = 6 * 4  # (24 bates) : [x, y, z, r, g, b] * sizeof(float)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(3, gl.GL_FLOAT, stride, None)

        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        # (12 bytes) : the rgb color starts after the 3 coordinates x, y, z
        offset = (3 * 4)  
        gl.glColorPointer(3, gl.GL_FLOAT, stride, ctypes.c_void_p(offset))

        # Drawing points
        noOfVertices = self.noPoints
        gl.glDrawArrays(gl.GL_POINTS, 0, noOfVertices)
        # Disabling Lighting
        """gl.glDisable(gl.GL_LIGHT0)
        gl.glDisable(gl.GL_LIGHTING)
        gl.glDisable(gl.GL_COLOR_MATERIAL)"""

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glPopMatrix()  # restore the previous modelview matrix

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def KeyPressed(self, event):
        print(event)
        if event.key() == Qt.Key.Key_W:
            print("Up")
            self.rotX += 100
            self.updateGL()

        if event.key() == Qt.Key.Key_A:
            print("Left")
            self.rotY -= 100
            self.updateGL()

            # self.setRotY(-1)
        if event.key() == Qt.Key.Key_S:
            print("Down")
            self.rotX -= 100
            self.updateGL()

        if event.key() == Qt.Key.Key_D:
            print("Right")
            self.rotY -= 100
            self.updateGL()

        self.updateGL()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.rotX = self.rotX + 1 * dy
            self.rotY = self.rotY + 1 * dx

        self.updateGL()

        # if event.buttons() & QtCore.Qt.ScrollPhase:
        #   self.setzoomFactor(self.zoomFactor + 0.1)

        self.lastPos = event.pos()

    def initGeometry(self):

        vArray = self.LoadVertices()
        self.noPoints = len(vArray) // 6
        # print("No. of Points: %s" % self.noPoints)

        self.vbo = self.CreateBuffer(vArray)

    def LoadVertices(self,):
        print('Load Vertices')
        print(self.xyz)
        point_cloud = self.xyz

        layers = point_cloud[:, 2]
        l_max = int(np.nanmax(layers[layers < 99]))

        # Loading the point cloud from file
        def vis_pc(xyz, color_axis=-1, C_Choice=self.colour_picked):
            pcd_points = xyz[:, 3:]
            pcd_colors = None

            if color_axis >= 0:
                if color_axis == 3:
                    axis_vis = np.arange(0, xyz.shape[0], dtype=np.float32)
                else:
                    axis_vis = xyz[:, color_axis]

                pcd_colors = C_Choice(axis_vis / l_max)[:, 0:3]

            return (pcd_points, pcd_colors)

        points, colors = vis_pc(
            point_cloud,
            self.colour_type,
            C_Choice=self.colour_picked
        )

        points = np.asarray(points).astype("float32")
        colors = np.asarray(colors).astype("float32")

        attributes = np.concatenate((points, colors), axis=1)

        return attributes.flatten()

    def CreateBuffer(self, attributes):
        bufferdata = (ctypes.c_float * len(attributes))(*attributes)  # float buffer
        buffersize = len(attributes) * 4  # buffer size in bytes

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, buffersize, bufferdata, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        return vbo
