# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QLabel, QSizePolicy, QSlider, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 370)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.display_options_label = QLabel(Dialog)
        self.display_options_label.setObjectName(u"display_options_label")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        self.display_options_label.setFont(font)

        self.verticalLayout.addWidget(self.display_options_label)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.zoom_label = QLabel(Dialog)
        self.zoom_label.setObjectName(u"zoom_label")

        self.gridLayout_5.addWidget(self.zoom_label, 0, 0, 1, 1)

        self.zoom_slider = QSlider(Dialog)
        self.zoom_slider.setObjectName(u"zoom_slider")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zoom_slider.sizePolicy().hasHeightForWidth())
        self.zoom_slider.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(8)
        font1.setBold(True)
        font1.setItalic(False)
        self.zoom_slider.setFont(font1)
        self.zoom_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.zoom_slider, 0, 1, 1, 1)

        self.pointsize_label = QLabel(Dialog)
        self.pointsize_label.setObjectName(u"pointsize_label")

        self.gridLayout_5.addWidget(self.pointsize_label, 1, 0, 1, 1)

        self.point_slider = QSlider(Dialog)
        self.point_slider.setObjectName(u"point_slider")
        self.point_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.point_slider, 1, 1, 1, 1)

        self.brightness_label = QLabel(Dialog)
        self.brightness_label.setObjectName(u"brightness_label")
        self.brightness_label.setEnabled(False)

        self.gridLayout_5.addWidget(self.brightness_label, 2, 0, 1, 1)

        self.brightness_slider = QSlider(Dialog)
        self.brightness_slider.setObjectName(u"brightness_slider")
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.brightness_slider, 2, 1, 1, 1)

        self.resolution_label = QLabel(Dialog)
        self.resolution_label.setObjectName(u"resolution_label")
        self.resolution_label.setEnabled(False)

        self.gridLayout_5.addWidget(self.resolution_label, 3, 0, 1, 1)

        self.resolution_slider = QSlider(Dialog)
        self.resolution_slider.setObjectName(u"resolution_slider")
        self.resolution_slider.setEnabled(False)
        self.resolution_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.resolution_slider, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_5)

        self.point_type_label = QLabel(Dialog)
        self.point_type_label.setObjectName(u"point_type_label")
        self.point_type_label.setEnabled(True)
        self.point_type_label.setFont(font)

        self.verticalLayout.addWidget(self.point_type_label)

        self.pointtype_comboBox = QComboBox(Dialog)
        self.pointtype_comboBox.setObjectName(u"pointtype_comboBox")
        self.pointtype_comboBox.setEnabled(True)

        self.verticalLayout.addWidget(self.pointtype_comboBox)

        self.colour_mode_label = QLabel(Dialog)
        self.colour_mode_label.setObjectName(u"colour_mode_label")
        self.colour_mode_label.setFont(font)

        self.verticalLayout.addWidget(self.colour_mode_label)

        self.colourmode_comboBox = QComboBox(Dialog)
        self.colourmode_comboBox.setObjectName(u"colourmode_comboBox")

        self.verticalLayout.addWidget(self.colourmode_comboBox)

        self.colour_label = QLabel(Dialog)
        self.colour_label.setObjectName(u"colour_label")
        self.colour_label.setFont(font)

        self.verticalLayout.addWidget(self.colour_label)

        self.colour_comboBox = QComboBox(Dialog)
        self.colour_comboBox.setObjectName(u"colour_comboBox")

        self.verticalLayout.addWidget(self.colour_comboBox)

        self.colour_label_2 = QLabel(Dialog)
        self.colour_label_2.setObjectName(u"colour_label_2")
        self.colour_label_2.setFont(font)

        self.verticalLayout.addWidget(self.colour_label_2)

        self.bgcolour_comboBox = QComboBox(Dialog)
        self.bgcolour_comboBox.setObjectName(u"bgcolour_comboBox")

        self.verticalLayout.addWidget(self.bgcolour_comboBox)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.display_options_label.setText(QCoreApplication.translate("Dialog", u"Display Options", None))
        self.zoom_label.setText(QCoreApplication.translate("Dialog", u"Zoom", None))
        self.pointsize_label.setText(QCoreApplication.translate("Dialog", u"Point Size", None))
        self.brightness_label.setText(QCoreApplication.translate("Dialog", u"Brightness", None))
        self.resolution_label.setText(QCoreApplication.translate("Dialog", u"Resolution", None))
        self.point_type_label.setText(QCoreApplication.translate("Dialog", u"Point Type", None))
        self.colour_mode_label.setText(QCoreApplication.translate("Dialog", u"Colour Mode", None))
        self.colour_label.setText(QCoreApplication.translate("Dialog", u"Colour", None))
        self.colour_label_2.setText(QCoreApplication.translate("Dialog", u"Background Colour", None))
    # retranslateUi

