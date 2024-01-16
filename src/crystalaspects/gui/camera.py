from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion


class Camera:
    def __init__(self, position=QVector3D(0, 0, -20), target=QVector3D(0, 0, 0)):
        self.position = position
        self.target = target
        self.up = QVector3D(0, 1, 0)
        self.right = QVector3D(1, 0, 0)

        self.rotationSpeed = 1.0
        self.zoomSpeed = 0.02
        self.scale = 1.0
        self.distance = (self.position - self.target).length()

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

    def orbit(self, dx, dy):
        # Create quaternions representing the rotations
        q_pitch = QQuaternion.fromAxisAndAngle(self.right, dy * self.rotationSpeed)
        q_yaw = QQuaternion.fromAxisAndAngle(self.up, -dx * self.rotationSpeed)

        # Rotate the position around the target
        direction = self.position - self.target
        direction = q_pitch.rotatedVector(direction)
        direction = q_yaw.rotatedVector(direction)

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
            print("unknown projection mode", kind)

    def projectionMode(self):
        return "Perspective" if self.perspectiveProjection else "Orthographic"
