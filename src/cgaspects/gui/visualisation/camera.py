import numpy as np
from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D, QVector4D
import logging

LOG = logging.getLogger("CGA:Camera")


def pca(vertices):
    "returns the magnitudes and the principle axes"
    centered_vertices = vertices - np.mean(vertices, axis=0)
    covariance_matrix = np.cov(centered_vertices.T)
    U, S, vh = np.linalg.svd(covariance_matrix)
    return S, vh


def bounding_box(vertices):
    return np.min(vertices, axis=0), np.max(vertices, axis=0)


class Camera:
    def __init__(self, position=QVector3D(0, 0, -20), target=QVector3D(0, 0, 0)):
        self.position = position
        self.target = target
        self.up = QVector3D(0, 1, 0)
        self.right = QVector3D(1, 0, 0)
        self.screen = QVector3D(0, 0, 1)

        self.rotationSpeed = 1.0
        self.zoomSpeed = 0.02
        self.scale = 1.0
        self.distance = (self.position - self.target).length()
        self.storeOrientation()

        self.perspectiveProjection = True
        self.fieldOfView = 45
        self.orthoSize = 10
        self.nearPlane = 0.01
        self.farPlane = 1000

    def modelMatrix(self):
        model = QMatrix4x4()
        # can adjust these later if for some bizarre reason
        # you'd want different scales in this program
        model.scale(self.scale, self.scale, self.scale)
        return model

    def viewMatrix(self):
        view = QMatrix4x4()
        view.lookAt(self.position, self.target, self.up)
        return view

    def modelViewMatrix(self):
        return self.viewMatrix() * self.modelMatrix()

    def projectionMatrix(self, aspectRatio):
        projection = QMatrix4x4()
        if self.perspectiveProjection:
            projection.perspective(
                self.fieldOfView, aspectRatio, self.nearPlane, self.farPlane
            )
        else:
            halfWidth = aspectRatio * self.orthoSize
            halfHeight = self.orthoSize
            projection.ortho(
                -halfWidth,
                halfWidth,
                -halfHeight,
                halfHeight,
                self.nearPlane,
                self.farPlane,
            )
        return projection

    def modelViewProjectionMatrix(self, aspectRatio):
        return (
            self.projectionMatrix(aspectRatio) * self.viewMatrix() * self.modelMatrix()
        )

    def storeOrientation(self):
        self._stored_orientation = (
            self.position,
            self.target,
            self.right,
            self.up,
            self.scale,
        )

    def resetOrientation(self):
        (
            self.position,
            self.target,
            self.right,
            self.up,
            self.scale,
        ) = self._stored_orientation

    def orbit(self, dx, dy, restrict_axis=None):

        # Create quaternions representing the rotations
        q_pitch = QQuaternion.fromAxisAndAngle(self.right, dy * self.rotationSpeed)
        q_yaw = QQuaternion.fromAxisAndAngle(self.up, -dx * self.rotationSpeed)
        # Apply axis restriction

        if restrict_axis == "shift_x":
            q_yaw = QQuaternion()
        elif restrict_axis == "shift_y":
            q_pitch = QQuaternion()
        elif restrict_axis == "shift_z":
            q_yaw = QQuaternion()
            q_pitch = QQuaternion()
            q_roll = QQuaternion.fromAxisAndAngle(self.screen, -dx * self.rotationSpeed)

        # Rotate the position around the target
        direction = self.position - self.target
        direction = q_pitch.rotatedVector(direction)
        direction = q_yaw.rotatedVector(direction)
        if restrict_axis == "shift_z":
            direction = q_roll.rotatedVector(direction)

        self.position = self.target + direction

        self.right = QVector3D.crossProduct(
            self.up, self.target - self.position
        ).normalized()

        self.up = QVector3D.crossProduct(
            self.target - self.position, self.right
        ).normalized()

        # Recalculate the distance in case of zooming
        self.distance = (self.position - self.target).length()

    def zoom(self, amount):
        self.scale *= 1 + amount * self.zoomSpeed
        if amount > 0:
            self.scale *= 1 + self.zoomSpeed
        elif amount < 0:
            self.scale /= 1 + self.zoomSpeed

    def updatePosition(self):
        direction = self.position - self.target
        direction = direction / direction.length()
        self.position = self.target + direction * self.distance

    def pan(self, dx, dy):
        # Adjust these factors to change the sensitivity of panning
        panSpeed = 0.1
        right = self.front.cross(self.front, self.up)
        up = self.right.cross(right, self.front)

        self.target += right * dx * panSpeed
        self.target += up * dy * panSpeed

    def toggleProjectionMode(self):
        self.perspectiveProjection = not self.perspectiveProjection

    def setProjectionMode(self, kind):
        if kind.lower() == "orthographic":
            self.perspectiveProjection = False
        elif kind.lower() == "perspective":
            self.perspectiveProjection = True
        else:
            LOG.error("unknown projection mode", kind)

    def fitToObject(self, points):
        extents, axes = pca(points)
        self.right = QVector3D(axes[0, 0], axes[0, 1], axes[0, 2])
        self.up = QVector3D.crossProduct(self.target - self.position, self.right)
        self.scale = 1 / np.sqrt(np.max(extents))
        self.storeOrientation()

    def projectionMode(self):
        return "Perspective" if self.perspectiveProjection else "Orthographic"
