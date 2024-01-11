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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QFrame, QGridLayout, QLabel, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_settings_Dialog(object):
    def setupUi(self, settings_Dialog):
        if not settings_Dialog.objectName():
            settings_Dialog.setObjectName(u"settings_Dialog")
        settings_Dialog.resize(496, 575)
        font = QFont()
        font.setFamilies([u"Apple Chancery"])
        font.setPointSize(10)
        font.setItalic(True)
        settings_Dialog.setFont(font)
        self.gridLayout = QGridLayout(settings_Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.settings_scrollArea = QScrollArea(settings_Dialog)
        self.settings_scrollArea.setObjectName(u"settings_scrollArea")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setItalic(False)
        self.settings_scrollArea.setFont(font1)
        self.settings_scrollArea.setFrameShadow(QFrame.Plain)
        self.settings_scrollArea.setLineWidth(0)
        self.settings_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 470, 549))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.display_options_label = QLabel(self.scrollAreaWidgetContents)
        self.display_options_label.setObjectName(u"display_options_label")
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setItalic(False)
        self.display_options_label.setFont(font2)

        self.verticalLayout_2.addWidget(self.display_options_label)

        self.display_options_formLayout = QFormLayout()
        self.display_options_formLayout.setObjectName(u"display_options_formLayout")
        self.display_options_formLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.display_options_formLayout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.display_options_formLayout.setLabelAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.display_options_formLayout.setHorizontalSpacing(20)
        self.display_options_formLayout.setVerticalSpacing(20)
        self.display_options_formLayout.setContentsMargins(10, 20, 10, 20)
        self.point_type_label = QLabel(self.scrollAreaWidgetContents)
        self.point_type_label.setObjectName(u"point_type_label")
        self.point_type_label.setEnabled(True)
        font3 = QFont()
        font3.setFamilies([u"Arial"])
        font3.setPointSize(11)
        font3.setBold(True)
        font3.setItalic(False)
        self.point_type_label.setFont(font3)

        self.display_options_formLayout.setWidget(4, QFormLayout.LabelRole, self.point_type_label)

        self.pointtype_comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.pointtype_comboBox.setObjectName(u"pointtype_comboBox")
        self.pointtype_comboBox.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pointtype_comboBox.sizePolicy().hasHeightForWidth())
        self.pointtype_comboBox.setSizePolicy(sizePolicy)
        self.pointtype_comboBox.setMinimumSize(QSize(0, 0))

        self.display_options_formLayout.setWidget(4, QFormLayout.FieldRole, self.pointtype_comboBox)

        self.colour_mode_label = QLabel(self.scrollAreaWidgetContents)
        self.colour_mode_label.setObjectName(u"colour_mode_label")
        self.colour_mode_label.setFont(font3)

        self.display_options_formLayout.setWidget(5, QFormLayout.LabelRole, self.colour_mode_label)

        self.colourmode_comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.colourmode_comboBox.setObjectName(u"colourmode_comboBox")
        sizePolicy.setHeightForWidth(self.colourmode_comboBox.sizePolicy().hasHeightForWidth())
        self.colourmode_comboBox.setSizePolicy(sizePolicy)
        self.colourmode_comboBox.setMinimumSize(QSize(100, 0))

        self.display_options_formLayout.setWidget(5, QFormLayout.FieldRole, self.colourmode_comboBox)

        self.colour_label = QLabel(self.scrollAreaWidgetContents)
        self.colour_label.setObjectName(u"colour_label")
        self.colour_label.setFont(font3)

        self.display_options_formLayout.setWidget(6, QFormLayout.LabelRole, self.colour_label)

        self.colour_comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.colour_comboBox.setObjectName(u"colour_comboBox")
        sizePolicy.setHeightForWidth(self.colour_comboBox.sizePolicy().hasHeightForWidth())
        self.colour_comboBox.setSizePolicy(sizePolicy)
        self.colour_comboBox.setMinimumSize(QSize(100, 0))

        self.display_options_formLayout.setWidget(6, QFormLayout.FieldRole, self.colour_comboBox)

        self.colour_label_2 = QLabel(self.scrollAreaWidgetContents)
        self.colour_label_2.setObjectName(u"colour_label_2")
        self.colour_label_2.setFont(font3)

        self.display_options_formLayout.setWidget(7, QFormLayout.LabelRole, self.colour_label_2)

        self.bgcolour_comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.bgcolour_comboBox.setObjectName(u"bgcolour_comboBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.bgcolour_comboBox.sizePolicy().hasHeightForWidth())
        self.bgcolour_comboBox.setSizePolicy(sizePolicy1)
        self.bgcolour_comboBox.setMinimumSize(QSize(100, 0))

        self.display_options_formLayout.setWidget(7, QFormLayout.FieldRole, self.bgcolour_comboBox)

        self.projection_label = QLabel(self.scrollAreaWidgetContents)
        self.projection_label.setObjectName(u"projection_label")
        self.projection_label.setFont(font3)

        self.display_options_formLayout.setWidget(8, QFormLayout.LabelRole, self.projection_label)

        self.zoom_label = QLabel(self.scrollAreaWidgetContents)
        self.zoom_label.setObjectName(u"zoom_label")
        self.zoom_label.setFont(font3)

        self.display_options_formLayout.setWidget(0, QFormLayout.LabelRole, self.zoom_label)

        self.zoom_slider = QSlider(self.scrollAreaWidgetContents)
        self.zoom_slider.setObjectName(u"zoom_slider")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.zoom_slider.sizePolicy().hasHeightForWidth())
        self.zoom_slider.setSizePolicy(sizePolicy2)
        font4 = QFont()
        font4.setFamilies([u"Arial"])
        font4.setPointSize(8)
        font4.setBold(True)
        font4.setItalic(False)
        self.zoom_slider.setFont(font4)
        self.zoom_slider.setOrientation(Qt.Horizontal)

        self.display_options_formLayout.setWidget(0, QFormLayout.FieldRole, self.zoom_slider)

        self.pointsize_label = QLabel(self.scrollAreaWidgetContents)
        self.pointsize_label.setObjectName(u"pointsize_label")
        self.pointsize_label.setFont(font3)

        self.display_options_formLayout.setWidget(1, QFormLayout.LabelRole, self.pointsize_label)

        self.point_slider = QSlider(self.scrollAreaWidgetContents)
        self.point_slider.setObjectName(u"point_slider")
        self.point_slider.setOrientation(Qt.Horizontal)

        self.display_options_formLayout.setWidget(1, QFormLayout.FieldRole, self.point_slider)

        self.brightness_label = QLabel(self.scrollAreaWidgetContents)
        self.brightness_label.setObjectName(u"brightness_label")
        self.brightness_label.setEnabled(False)
        self.brightness_label.setFont(font3)

        self.display_options_formLayout.setWidget(2, QFormLayout.LabelRole, self.brightness_label)

        self.brightness_slider = QSlider(self.scrollAreaWidgetContents)
        self.brightness_slider.setObjectName(u"brightness_slider")
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setOrientation(Qt.Horizontal)

        self.display_options_formLayout.setWidget(2, QFormLayout.FieldRole, self.brightness_slider)

        self.resolution_label = QLabel(self.scrollAreaWidgetContents)
        self.resolution_label.setObjectName(u"resolution_label")
        self.resolution_label.setEnabled(False)
        self.resolution_label.setFont(font3)

        self.display_options_formLayout.setWidget(3, QFormLayout.LabelRole, self.resolution_label)

        self.resolution_slider = QSlider(self.scrollAreaWidgetContents)
        self.resolution_slider.setObjectName(u"resolution_slider")
        self.resolution_slider.setEnabled(False)
        self.resolution_slider.setOrientation(Qt.Horizontal)

        self.display_options_formLayout.setWidget(3, QFormLayout.FieldRole, self.resolution_slider)


        self.verticalLayout_2.addLayout(self.display_options_formLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.settings_scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.settings_scrollArea, 0, 0, 1, 1)


        self.retranslateUi(settings_Dialog)

        QMetaObject.connectSlotsByName(settings_Dialog)
    # setupUi

    def retranslateUi(self, settings_Dialog):
        settings_Dialog.setWindowTitle(QCoreApplication.translate("settings_Dialog", u"Settings", None))
        self.display_options_label.setText(QCoreApplication.translate("settings_Dialog", u"Display Options", None))
        self.point_type_label.setText(QCoreApplication.translate("settings_Dialog", u"Point Type", None))
        self.colour_mode_label.setText(QCoreApplication.translate("settings_Dialog", u"Colour Mode", None))
        self.colour_label.setText(QCoreApplication.translate("settings_Dialog", u"Colour", None))
        self.colour_label_2.setText(QCoreApplication.translate("settings_Dialog", u"Background Colour", None))
        self.projection_label.setText(QCoreApplication.translate("settings_Dialog", u"Projection", None))
        self.zoom_label.setText(QCoreApplication.translate("settings_Dialog", u"Zoom", None))
        self.pointsize_label.setText(QCoreApplication.translate("settings_Dialog", u"Point Size", None))
        self.brightness_label.setText(QCoreApplication.translate("settings_Dialog", u"Brightness", None))
        self.resolution_label.setText(QCoreApplication.translate("settings_Dialog", u"Resolution", None))
    # retranslateUi

