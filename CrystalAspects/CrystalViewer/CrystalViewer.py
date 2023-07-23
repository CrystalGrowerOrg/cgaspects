import sys
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5 import QtOpenGL, QtCore
from PyQt5.QtCore import Qt
import OpenGL.GL as gl
from OpenGL.GL import *
from OpenGL.GLUT import *

class CrystalViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.atoms = []  # List to store the atoms data from XYZ file

        # XYZ positions for mouse movements
        self.lastPos = None
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
        # self.object = 0
        self.zoomFactor = 1.0

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10, 10, -10, 10, -10, 10)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glPointSize(3.0)  # Set the size of the points

        glColor3f(1.0, 1.0, 1.0)  # Set the color of the points to white

        gl.glScale(0.1 * self.zoomFactor, 0.1 * self.zoomFactor, 0.1 * self.zoomFactor)

        glBegin(GL_POINTS)
        '''for atom in self.atoms:
            glVertex3f(atom[3], atom[4], atom[5])'''
        glEnd()

        glFlush()

    def wheelEvent(self, event):
        scroll = event.angleDelta()
        if scroll.y() > 0:
            self.zoomFactor += 0.1
            self.update()
        else:
            self.zoomFactor -= 0.1
            self.update()

    def update_projection_matrix(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-10 * self.scale_factor, 10 * self.scale_factor,
                -10 * self.scale_factor, 10 * self.scale_factor,
                -10, 10)
        glMatrixMode(GL_MODELVIEW)

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

    def setRotX(self, val):
        self.rotX = self.rotX + val

    def setRotY(self, val):
        self.rotY = self.rotY + val

    def setRotZ(self, val):
        self.rotZ = self.rotZ + val

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def update_rotation_matrix(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(self.x_angle, 1, 0, 0)
        glRotatef(self.y_angle, 0, 1, 0)