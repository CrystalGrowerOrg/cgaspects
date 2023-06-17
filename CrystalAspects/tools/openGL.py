from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtOpenGL
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QInputDialog, QFileDialog

import OpenGL.GL as gl  # python wrapping of OpenGL
from OpenGL.GL import glReadPixels, GL_RGBA, GL_UNSIGNED_BYTE, glGetIntegerv
from OpenGL import GLU  # OpenGL Utility Library, extends OpenGL functionality

from OpenGL.GL import glGenLists, glNewList, glBegin, GL_COMPILE, GL_TRIANGLES, glVertex3f, glEndList, glEnd, glCallList
from OpenGL.GLUT import glutSwapBuffers, glutSolidSphere
from OpenGL.GLU import gluNewQuadric, gluSphere
import OpenGL.GLU as glu

import numpy as np
import ctypes
from matplotlib import cm
from PIL import Image

from CrystalAspects.tools.shape_analysis import CrystalShape
from CrystalAspects.tools.crystal_math import transform_axes


class vis_GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

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
        self.zoomFactor = 1.0

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

        self.x_arrow_model = self.createArrow()
        self.y_arrow_model = self.createArrow()
        self.z_arrow_model = self.createArrow()

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
        self.updateGL()

        return arrow_model

    def pass_XYZ(self, xyz):
        self.xyz = xyz
        print("XYZ cordinates passed on OpenGL widget(class)")

    def pass_XYZ_list(self, xyz_path_list):
        self.xyz_path_list = xyz_path_list
        print("XYZ file paths passed to OpenGL widget")

    def get_XYZ_from_list(self, value):
        self.sim_num = value
        self.xyz, _, _ = CrystalShape.read_XYZ(self.xyz_path_list[value])
        self.initGeometry()
        self.updateGL()

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
        '''viewport = ctypes.c_int * 4
        gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)
        viewport_width, viewport_height = viewport[2], viewport[3]
        width, height = map(
            int, resolution.split("x")
        ) ''' # Split the resolution string and convert to integers

        # Calculate the x and y coordinates of the lower left corner of the region to read
        '''x = (viewport_width - width) // 2
        y = (viewport_height - height) // 2

        # Read the pixel data from the framebuffer
        pixels = (ctypes.c_ubyte * (width * height * 4))()
        gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, pixels)

        # Create a QImage from the pixel data
        image = QImage(pixels, width, height, QImage.Format_RGBA8888)'''
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

    def get_point_type(self, value):

        self.point_type = self.point_types[value]
        print(f" Point Type: {self.point_types[value]}")
        print(value)
        self.initGeometry()
        '''if value == 1:
            pcd_points = self.LoadVertices()
            self.draw_spheres(pcd_points)
            self.initGeometry()'''
        self.updateGL()

    def change_point_size(self, val):
        self.point_size = val
        self.updateGL()

    def zoomGL(self, val):
        self.zoomFactor = val
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
        self.rotZ = self.rotZ + val

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
        self.lastPos = event.pos()

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

        self.updateGL()

    def mouseMoveEvent(self, event):
        # print(f"Button pressed: {event.button()}")

        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        dz = dx * 0.01  # Scale the rotation amount
        dz = max(-100, min(dz, 100))  # Clamp the rotation amount to a certain range
        self.rotZ += dz  # Update the rotZ value

        if event.buttons() & QtCore.Qt.LeftButton:
            self.rotX = self.rotX + 0.5 * dy
            self.rotY = self.rotY + 0.5 * dx
            #self.rotZ = self.rotZ + 1 * dz

        if (
            event.buttons() & QtCore.Qt.LeftButton
            & QtCore.Qt.RightButton
        ):
            self.rotZ = self.rotZ + 0.1 * dz

        if event.buttons() & QtCore.Qt.RightButton:
            gl.glTranslate(dx * 100, dy * 100, dz * 100)

        self.updateGL()

        self.lastPos = event.pos()

    def initGeometry(self):

        vArrayv = self.LoadVertices()
        vArray = vArrayv.flatten()
        self.noPoints = len(vArray) // 6
        print("v array is: ")
        print(vArray)
        # print("No. of Points: %s" % self.noPoints)
        self.vbo = self.CreateBuffer(vArray)
        '''self.draw_spheres(self.LoadVertices())'''


    def LoadVertices(
        self,
    ):
        print("Loading Vertices")
        point_cloud = self.xyz
        print("Coords: ", point_cloud[:5], f"\n...(Total: {point_cloud.shape[0]})")
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
            point_cloud, self.colour_type, C_Choice=self.colour_picked
        )

        points = np.asarray(points).astype("float32")
        colors = np.asarray(colors).astype("float32")

        attributes = np.concatenate((points, colors), axis=1)
        print("attributes")
        print(attributes)
        print("attributes.flatten")
        print(attributes.flatten())

        return attributes

    # Create sphere
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
        print('Draw Spheres')
        print(points)
        radius = 0.1  # Sphere radius
        for p in points:
            gl.glTranslatef(p[0], p[1], p[2])
            glutSolidSphere(radius, 16, 16)
            gl.glTranslatef(-p[0], -p[1], -p[2])
        #gl.glPopMatrix()
        self.updateGL()

    def paintGL(self):
        # Clear the color and depth buffers
        '''if self.point_type == "Sphere":'''
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Push Matrix
        '''gl.glPushMatrix()'''

        # Enabling Lighting
        #gl.glEnable(gl.GL_LIGHTING)
        #gl.glEnable(gl.GL_LIGHT0)
        '''gl.glLight(gl.GL_LIGHT0, gl.GL_POSITION, (1, 1, 1, 0))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)'''

        # set material properties
        #gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE, [1.0, 0.0, 0.0, 1.0])
        '''gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SPECULAR, [5.0, 1.0, 1.0, 1.0])
        gl.glMaterialfv(gl.GL_FRONT_AND_BACK, gl.GL_SHININESS, 100)'''

        '''for p in self.PointCloud():
            gl.glTranslatef(p[0], p[1], p[2])
            #glutSolidSphere(self.point_size, 16, 16)
            gl.glTranslatef(-p[0], -p[1], -p[2])
        gl.glPopMatrix()
        glutSwapBuffers()'''

        # push the current matrix to the current stack
        gl.glLoadIdentity()
        gl.glTranslate(0.0, 0.0, -50.0)  # third, translate cube to specified depth. Starting depth
        gl.glScale(0.1 * self.zoomFactor, 0.1 * self.zoomFactor, 0.1 * self.zoomFactor)
        # gl.glScale(20.0, 20.0, 20.0)       # second, scale cube
        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)  # first, translate cube center to origin

        # Point size
        gl.glPointSize(self.point_size)
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        stride = 6 * 4  # (24 bates) : [x, y, z, r, g, b] * sizeof(float)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointer(3, gl.GL_FLOAT, stride, None)

        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        # (12 bytes) : the rgb color starts after the 3 coordinates x, y, z
        offset = 3 * 4
        gl.glColorPointer(3, gl.GL_FLOAT, stride, ctypes.c_void_p(offset))

        # Drawing points
        noOfVertices = self.noPoints
        gl.glDrawArrays(gl.GL_POINTS, 0, noOfVertices)



        '''if self.point_type == "Spheres":
            self.draw_spheres(self.PointCloud())'''
        #gl.glLoadIdentity()
        gl.glMatrixMode(gl.GL_MODELVIEW)
        '''gl.glPushMatrix()
        for p in self.PointCloud():
            gl.glTranslatef(p[0], p[1], p[2])
            #glutSolidSphere(self.point_size, 16, 16)
            gl.glTranslatef(-p[0], -p[1], -p[2])
        gl.glPopMatrix()'''

        glutSwapBuffers()

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        #gl.glPopMatrix()  # restore the previous modelview matrix

        # Draw Arrows
        '''gl.glLoadIdentity()
        self.createArrow()'''
        #gl.glPopMatrix()

        #glutSwapBuffers()
        """"
        #Draw axes
        gl.glLoadIdentity()
        gl.glPushMatrix()
        self.create_arrow(width=1, height=1)
        gl.glPopMatrix()
        """


    def CreateBuffer(self, attributes):
        bufferdata = (ctypes.c_float * len(attributes))(*attributes)  # float buffer
        buffersize = len(attributes) * 4  # buffer size in bytes

        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, buffersize, bufferdata, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        return vbo
