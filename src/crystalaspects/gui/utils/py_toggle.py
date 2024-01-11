from PySide6.QtCore import QRect, Qt, QEasingCurve, QPropertyAnimation, QPoint, Property, QSize
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QCheckBox, QLabel, QSizePolicy

class PyToggle(QCheckBox):
    def __init__(
        self,
        state_text = ["ON", "OFF"],
        min_width = 60,
        min_height = 28,
        expanding=False,
        bg_color = "#777", 
        circle_color = "#DDD",
        active_color = "#00BCFF",
        animation_curve = QEasingCurve.OutBounce
    ):
        QCheckBox.__init__(self)

        if expanding:
            self.setFixedSize(min_width, min_height)
        if not expanding:
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(1)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
            self.setSizePolicy(sizePolicy)
            self.setMinimumSize(QSize(min_width, 0))

        self.setCursor(Qt.PointingHandCursor)

        # COLORS
        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        self.state_text = state_text

        self._position = 3
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setEasingCurve(animation_curve)
        self.animation.setDuration(500)
        self.stateChanged.connect(self.setup_animation)

    @Property(float)
    def position(self):
        return self._position

    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()

    # START STOP ANIMATION
    def setup_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 26)
        else:
            self.animation.setEndValue(4)
        self.animation.start()
    
    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setFont(QFont("Arial", 12))

        # SET PEN
        p.setPen(Qt.NoPen)

        # DRAW RECT
        rect = QRect(0, 0, self.width(), self.height())
        # Adjust the height for drawing
        ellipse_size = self.height() - 6
        rect_height = self.height()
        corner_radius = min(self.height() // 2, 14)

        if not self.isChecked():
            p.setBrush(QColor(self._bg_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), corner_radius, corner_radius)
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._position, 3, ellipse_size, ellipse_size)

            # Draw text for the off state
            p.setPen(QColor("#000"))
            textRect = QRect(0, 0, rect.width() - 30, self.height())
            p.drawText(textRect, Qt.AlignCenter, self.state_text[1])

        else:
            p.setBrush(QColor(self._active_color))
            p.drawRoundedRect(0, 0, rect.width(), self.height(), corner_radius, corner_radius)
            p.setBrush(QColor(self._circle_color))
            p.drawEllipse(self._position, 3, ellipse_size, ellipse_size)

            # Draw text for the on state
            p.setPen(QColor("#FFF"))
            textRect = QRect(30, 0, rect.width() - 30, self.height())
            p.drawText(textRect, Qt.AlignCenter, self.state_text[0])

        p.end()