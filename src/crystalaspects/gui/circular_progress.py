from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import QRect, Qt


class PyCircularProgress(QWidget):
    def __init__(
        self,
        value=0,
        progress_width=15,
        is_rounded=True,
        max_value=100,
        progress_color="#ff79c6",
        enable_text=True,
        font_family="Arial",
        font_size=20,
        suffix="%",
        text_color="#ff79c6",
        enable_bg=True,
        bg_color="#44475a",
        comment=""
    ):
        QWidget.__init__(self)

        # CUSTOM PROPERTIES
        self.value = value
        self.progress_width = progress_width
        self.progress_rounded_cap = is_rounded
        self.max_value = max_value
        self.progress_color = progress_color
        # Text
        self.enable_text = enable_text
        self.comment = comment
        self.font_family = font_family
        self.font_size = font_size
        self.suffix = suffix
        self.text_color = text_color
        # BG
        self.enable_bg = enable_bg
        self.bg_color = bg_color

    # ADD DROPSHADOW
    def add_shadow(self, enable):
        if enable:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(15)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 80))
            self.setGraphicsEffect(self.shadow)

    # SET VALUE
    def set_value(self, value):
        self.value = value
        self.repaint() # Render progress bar after change value
    
    # SET COMMENT
    def set_comment(self, comment):
        self.comment = comment
        self.repaint()


    # PAINT EVENT (DESIGN YOUR CIRCULAR PROGRESS HERE)
    def paintEvent(self, e):
        # SET PROGRESS PARAMETERS
        width = self.width() - self.progress_width
        height = self.height() - self.progress_width
        margin = self.progress_width / 2
        value =  self.value * 360 / self.max_value

        # PAINTER
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing) # remove pixelated edges
        paint.setFont(QFont(self.font_family, self.font_size))

        # CREATE RECTANGLE
        rect = QRect(0, 0, self.width(), self.height())
        paint.setPen(Qt.NoPen)

        # PEN
        pen = QPen()             
        pen.setWidth(self.progress_width)
        # Set Round Cap
        if self.progress_rounded_cap:
            pen.setCapStyle(Qt.RoundCap)

        # ENABLE BG
        if self.enable_bg:
            pen.setColor(QColor(self.bg_color))
            paint.setPen(pen)  
            paint.drawArc(margin, margin, width, height, 0, 360 * 16) 

        # CREATE ARC / CIRCULAR PROGRESS
        pen.setColor(QColor(self.progress_color))
        paint.setPen(pen)      
        paint.drawArc(margin, margin, width, height, -90 * 16, -value * 16)       

        # DRAW COMMENT TEXT
        if self.comment:  # Check if the comment text is not empty
            pen = QPen()  # Create a new pen for the comment text
            pen.setColor(Qt.black)  # Set the text color to black
            paint.setPen(pen)
            # Draw the comment text in the center of the widget
            paint.drawText(rect, Qt.AlignCenter, self.comment)

        # CREATE TEXT
        if self.enable_text:
            pen.setColor(QColor(self.text_color))
            paint.setPen(pen)
            paint.drawText(rect, Qt.AlignCenter, f"{self.value}{self.suffix}")

        # END
        paint.end()