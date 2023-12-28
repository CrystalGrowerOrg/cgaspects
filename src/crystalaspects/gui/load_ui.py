# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QMainWindow,
    QProgressBar, QPushButton, QScrollArea, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QStatusBar,
    QTextEdit, QToolBox, QToolButton, QVBoxLayout,
    QWidget)
from crystalaspects.gui import qticons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1400, 847)
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        icon = QIcon()
        icon.addFile(u"../../../res/icon.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.actionOpen_Simulations = QAction(MainWindow)
        self.actionOpen_Simulations.setObjectName(u"actionOpen_Simulations")
        self.actionOpen_XYZs = QAction(MainWindow)
        self.actionOpen_XYZs.setObjectName(u"actionOpen_XYZs")
        self.actionOpen_Outputs = QAction(MainWindow)
        self.actionOpen_Outputs.setObjectName(u"actionOpen_Outputs")
        self.actionAmber = QAction(MainWindow)
        self.actionAmber.setObjectName(u"actionAmber")
        self.actionBlue = QAction(MainWindow)
        self.actionBlue.setObjectName(u"actionBlue")
        self.actionCyan = QAction(MainWindow)
        self.actionCyan.setObjectName(u"actionCyan")
        self.actionCyan_500 = QAction(MainWindow)
        self.actionCyan_500.setObjectName(u"actionCyan_500")
        self.actionLight_green = QAction(MainWindow)
        self.actionLight_green.setObjectName(u"actionLight_green")
        self.actionPink = QAction(MainWindow)
        self.actionPink.setObjectName(u"actionPink")
        self.actionPurple = QAction(MainWindow)
        self.actionPurple.setObjectName(u"actionPurple")
        self.actionRed_2 = QAction(MainWindow)
        self.actionRed_2.setObjectName(u"actionRed_2")
        self.actionTeal = QAction(MainWindow)
        self.actionTeal.setObjectName(u"actionTeal")
        self.actionYellow = QAction(MainWindow)
        self.actionYellow.setObjectName(u"actionYellow")
        self.actionAmber_2 = QAction(MainWindow)
        self.actionAmber_2.setObjectName(u"actionAmber_2")
        self.actionBlue_2 = QAction(MainWindow)
        self.actionBlue_2.setObjectName(u"actionBlue_2")
        self.actionCyan_2 = QAction(MainWindow)
        self.actionCyan_2.setObjectName(u"actionCyan_2")
        self.actionLight_green_2 = QAction(MainWindow)
        self.actionLight_green_2.setObjectName(u"actionLight_green_2")
        self.actionPink_2 = QAction(MainWindow)
        self.actionPink_2.setObjectName(u"actionPink_2")
        self.actionPurple_2 = QAction(MainWindow)
        self.actionPurple_2.setObjectName(u"actionPurple_2")
        self.actionRed = QAction(MainWindow)
        self.actionRed.setObjectName(u"actionRed")
        self.actionTeal_2 = QAction(MainWindow)
        self.actionTeal_2.setObjectName(u"actionTeal_2")
        self.actionCyan_501 = QAction(MainWindow)
        self.actionCyan_501.setObjectName(u"actionCyan_501")
        self.actionLight_green_3 = QAction(MainWindow)
        self.actionLight_green_3.setObjectName(u"actionLight_green_3")
        self.actionPink_3 = QAction(MainWindow)
        self.actionPink_3.setObjectName(u"actionPink_3")
        self.actionPurple_3 = QAction(MainWindow)
        self.actionPurple_3.setObjectName(u"actionPurple_3")
        self.actionRed_3 = QAction(MainWindow)
        self.actionRed_3.setObjectName(u"actionRed_3")
        self.actionTeal_3 = QAction(MainWindow)
        self.actionTeal_3.setObjectName(u"actionTeal_3")
        self.actionYellow_2 = QAction(MainWindow)
        self.actionYellow_2.setObjectName(u"actionYellow_2")
        self.action_5 = QAction(MainWindow)
        self.action_5.setObjectName(u"action_5")
        self.action_5.setCheckable(False)
        self.action_4 = QAction(MainWindow)
        self.action_4.setObjectName(u"action_4")
        self.action_6 = QAction(MainWindow)
        self.action_6.setObjectName(u"action_6")
        self.action_7 = QAction(MainWindow)
        self.action_7.setObjectName(u"action_7")
        self.action_1 = QAction(MainWindow)
        self.action_1.setObjectName(u"action_1")
        self.action0 = QAction(MainWindow)
        self.action0.setObjectName(u"action0")
        self.action1 = QAction(MainWindow)
        self.action1.setObjectName(u"action1")
        self.action2 = QAction(MainWindow)
        self.action2.setObjectName(u"action2")
        self.action3 = QAction(MainWindow)
        self.action3.setObjectName(u"action3")
        self.action4 = QAction(MainWindow)
        self.action4.setObjectName(u"action4")
        self.action5 = QAction(MainWindow)
        self.action5.setObjectName(u"action5")
        self.actionDensity_2 = QAction(MainWindow)
        self.actionDensity_2.setObjectName(u"actionDensity_2")
        self.actionStyle = QAction(MainWindow)
        self.actionStyle.setObjectName(u"actionStyle")
        self.action_8 = QAction(MainWindow)
        self.action_8.setObjectName(u"action_8")
        self.action_9 = QAction(MainWindow)
        self.action_9.setObjectName(u"action_9")
        self.action_10 = QAction(MainWindow)
        self.action_10.setObjectName(u"action_10")
        self.action_11 = QAction(MainWindow)
        self.action_11.setObjectName(u"action_11")
        self.action0_2 = QAction(MainWindow)
        self.action0_2.setObjectName(u"action0_2")
        self.action1_2 = QAction(MainWindow)
        self.action1_2.setObjectName(u"action1_2")
        self.action2_2 = QAction(MainWindow)
        self.action2_2.setObjectName(u"action2_2")
        self.action3_2 = QAction(MainWindow)
        self.action3_2.setObjectName(u"action3_2")
        self.action4_2 = QAction(MainWindow)
        self.action4_2.setObjectName(u"action4_2")
        self.action_12 = QAction(MainWindow)
        self.action_12.setObjectName(u"action_12")
        self.action_13 = QAction(MainWindow)
        self.action_13.setObjectName(u"action_13")
        self.action_14 = QAction(MainWindow)
        self.action_14.setObjectName(u"action_14")
        self.action0_3 = QAction(MainWindow)
        self.action0_3.setObjectName(u"action0_3")
        self.action1_3 = QAction(MainWindow)
        self.action1_3.setObjectName(u"action1_3")
        self.action2_3 = QAction(MainWindow)
        self.action2_3.setObjectName(u"action2_3")
        self.action3_3 = QAction(MainWindow)
        self.action3_3.setObjectName(u"action3_3")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.import_pushButton = QPushButton(self.centralwidget)
        self.import_pushButton.setObjectName(u"import_pushButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.import_pushButton.sizePolicy().hasHeightForWidth())
        self.import_pushButton.setSizePolicy(sizePolicy)
        self.import_pushButton.setMinimumSize(QSize(150, 45))
        self.import_pushButton.setBaseSize(QSize(0, 0))
        icon1 = QIcon()
        icon1.addFile(u":/material_icons/material_icons/png/folder-arrow-down.png", QSize(), QIcon.Normal, QIcon.Off)
        self.import_pushButton.setIcon(icon1)
        self.import_pushButton.setIconSize(QSize(20, 20))

        self.gridLayout.addWidget(self.import_pushButton, 0, 0, 1, 1)

        self.settings_toolButton = QToolButton(self.centralwidget)
        self.settings_toolButton.setObjectName(u"settings_toolButton")
        self.settings_toolButton.setEnabled(False)
        icon2 = QIcon()
        icon2.addFile(u":/material_icons/material_icons/png/cog.png", QSize(), QIcon.Normal, QIcon.Off)
        self.settings_toolButton.setIcon(icon2)
        self.settings_toolButton.setIconSize(QSize(20, 20))

        self.gridLayout.addWidget(self.settings_toolButton, 0, 9, 1, 1)

        self.vis_scrollArea = QScrollArea(self.centralwidget)
        self.vis_scrollArea.setObjectName(u"vis_scrollArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(30)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.vis_scrollArea.sizePolicy().hasHeightForWidth())
        self.vis_scrollArea.setSizePolicy(sizePolicy1)
        self.vis_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 951, 754))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.main_frame = QFrame(self.scrollAreaWidgetContents_4)
        self.main_frame.setObjectName(u"main_frame")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(5)
        sizePolicy2.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(sizePolicy2)
        self.gl_vLayout = QGridLayout(self.main_frame)
        self.gl_vLayout.setObjectName(u"gl_vLayout")

        self.gridLayout_4.addWidget(self.main_frame, 0, 1, 1, 2)

        self.xyz_horizontalSlider = QSlider(self.scrollAreaWidgetContents_4)
        self.xyz_horizontalSlider.setObjectName(u"xyz_horizontalSlider")
        self.xyz_horizontalSlider.setOrientation(Qt.Horizontal)

        self.gridLayout_4.addWidget(self.xyz_horizontalSlider, 1, 1, 1, 1)

        self.xyz_spinBox = QSpinBox(self.scrollAreaWidgetContents_4)
        self.xyz_spinBox.setObjectName(u"xyz_spinBox")

        self.gridLayout_4.addWidget(self.xyz_spinBox, 1, 2, 1, 1)

        self.vis_scrollArea.setWidget(self.scrollAreaWidgetContents_4)

        self.gridLayout.addWidget(self.vis_scrollArea, 3, 7, 3, 3)

        self.output_textbox = QTextEdit(self.centralwidget)
        self.output_textbox.setObjectName(u"output_textbox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(5)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.output_textbox.sizePolicy().hasHeightForWidth())
        self.output_textbox.setSizePolicy(sizePolicy3)
        self.output_textbox.setMinimumSize(QSize(0, 75))
        self.output_textbox.setStyleSheet(u"background-color: rgb(58, 64, 85);\n"
"color: rgb(255, 255, 255);")
        self.output_textbox.setReadOnly(True)

        self.gridLayout.addWidget(self.output_textbox, 5, 0, 1, 3)

        self.console_label = QLabel(self.centralwidget)
        self.console_label.setObjectName(u"console_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.console_label.sizePolicy().hasHeightForWidth())
        self.console_label.setSizePolicy(sizePolicy4)
        self.console_label.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout.addWidget(self.console_label, 4, 0, 1, 3)

        self.scrollArea_options = QScrollArea(self.centralwidget)
        self.scrollArea_options.setObjectName(u"scrollArea_options")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(5)
        sizePolicy5.setVerticalStretch(4)
        sizePolicy5.setHeightForWidth(self.scrollArea_options.sizePolicy().hasHeightForWidth())
        self.scrollArea_options.setSizePolicy(sizePolicy5)
        self.scrollArea_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 411, 574))
        self.gridLayout_12 = QGridLayout(self.scrollAreaWidgetContents_5)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.main_toolBox = QToolBox(self.scrollAreaWidgetContents_5)
        self.main_toolBox.setObjectName(u"main_toolBox")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(3)
        sizePolicy6.setHeightForWidth(self.main_toolBox.sizePolicy().hasHeightForWidth())
        self.main_toolBox.setSizePolicy(sizePolicy6)
        self.main_toolBox.setMinimumSize(QSize(0, 450))
        self.batch_analysis_tab = QWidget()
        self.batch_analysis_tab.setObjectName(u"batch_analysis_tab")
        self.batch_analysis_tab.setGeometry(QRect(0, 0, 387, 370))
        self.gridLayout_6 = QGridLayout(self.batch_analysis_tab)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_6.addItem(self.verticalSpacer_3, 1, 0, 1, 1)

        self.progressBar = QProgressBar(self.batch_analysis_tab)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"	background-color: rgb(213, 215, 255);\n"
"	color: rgb(0, 0, 127);\n"
"	border-style: none;\n"
"	border-radius: 10px;\n"
"	text-align: center;\n"
"}\n"
"QProgressBar::chunk{\n"
"	border-radius: 10px;\n"
"	background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.489, stop:0 rgba(255, 170, 255, 255), stop:1 rgba(185, 135, 255, 255));\n"
"}")
        self.progressBar.setValue(0)

        self.gridLayout_6.addWidget(self.progressBar, 2, 0, 1, 3)

        self.main_toolBox.addItem(self.batch_analysis_tab, u"Batch Analysis")
        self.plotting_tab = QWidget()
        self.plotting_tab.setObjectName(u"plotting_tab")
        self.plotting_tab.setGeometry(QRect(0, 0, 387, 370))
        self.main_toolBox.addItem(self.plotting_tab, u"Plotting")
        self.crystal_info_tab = QWidget()
        self.crystal_info_tab.setObjectName(u"crystal_info_tab")
        self.crystal_info_tab.setGeometry(QRect(0, 0, 387, 370))
        self.gridLayout_2 = QGridLayout(self.crystal_info_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.ml_label = QLabel(self.crystal_info_tab)
        self.ml_label.setObjectName(u"ml_label")

        self.gridLayout_2.addWidget(self.ml_label, 5, 0, 1, 1)

        self.crystal_savol_label = QLabel(self.crystal_info_tab)
        self.crystal_savol_label.setObjectName(u"crystal_savol_label")

        self.gridLayout_2.addWidget(self.crystal_savol_label, 7, 0, 1, 1)

        self.spacegroup_label = QLabel(self.crystal_info_tab)
        self.spacegroup_label.setObjectName(u"spacegroup_label")
        self.spacegroup_label.setEnabled(False)

        self.gridLayout_2.addWidget(self.spacegroup_label, 2, 0, 1, 1)

        self.crystal_ar_label = QLabel(self.crystal_info_tab)
        self.crystal_ar_label.setObjectName(u"crystal_ar_label")

        self.gridLayout_2.addWidget(self.crystal_ar_label, 3, 0, 1, 1)

        self.show_info_button = QPushButton(self.crystal_info_tab)
        self.show_info_button.setObjectName(u"show_info_button")
        sizePolicy7 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(1)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.show_info_button.sizePolicy().hasHeightForWidth())
        self.show_info_button.setSizePolicy(sizePolicy7)
        self.show_info_button.setMinimumSize(QSize(200, 0))

        self.gridLayout_2.addWidget(self.show_info_button, 1, 0, 1, 1)

        self.sm_label = QLabel(self.crystal_info_tab)
        self.sm_label.setObjectName(u"sm_label")

        self.gridLayout_2.addWidget(self.sm_label, 4, 0, 1, 1)

        self.crystal_vol_label = QLabel(self.crystal_info_tab)
        self.crystal_vol_label.setObjectName(u"crystal_vol_label")

        self.gridLayout_2.addWidget(self.crystal_vol_label, 9, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.fname_label = QLabel(self.crystal_info_tab)
        self.fname_label.setObjectName(u"fname_label")
        sizePolicy8 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy8.setHorizontalStretch(1)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.fname_label.sizePolicy().hasHeightForWidth())
        self.fname_label.setSizePolicy(sizePolicy8)

        self.horizontalLayout.addWidget(self.fname_label)

        self.fname_comboBox = QComboBox(self.crystal_info_tab)
        self.fname_comboBox.setObjectName(u"fname_comboBox")
        sizePolicy9 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy9.setHorizontalStretch(3)
        sizePolicy9.setVerticalStretch(1)
        sizePolicy9.setHeightForWidth(self.fname_comboBox.sizePolicy().hasHeightForWidth())
        self.fname_comboBox.setSizePolicy(sizePolicy9)
        self.fname_comboBox.setMinimumSize(QSize(200, 0))

        self.horizontalLayout.addWidget(self.fname_comboBox)


        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.crystal_sa_label = QLabel(self.crystal_info_tab)
        self.crystal_sa_label.setObjectName(u"crystal_sa_label")

        self.gridLayout_2.addWidget(self.crystal_sa_label, 8, 0, 1, 1)

        self.shape_label = QLabel(self.crystal_info_tab)
        self.shape_label.setObjectName(u"shape_label")

        self.gridLayout_2.addWidget(self.shape_label, 6, 0, 1, 1)

        self.main_toolBox.addItem(self.crystal_info_tab, u"Crystal Information")
        self.variables_tab = QWidget()
        self.variables_tab.setObjectName(u"variables_tab")
        self.variables_tab.setGeometry(QRect(0, 0, 387, 370))
        self.gridLayout_7 = QGridLayout(self.variables_tab)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.EVariable_title_label_2 = QLabel(self.variables_tab)
        self.EVariable_title_label_2.setObjectName(u"EVariable_title_label_2")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(10)
        font1.setBold(True)
        font1.setItalic(False)
        self.EVariable_title_label_2.setFont(font1)

        self.gridLayout_7.addWidget(self.EVariable_title_label_2, 1, 0, 1, 1)

        self.select_summary_slider_button = QPushButton(self.variables_tab)
        self.select_summary_slider_button.setObjectName(u"select_summary_slider_button")
        self.select_summary_slider_button.setEnabled(False)
        sizePolicy10 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(1)
        sizePolicy10.setHeightForWidth(self.select_summary_slider_button.sizePolicy().hasHeightForWidth())
        self.select_summary_slider_button.setSizePolicy(sizePolicy10)
        self.select_summary_slider_button.setMinimumSize(QSize(200, 0))
        self.select_summary_slider_button.setFont(font1)

        self.gridLayout_7.addWidget(self.select_summary_slider_button, 0, 0, 1, 1, Qt.AlignLeft)

        self.E_variables_layout = QGridLayout()
        self.E_variables_layout.setObjectName(u"E_variables_layout")
        self.E_variables_layout.setSizeConstraint(QLayout.SetNoConstraint)

        self.gridLayout_7.addLayout(self.E_variables_layout, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.main_toolBox.addItem(self.variables_tab, u"Variables")
        self.vis_options_tab = QWidget()
        self.vis_options_tab.setObjectName(u"vis_options_tab")
        self.vis_options_tab.setGeometry(QRect(0, 0, 372, 404))
        self.verticalLayout = QVBoxLayout(self.vis_options_tab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.saveFrame_button = QPushButton(self.vis_options_tab)
        self.saveFrame_button.setObjectName(u"saveFrame_button")
        icon3 = QIcon()
        icon3.addFile(u":/material_icons/material_icons/png/content-save.png", QSize(), QIcon.Normal, QIcon.Off)
        self.saveFrame_button.setIcon(icon3)

        self.verticalLayout.addWidget(self.saveFrame_button)

        self.display_options_label = QLabel(self.vis_options_tab)
        self.display_options_label.setObjectName(u"display_options_label")
        self.display_options_label.setFont(font1)

        self.verticalLayout.addWidget(self.display_options_label)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.zoom_label = QLabel(self.vis_options_tab)
        self.zoom_label.setObjectName(u"zoom_label")

        self.gridLayout_5.addWidget(self.zoom_label, 0, 0, 1, 1)

        self.zoom_slider = QSlider(self.vis_options_tab)
        self.zoom_slider.setObjectName(u"zoom_slider")
        sizePolicy11 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy11.setHorizontalStretch(0)
        sizePolicy11.setVerticalStretch(0)
        sizePolicy11.setHeightForWidth(self.zoom_slider.sizePolicy().hasHeightForWidth())
        self.zoom_slider.setSizePolicy(sizePolicy11)
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(8)
        font2.setBold(True)
        font2.setItalic(False)
        self.zoom_slider.setFont(font2)
        self.zoom_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.zoom_slider, 0, 1, 1, 1)

        self.pointsize_label = QLabel(self.vis_options_tab)
        self.pointsize_label.setObjectName(u"pointsize_label")

        self.gridLayout_5.addWidget(self.pointsize_label, 1, 0, 1, 1)

        self.point_slider = QSlider(self.vis_options_tab)
        self.point_slider.setObjectName(u"point_slider")
        self.point_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.point_slider, 1, 1, 1, 1)

        self.brightness_label = QLabel(self.vis_options_tab)
        self.brightness_label.setObjectName(u"brightness_label")
        self.brightness_label.setEnabled(False)

        self.gridLayout_5.addWidget(self.brightness_label, 2, 0, 1, 1)

        self.brightness_slider = QSlider(self.vis_options_tab)
        self.brightness_slider.setObjectName(u"brightness_slider")
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.brightness_slider, 2, 1, 1, 1)

        self.resolution_label = QLabel(self.vis_options_tab)
        self.resolution_label.setObjectName(u"resolution_label")
        self.resolution_label.setEnabled(False)

        self.gridLayout_5.addWidget(self.resolution_label, 3, 0, 1, 1)

        self.resolution_slider = QSlider(self.vis_options_tab)
        self.resolution_slider.setObjectName(u"resolution_slider")
        self.resolution_slider.setEnabled(False)
        self.resolution_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.resolution_slider, 3, 1, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout_5)

        self.point_type_label = QLabel(self.vis_options_tab)
        self.point_type_label.setObjectName(u"point_type_label")
        self.point_type_label.setEnabled(True)
        self.point_type_label.setFont(font1)

        self.verticalLayout.addWidget(self.point_type_label)

        self.pointtype_comboBox = QComboBox(self.vis_options_tab)
        self.pointtype_comboBox.setObjectName(u"pointtype_comboBox")
        self.pointtype_comboBox.setEnabled(True)

        self.verticalLayout.addWidget(self.pointtype_comboBox)

        self.colour_mode_label = QLabel(self.vis_options_tab)
        self.colour_mode_label.setObjectName(u"colour_mode_label")
        self.colour_mode_label.setFont(font1)

        self.verticalLayout.addWidget(self.colour_mode_label)

        self.colourmode_comboBox = QComboBox(self.vis_options_tab)
        self.colourmode_comboBox.setObjectName(u"colourmode_comboBox")

        self.verticalLayout.addWidget(self.colourmode_comboBox)

        self.colour_label = QLabel(self.vis_options_tab)
        self.colour_label.setObjectName(u"colour_label")
        self.colour_label.setFont(font1)

        self.verticalLayout.addWidget(self.colour_label)

        self.colour_comboBox = QComboBox(self.vis_options_tab)
        self.colour_comboBox.setObjectName(u"colour_comboBox")

        self.verticalLayout.addWidget(self.colour_comboBox)

        self.colour_label_2 = QLabel(self.vis_options_tab)
        self.colour_label_2.setObjectName(u"colour_label_2")
        self.colour_label_2.setFont(font1)

        self.verticalLayout.addWidget(self.colour_label_2)

        self.bgcolour_comboBox = QComboBox(self.vis_options_tab)
        self.bgcolour_comboBox.setObjectName(u"bgcolour_comboBox")

        self.verticalLayout.addWidget(self.bgcolour_comboBox)

        self.main_toolBox.addItem(self.vis_options_tab, u"Visualiser Options")
        self.video_options_tab = QWidget()
        self.video_options_tab.setObjectName(u"video_options_tab")
        self.video_options_tab.setGeometry(QRect(0, 0, 387, 370))
        self.gridLayout_11 = QGridLayout(self.video_options_tab)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.pause_button = QPushButton(self.video_options_tab)
        self.pause_button.setObjectName(u"pause_button")
        self.pause_button.setMinimumSize(QSize(0, 45))
        icon4 = QIcon()
        icon4.addFile(u":/material_icons/material_icons/png/pause-box.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pause_button.setIcon(icon4)

        self.gridLayout_11.addWidget(self.pause_button, 2, 1, 1, 1)

        self.end_simvis_button = QPushButton(self.video_options_tab)
        self.end_simvis_button.setObjectName(u"end_simvis_button")
        self.end_simvis_button.setMinimumSize(QSize(0, 45))
        icon5 = QIcon()
        icon5.addFile(u":/material_icons/material_icons/png/step-forward-2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.end_simvis_button.setIcon(icon5)

        self.gridLayout_11.addWidget(self.end_simvis_button, 13, 1, 1, 1)

        self.play_button = QPushButton(self.video_options_tab)
        self.play_button.setObjectName(u"play_button")
        self.play_button.setMinimumSize(QSize(0, 45))
        icon6 = QIcon()
        icon6.addFile(u":/material_icons/material_icons/png/play-box.png", QSize(), QIcon.Normal, QIcon.Off)
        self.play_button.setIcon(icon6)

        self.gridLayout_11.addWidget(self.play_button, 2, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_11.addItem(self.verticalSpacer_2, 18, 0, 1, 1)

        self.current_frame_spinBox = QSpinBox(self.video_options_tab)
        self.current_frame_spinBox.setObjectName(u"current_frame_spinBox")
        self.current_frame_spinBox.setMinimumSize(QSize(0, 20))

        self.gridLayout_11.addWidget(self.current_frame_spinBox, 0, 1, 1, 1)

        self.current_frame_comboBox = QComboBox(self.video_options_tab)
        self.current_frame_comboBox.setObjectName(u"current_frame_comboBox")
        self.current_frame_comboBox.setMinimumSize(QSize(0, 20))

        self.gridLayout_11.addWidget(self.current_frame_comboBox, 1, 0, 1, 2)

        self.frame_slider = QSlider(self.video_options_tab)
        self.frame_slider.setObjectName(u"frame_slider")
        self.frame_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_11.addWidget(self.frame_slider, 14, 0, 1, 2)

        self.start_simvis_button = QPushButton(self.video_options_tab)
        self.start_simvis_button.setObjectName(u"start_simvis_button")
        self.start_simvis_button.setMinimumSize(QSize(0, 45))
        icon7 = QIcon()
        icon7.addFile(u":/material_icons/material_icons/png/step-backward-2.png", QSize(), QIcon.Normal, QIcon.Off)
        self.start_simvis_button.setIcon(icon7)

        self.gridLayout_11.addWidget(self.start_simvis_button, 13, 0, 1, 1)

        self.current_frame_label = QLabel(self.video_options_tab)
        self.current_frame_label.setObjectName(u"current_frame_label")

        self.gridLayout_11.addWidget(self.current_frame_label, 0, 0, 1, 1)

        self.previous_button = QPushButton(self.video_options_tab)
        self.previous_button.setObjectName(u"previous_button")
        self.previous_button.setMinimumSize(QSize(0, 40))
        icon8 = QIcon()
        icon8.addFile(u":/material_icons/material_icons/png/step-backward.png", QSize(), QIcon.Normal, QIcon.Off)
        self.previous_button.setIcon(icon8)

        self.gridLayout_11.addWidget(self.previous_button, 4, 0, 1, 1)

        self.next_button = QPushButton(self.video_options_tab)
        self.next_button.setObjectName(u"next_button")
        self.next_button.setMinimumSize(QSize(0, 45))
        icon9 = QIcon()
        icon9.addFile(u":/material_icons/material_icons/png/step-forward.png", QSize(), QIcon.Normal, QIcon.Off)
        self.next_button.setIcon(icon9)

        self.gridLayout_11.addWidget(self.next_button, 4, 1, 1, 1)

        self.main_toolBox.addItem(self.video_options_tab, u"Video Options")

        self.gridLayout_12.addWidget(self.main_toolBox, 1, 0, 1, 1)

        self.scrollArea_options.setWidget(self.scrollAreaWidgetContents_5)

        self.gridLayout.addWidget(self.scrollArea_options, 3, 0, 1, 3)

        self.open_saved_pushButton = QPushButton(self.centralwidget)
        self.open_saved_pushButton.setObjectName(u"open_saved_pushButton")
        self.open_saved_pushButton.setEnabled(False)
        sizePolicy.setHeightForWidth(self.open_saved_pushButton.sizePolicy().hasHeightForWidth())
        self.open_saved_pushButton.setSizePolicy(sizePolicy)
        self.open_saved_pushButton.setMinimumSize(QSize(150, 45))
        self.open_saved_pushButton.setBaseSize(QSize(0, 0))
        icon10 = QIcon()
        icon10.addFile(u":/material_icons/material_icons/png/folder-arrow-right.png", QSize(), QIcon.Normal, QIcon.Off)
        self.open_saved_pushButton.setIcon(icon10)
        self.open_saved_pushButton.setIconSize(QSize(20, 20))

        self.gridLayout.addWidget(self.open_saved_pushButton, 0, 8, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        font3 = QFont()
        font3.setFamilies([u"Arial"])
        font3.setPointSize(8)
        font3.setItalic(True)
        self.statusbar.setFont(font3)
        self.statusbar.setCursor(QCursor(Qt.ArrowCursor))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.main_toolBox.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"CrystalAspects", None))
        self.actionOpen_Simulations.setText(QCoreApplication.translate("MainWindow", u"Open Simulations", None))
        self.actionOpen_XYZs.setText(QCoreApplication.translate("MainWindow", u"Open XYZs", None))
        self.actionOpen_Outputs.setText(QCoreApplication.translate("MainWindow", u"Open Outputs", None))
        self.actionAmber.setText(QCoreApplication.translate("MainWindow", u"Amber", None))
        self.actionBlue.setText(QCoreApplication.translate("MainWindow", u"Blue", None))
        self.actionCyan.setText(QCoreApplication.translate("MainWindow", u"Cyan", None))
        self.actionCyan_500.setText(QCoreApplication.translate("MainWindow", u"Cyan-500", None))
        self.actionLight_green.setText(QCoreApplication.translate("MainWindow", u"Light-green", None))
        self.actionPink.setText(QCoreApplication.translate("MainWindow", u"Pink", None))
        self.actionPurple.setText(QCoreApplication.translate("MainWindow", u"Purple", None))
        self.actionRed_2.setText(QCoreApplication.translate("MainWindow", u"Red", None))
        self.actionTeal.setText(QCoreApplication.translate("MainWindow", u"Teal", None))
        self.actionYellow.setText(QCoreApplication.translate("MainWindow", u"Yellow", None))
        self.actionAmber_2.setText(QCoreApplication.translate("MainWindow", u"Amber", None))
        self.actionBlue_2.setText(QCoreApplication.translate("MainWindow", u"Blue", None))
        self.actionCyan_2.setText(QCoreApplication.translate("MainWindow", u"Cyan", None))
        self.actionLight_green_2.setText(QCoreApplication.translate("MainWindow", u"Light-green", None))
        self.actionPink_2.setText(QCoreApplication.translate("MainWindow", u"Pink", None))
        self.actionPurple_2.setText(QCoreApplication.translate("MainWindow", u"Purple", None))
        self.actionRed.setText(QCoreApplication.translate("MainWindow", u"Red", None))
        self.actionTeal_2.setText(QCoreApplication.translate("MainWindow", u"Teal", None))
        self.actionCyan_501.setText(QCoreApplication.translate("MainWindow", u"Cyan-500", None))
        self.actionLight_green_3.setText(QCoreApplication.translate("MainWindow", u"Light-green", None))
        self.actionPink_3.setText(QCoreApplication.translate("MainWindow", u"Pink", None))
        self.actionPurple_3.setText(QCoreApplication.translate("MainWindow", u"Purple", None))
        self.actionRed_3.setText(QCoreApplication.translate("MainWindow", u"Red", None))
        self.actionTeal_3.setText(QCoreApplication.translate("MainWindow", u"Teal", None))
        self.actionYellow_2.setText(QCoreApplication.translate("MainWindow", u"Yellow", None))
        self.action_5.setText(QCoreApplication.translate("MainWindow", u"-5", None))
        self.action_4.setText(QCoreApplication.translate("MainWindow", u"-4", None))
        self.action_6.setText(QCoreApplication.translate("MainWindow", u"-3", None))
        self.action_7.setText(QCoreApplication.translate("MainWindow", u"-2", None))
        self.action_1.setText(QCoreApplication.translate("MainWindow", u"-1", None))
        self.action0.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.action1.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.action2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.action3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.action4.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.action5.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.actionDensity_2.setText(QCoreApplication.translate("MainWindow", u"Density", None))
        self.actionStyle.setText(QCoreApplication.translate("MainWindow", u"Style", None))
        self.action_8.setText(QCoreApplication.translate("MainWindow", u"-4", None))
        self.action_9.setText(QCoreApplication.translate("MainWindow", u"-3", None))
        self.action_10.setText(QCoreApplication.translate("MainWindow", u"-2", None))
        self.action_11.setText(QCoreApplication.translate("MainWindow", u"-1", None))
        self.action0_2.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.action1_2.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.action2_2.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.action3_2.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.action4_2.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.action_12.setText(QCoreApplication.translate("MainWindow", u"-3", None))
        self.action_13.setText(QCoreApplication.translate("MainWindow", u"-2", None))
        self.action_14.setText(QCoreApplication.translate("MainWindow", u"-1", None))
        self.action0_3.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.action1_3.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.action2_3.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.action3_3.setText(QCoreApplication.translate("MainWindow", u"3", None))
        self.import_pushButton.setText(QCoreApplication.translate("MainWindow", u"   Import", None))
        self.settings_toolButton.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.console_label.setText(QCoreApplication.translate("MainWindow", u"Console", None))
        self.main_toolBox.setItemText(self.main_toolBox.indexOf(self.batch_analysis_tab), QCoreApplication.translate("MainWindow", u"Batch Analysis", None))
        self.main_toolBox.setItemText(self.main_toolBox.indexOf(self.plotting_tab), QCoreApplication.translate("MainWindow", u"Plotting", None))
        self.ml_label.setText(QCoreApplication.translate("MainWindow", u"Medium/Long:", None))
        self.crystal_savol_label.setText(QCoreApplication.translate("MainWindow", u"Surface Area:Volume:", None))
        self.spacegroup_label.setText(QCoreApplication.translate("MainWindow", u"Space group:", None))
        self.crystal_ar_label.setText(QCoreApplication.translate("MainWindow", u"Aspect Ratio", None))
        self.show_info_button.setText(QCoreApplication.translate("MainWindow", u"Show Information", None))
        self.sm_label.setText(QCoreApplication.translate("MainWindow", u"Short/Medium:", None))
        self.crystal_vol_label.setText(QCoreApplication.translate("MainWindow", u"Crystal Volume (nm<sup>2</sup>):", None))
        self.fname_label.setText(QCoreApplication.translate("MainWindow", u"Filename:", None))
        self.crystal_sa_label.setText(QCoreApplication.translate("MainWindow", u"Crystal Surface Area (nm<sup>2</sup>):", None))
        self.shape_label.setText(QCoreApplication.translate("MainWindow", u"General Shape:", None))
        self.main_toolBox.setItemText(self.main_toolBox.indexOf(self.crystal_info_tab), QCoreApplication.translate("MainWindow", u"Crystal Information", None))
        self.EVariable_title_label_2.setText(QCoreApplication.translate("MainWindow", u"Variables:", None))
        self.select_summary_slider_button.setText(QCoreApplication.translate("MainWindow", u"Select Summary File", None))
        self.main_toolBox.setItemText(self.main_toolBox.indexOf(self.variables_tab), QCoreApplication.translate("MainWindow", u"Variables", None))
        self.saveFrame_button.setText(QCoreApplication.translate("MainWindow", u"   Save Frame", None))
        self.display_options_label.setText(QCoreApplication.translate("MainWindow", u"Display Options", None))
        self.zoom_label.setText(QCoreApplication.translate("MainWindow", u"Zoom", None))
        self.pointsize_label.setText(QCoreApplication.translate("MainWindow", u"Point Size", None))
        self.brightness_label.setText(QCoreApplication.translate("MainWindow", u"Brightness", None))
        self.resolution_label.setText(QCoreApplication.translate("MainWindow", u"Resolution", None))
        self.point_type_label.setText(QCoreApplication.translate("MainWindow", u"Point Type", None))
        self.colour_mode_label.setText(QCoreApplication.translate("MainWindow", u"Colour Mode", None))
        self.colour_label.setText(QCoreApplication.translate("MainWindow", u"Colour", None))
        self.colour_label_2.setText(QCoreApplication.translate("MainWindow", u"Background Colour", None))
        self.main_toolBox.setItemText(self.main_toolBox.indexOf(self.vis_options_tab), QCoreApplication.translate("MainWindow", u"Visualiser Options", None))
        self.pause_button.setText(QCoreApplication.translate("MainWindow", u"   Pause", None))
        self.end_simvis_button.setText(QCoreApplication.translate("MainWindow", u"   End", None))
        self.play_button.setText(QCoreApplication.translate("MainWindow", u"   Play", None))
        self.start_simvis_button.setText(QCoreApplication.translate("MainWindow", u"   Start", None))
        self.current_frame_label.setText(QCoreApplication.translate("MainWindow", u"Current Frame", None))
        self.previous_button.setText(QCoreApplication.translate("MainWindow", u"   Previous", None))
        self.next_button.setText(QCoreApplication.translate("MainWindow", u"   Next", None))
        self.main_toolBox.setItemText(self.main_toolBox.indexOf(self.video_options_tab), QCoreApplication.translate("MainWindow", u"Video Options", None))
        self.open_saved_pushButton.setText(QCoreApplication.translate("MainWindow", u"   View Results", None))
    # retranslateUi

