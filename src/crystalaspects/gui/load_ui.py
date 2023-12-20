# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon, QImage,
                           QKeySequence, QLinearGradient, QPainter, QPalette,
                           QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
                               QHBoxLayout, QLabel, QLayout, QMainWindow,
                               QProgressBar, QPushButton, QScrollArea,
                               QSizePolicy, QSlider, QSpacerItem, QSpinBox,
                               QStatusBar, QTextEdit, QToolBox, QVBoxLayout,
                               QWidget)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1400, 847)
        font = QFont()
        font.setFamilies(["Arial"])
        font.setPointSize(10)
        MainWindow.setFont(font)
        icon = QIcon()
        icon.addFile("../../../res/icon.png", QSize(), QIcon.Normal, QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.actionOpen_Simulations = QAction(MainWindow)
        self.actionOpen_Simulations.setObjectName("actionOpen_Simulations")
        self.actionOpen_XYZs = QAction(MainWindow)
        self.actionOpen_XYZs.setObjectName("actionOpen_XYZs")
        self.actionOpen_Outputs = QAction(MainWindow)
        self.actionOpen_Outputs.setObjectName("actionOpen_Outputs")
        self.actionAmber = QAction(MainWindow)
        self.actionAmber.setObjectName("actionAmber")
        self.actionBlue = QAction(MainWindow)
        self.actionBlue.setObjectName("actionBlue")
        self.actionCyan = QAction(MainWindow)
        self.actionCyan.setObjectName("actionCyan")
        self.actionCyan_500 = QAction(MainWindow)
        self.actionCyan_500.setObjectName("actionCyan_500")
        self.actionLight_green = QAction(MainWindow)
        self.actionLight_green.setObjectName("actionLight_green")
        self.actionPink = QAction(MainWindow)
        self.actionPink.setObjectName("actionPink")
        self.actionPurple = QAction(MainWindow)
        self.actionPurple.setObjectName("actionPurple")
        self.actionRed_2 = QAction(MainWindow)
        self.actionRed_2.setObjectName("actionRed_2")
        self.actionTeal = QAction(MainWindow)
        self.actionTeal.setObjectName("actionTeal")
        self.actionYellow = QAction(MainWindow)
        self.actionYellow.setObjectName("actionYellow")
        self.actionAmber_2 = QAction(MainWindow)
        self.actionAmber_2.setObjectName("actionAmber_2")
        self.actionBlue_2 = QAction(MainWindow)
        self.actionBlue_2.setObjectName("actionBlue_2")
        self.actionCyan_2 = QAction(MainWindow)
        self.actionCyan_2.setObjectName("actionCyan_2")
        self.actionLight_green_2 = QAction(MainWindow)
        self.actionLight_green_2.setObjectName("actionLight_green_2")
        self.actionPink_2 = QAction(MainWindow)
        self.actionPink_2.setObjectName("actionPink_2")
        self.actionPurple_2 = QAction(MainWindow)
        self.actionPurple_2.setObjectName("actionPurple_2")
        self.actionRed = QAction(MainWindow)
        self.actionRed.setObjectName("actionRed")
        self.actionTeal_2 = QAction(MainWindow)
        self.actionTeal_2.setObjectName("actionTeal_2")
        self.actionCyan_501 = QAction(MainWindow)
        self.actionCyan_501.setObjectName("actionCyan_501")
        self.actionLight_green_3 = QAction(MainWindow)
        self.actionLight_green_3.setObjectName("actionLight_green_3")
        self.actionPink_3 = QAction(MainWindow)
        self.actionPink_3.setObjectName("actionPink_3")
        self.actionPurple_3 = QAction(MainWindow)
        self.actionPurple_3.setObjectName("actionPurple_3")
        self.actionRed_3 = QAction(MainWindow)
        self.actionRed_3.setObjectName("actionRed_3")
        self.actionTeal_3 = QAction(MainWindow)
        self.actionTeal_3.setObjectName("actionTeal_3")
        self.actionYellow_2 = QAction(MainWindow)
        self.actionYellow_2.setObjectName("actionYellow_2")
        self.action_5 = QAction(MainWindow)
        self.action_5.setObjectName("action_5")
        self.action_5.setCheckable(False)
        self.action_4 = QAction(MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_6 = QAction(MainWindow)
        self.action_6.setObjectName("action_6")
        self.action_7 = QAction(MainWindow)
        self.action_7.setObjectName("action_7")
        self.action_1 = QAction(MainWindow)
        self.action_1.setObjectName("action_1")
        self.action0 = QAction(MainWindow)
        self.action0.setObjectName("action0")
        self.action1 = QAction(MainWindow)
        self.action1.setObjectName("action1")
        self.action2 = QAction(MainWindow)
        self.action2.setObjectName("action2")
        self.action3 = QAction(MainWindow)
        self.action3.setObjectName("action3")
        self.action4 = QAction(MainWindow)
        self.action4.setObjectName("action4")
        self.action5 = QAction(MainWindow)
        self.action5.setObjectName("action5")
        self.actionDensity_2 = QAction(MainWindow)
        self.actionDensity_2.setObjectName("actionDensity_2")
        self.actionStyle = QAction(MainWindow)
        self.actionStyle.setObjectName("actionStyle")
        self.action_8 = QAction(MainWindow)
        self.action_8.setObjectName("action_8")
        self.action_9 = QAction(MainWindow)
        self.action_9.setObjectName("action_9")
        self.action_10 = QAction(MainWindow)
        self.action_10.setObjectName("action_10")
        self.action_11 = QAction(MainWindow)
        self.action_11.setObjectName("action_11")
        self.action0_2 = QAction(MainWindow)
        self.action0_2.setObjectName("action0_2")
        self.action1_2 = QAction(MainWindow)
        self.action1_2.setObjectName("action1_2")
        self.action2_2 = QAction(MainWindow)
        self.action2_2.setObjectName("action2_2")
        self.action3_2 = QAction(MainWindow)
        self.action3_2.setObjectName("action3_2")
        self.action4_2 = QAction(MainWindow)
        self.action4_2.setObjectName("action4_2")
        self.action_12 = QAction(MainWindow)
        self.action_12.setObjectName("action_12")
        self.action_13 = QAction(MainWindow)
        self.action_13.setObjectName("action_13")
        self.action_14 = QAction(MainWindow)
        self.action_14.setObjectName("action_14")
        self.action0_3 = QAction(MainWindow)
        self.action0_3.setObjectName("action0_3")
        self.action1_3 = QAction(MainWindow)
        self.action1_3.setObjectName("action1_3")
        self.action2_3 = QAction(MainWindow)
        self.action2_3.setObjectName("action2_3")
        self.action3_3 = QAction(MainWindow)
        self.action3_3.setObjectName("action3_3")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.vis_scrollArea = QScrollArea(self.centralwidget)
        self.vis_scrollArea.setObjectName("vis_scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(20)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.vis_scrollArea.sizePolicy().hasHeightForWidth()
        )
        self.vis_scrollArea.setSizePolicy(sizePolicy)
        self.vis_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName("scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 909, 801))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.main_frame = QFrame(self.scrollAreaWidgetContents_3)
        self.main_frame.setObjectName("main_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(5)
        sizePolicy1.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(sizePolicy1)
        self.gl_vLayout = QGridLayout(self.main_frame)
        self.gl_vLayout.setObjectName("gl_vLayout")

        self.gridLayout_4.addWidget(self.main_frame, 0, 1, 1, 2)

        self.vis_scrollArea.setWidget(self.scrollAreaWidgetContents_3)

        self.gridLayout.addWidget(self.vis_scrollArea, 0, 2, 3, 1)

        self.scrollArea_options = QScrollArea(self.centralwidget)
        self.scrollArea_options.setObjectName("scrollArea_options")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(4)
        sizePolicy2.setHeightForWidth(
            self.scrollArea_options.sizePolicy().hasHeightForWidth()
        )
        self.scrollArea_options.setSizePolicy(sizePolicy2)
        self.scrollArea_options.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName("scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 453, 613))
        self.gridLayout_12 = QGridLayout(self.scrollAreaWidgetContents_5)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.main_toolBox = QToolBox(self.scrollAreaWidgetContents_5)
        self.main_toolBox.setObjectName("main_toolBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(3)
        sizePolicy3.setHeightForWidth(
            self.main_toolBox.sizePolicy().hasHeightForWidth()
        )
        self.main_toolBox.setSizePolicy(sizePolicy3)
        self.main_toolBox.setMinimumSize(QSize(0, 450))
        self.batch_analysis_tab = QWidget()
        self.batch_analysis_tab.setObjectName("batch_analysis_tab")
        self.batch_analysis_tab.setGeometry(QRect(0, 0, 661, 408))
        self.gridLayout_6 = QGridLayout(self.batch_analysis_tab)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.progressBar = QProgressBar(self.batch_analysis_tab)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet(
            "QProgressBar {\n"
            "	background-color: rgb(213, 215, 255);\n"
            "	color: rgb(0, 0, 127);\n"
            "	border-style: none;\n"
            "	border-radius: 10px;\n"
            "	text-align: center;\n"
            "}\n"
            "QProgressBar::chunk{\n"
            "	border-radius: 10px;\n"
            "	background-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.489, stop:0 rgba(255, 170, 255, 255), stop:1 rgba(185, 135, 255, 255));\n"
            "}"
        )
        self.progressBar.setValue(0)

        self.gridLayout_6.addWidget(self.progressBar, 1, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout_6.addItem(self.verticalSpacer_3, 0, 0, 1, 1)

        self.main_toolBox.addItem(self.batch_analysis_tab, "Batch Analysis")
        self.plotting_tab = QWidget()
        self.plotting_tab.setObjectName("plotting_tab")
        self.plotting_tab.setGeometry(QRect(0, 0, 661, 408))
        self.main_toolBox.addItem(self.plotting_tab, "Plotting")
        self.crystal_info_tab = QWidget()
        self.crystal_info_tab.setObjectName("crystal_info_tab")
        self.crystal_info_tab.setGeometry(QRect(0, 0, 429, 409))
        self.gridLayout_2 = QGridLayout(self.crystal_info_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.ml_label = QLabel(self.crystal_info_tab)
        self.ml_label.setObjectName("ml_label")

        self.gridLayout_2.addWidget(self.ml_label, 5, 0, 1, 1)

        self.crystal_savol_label = QLabel(self.crystal_info_tab)
        self.crystal_savol_label.setObjectName("crystal_savol_label")

        self.gridLayout_2.addWidget(self.crystal_savol_label, 7, 0, 1, 1)

        self.spacegroup_label = QLabel(self.crystal_info_tab)
        self.spacegroup_label.setObjectName("spacegroup_label")
        self.spacegroup_label.setEnabled(False)

        self.gridLayout_2.addWidget(self.spacegroup_label, 2, 0, 1, 1)

        self.crystal_ar_label = QLabel(self.crystal_info_tab)
        self.crystal_ar_label.setObjectName("crystal_ar_label")

        self.gridLayout_2.addWidget(self.crystal_ar_label, 3, 0, 1, 1)

        self.show_info_button = QPushButton(self.crystal_info_tab)
        self.show_info_button.setObjectName("show_info_button")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(
            self.show_info_button.sizePolicy().hasHeightForWidth()
        )
        self.show_info_button.setSizePolicy(sizePolicy4)
        self.show_info_button.setMinimumSize(QSize(200, 0))

        self.gridLayout_2.addWidget(self.show_info_button, 1, 0, 1, 1)

        self.sm_label = QLabel(self.crystal_info_tab)
        self.sm_label.setObjectName("sm_label")

        self.gridLayout_2.addWidget(self.sm_label, 4, 0, 1, 1)

        self.crystal_vol_label = QLabel(self.crystal_info_tab)
        self.crystal_vol_label.setObjectName("crystal_vol_label")

        self.gridLayout_2.addWidget(self.crystal_vol_label, 9, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.fname_label = QLabel(self.crystal_info_tab)
        self.fname_label.setObjectName("fname_label")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(1)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.fname_label.sizePolicy().hasHeightForWidth())
        self.fname_label.setSizePolicy(sizePolicy5)

        self.horizontalLayout.addWidget(self.fname_label)

        self.fname_comboBox = QComboBox(self.crystal_info_tab)
        self.fname_comboBox.setObjectName("fname_comboBox")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(3)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(
            self.fname_comboBox.sizePolicy().hasHeightForWidth()
        )
        self.fname_comboBox.setSizePolicy(sizePolicy6)
        self.fname_comboBox.setMinimumSize(QSize(200, 0))

        self.horizontalLayout.addWidget(self.fname_comboBox)

        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.crystal_sa_label = QLabel(self.crystal_info_tab)
        self.crystal_sa_label.setObjectName("crystal_sa_label")

        self.gridLayout_2.addWidget(self.crystal_sa_label, 8, 0, 1, 1)

        self.shape_label = QLabel(self.crystal_info_tab)
        self.shape_label.setObjectName("shape_label")

        self.gridLayout_2.addWidget(self.shape_label, 6, 0, 1, 1)

        self.main_toolBox.addItem(self.crystal_info_tab, "Crystal Information")
        self.variables_tab = QWidget()
        self.variables_tab.setObjectName("variables_tab")
        self.variables_tab.setGeometry(QRect(0, 0, 661, 408))
        self.gridLayout_7 = QGridLayout(self.variables_tab)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.EVariable_title_label_2 = QLabel(self.variables_tab)
        self.EVariable_title_label_2.setObjectName("EVariable_title_label_2")
        font1 = QFont()
        font1.setFamilies(["Arial"])
        font1.setPointSize(10)
        font1.setBold(True)
        font1.setItalic(False)
        self.EVariable_title_label_2.setFont(font1)

        self.gridLayout_7.addWidget(self.EVariable_title_label_2, 1, 0, 1, 1)

        self.select_summary_slider_button = QPushButton(self.variables_tab)
        self.select_summary_slider_button.setObjectName("select_summary_slider_button")
        self.select_summary_slider_button.setEnabled(False)
        sizePolicy7 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(1)
        sizePolicy7.setHeightForWidth(
            self.select_summary_slider_button.sizePolicy().hasHeightForWidth()
        )
        self.select_summary_slider_button.setSizePolicy(sizePolicy7)
        self.select_summary_slider_button.setMinimumSize(QSize(200, 0))
        self.select_summary_slider_button.setFont(font1)

        self.gridLayout_7.addWidget(
            self.select_summary_slider_button, 0, 0, 1, 1, Qt.AlignLeft
        )

        self.E_variables_layout = QGridLayout()
        self.E_variables_layout.setObjectName("E_variables_layout")
        self.E_variables_layout.setSizeConstraint(QLayout.SetNoConstraint)

        self.gridLayout_7.addLayout(self.E_variables_layout, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout_7.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.main_toolBox.addItem(self.variables_tab, "Variables")
        self.vis_options_tab = QWidget()
        self.vis_options_tab.setObjectName("vis_options_tab")
        self.vis_options_tab.setGeometry(QRect(0, 0, 661, 408))
        self.verticalLayout = QVBoxLayout(self.vis_options_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.saveFrame_button = QPushButton(self.vis_options_tab)
        self.saveFrame_button.setObjectName("saveFrame_button")

        self.verticalLayout.addWidget(self.saveFrame_button)

        self.display_options_label = QLabel(self.vis_options_tab)
        self.display_options_label.setObjectName("display_options_label")
        self.display_options_label.setFont(font1)

        self.verticalLayout.addWidget(self.display_options_label)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.zoom_label = QLabel(self.vis_options_tab)
        self.zoom_label.setObjectName("zoom_label")

        self.gridLayout_5.addWidget(self.zoom_label, 0, 0, 1, 1)

        self.zoom_slider = QSlider(self.vis_options_tab)
        self.zoom_slider.setObjectName("zoom_slider")
        sizePolicy8 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.zoom_slider.sizePolicy().hasHeightForWidth())
        self.zoom_slider.setSizePolicy(sizePolicy8)
        font2 = QFont()
        font2.setFamilies(["Arial"])
        font2.setPointSize(8)
        font2.setBold(True)
        font2.setItalic(False)
        self.zoom_slider.setFont(font2)
        self.zoom_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.zoom_slider, 0, 1, 1, 1)

        self.pointsize_label = QLabel(self.vis_options_tab)
        self.pointsize_label.setObjectName("pointsize_label")

        self.gridLayout_5.addWidget(self.pointsize_label, 1, 0, 1, 1)

        self.point_slider = QSlider(self.vis_options_tab)
        self.point_slider.setObjectName("point_slider")
        self.point_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.point_slider, 1, 1, 1, 1)

        self.brightness_label = QLabel(self.vis_options_tab)
        self.brightness_label.setObjectName("brightness_label")
        self.brightness_label.setEnabled(False)

        self.gridLayout_5.addWidget(self.brightness_label, 2, 0, 1, 1)

        self.brightness_slider = QSlider(self.vis_options_tab)
        self.brightness_slider.setObjectName("brightness_slider")
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.brightness_slider, 2, 1, 1, 1)

        self.resolution_label = QLabel(self.vis_options_tab)
        self.resolution_label.setObjectName("resolution_label")
        self.resolution_label.setEnabled(False)

        self.gridLayout_5.addWidget(self.resolution_label, 3, 0, 1, 1)

        self.resolution_slider = QSlider(self.vis_options_tab)
        self.resolution_slider.setObjectName("resolution_slider")
        self.resolution_slider.setEnabled(False)
        self.resolution_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_5.addWidget(self.resolution_slider, 3, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout_5)

        self.point_type_label = QLabel(self.vis_options_tab)
        self.point_type_label.setObjectName("point_type_label")
        self.point_type_label.setEnabled(True)
        self.point_type_label.setFont(font1)

        self.verticalLayout.addWidget(self.point_type_label)

        self.pointtype_comboBox = QComboBox(self.vis_options_tab)
        self.pointtype_comboBox.setObjectName("pointtype_comboBox")
        self.pointtype_comboBox.setEnabled(True)

        self.verticalLayout.addWidget(self.pointtype_comboBox)

        self.colour_mode_label = QLabel(self.vis_options_tab)
        self.colour_mode_label.setObjectName("colour_mode_label")
        self.colour_mode_label.setFont(font1)

        self.verticalLayout.addWidget(self.colour_mode_label)

        self.colourmode_comboBox = QComboBox(self.vis_options_tab)
        self.colourmode_comboBox.setObjectName("colourmode_comboBox")

        self.verticalLayout.addWidget(self.colourmode_comboBox)

        self.colour_label = QLabel(self.vis_options_tab)
        self.colour_label.setObjectName("colour_label")
        self.colour_label.setFont(font1)

        self.verticalLayout.addWidget(self.colour_label)

        self.colour_comboBox = QComboBox(self.vis_options_tab)
        self.colour_comboBox.setObjectName("colour_comboBox")

        self.verticalLayout.addWidget(self.colour_comboBox)

        self.colour_label_2 = QLabel(self.vis_options_tab)
        self.colour_label_2.setObjectName("colour_label_2")
        self.colour_label_2.setFont(font1)

        self.verticalLayout.addWidget(self.colour_label_2)

        self.bgcolour_comboBox = QComboBox(self.vis_options_tab)
        self.bgcolour_comboBox.setObjectName("bgcolour_comboBox")

        self.verticalLayout.addWidget(self.bgcolour_comboBox)

        self.main_toolBox.addItem(self.vis_options_tab, "Visualiser Options")
        self.video_options_tab = QWidget()
        self.video_options_tab.setObjectName("video_options_tab")
        self.video_options_tab.setGeometry(QRect(0, 0, 661, 408))
        self.gridLayout_11 = QGridLayout(self.video_options_tab)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.play_button = QPushButton(self.video_options_tab)
        self.play_button.setObjectName("play_button")

        self.gridLayout_11.addWidget(self.play_button, 3, 0, 1, 1)

        self.pause_button = QPushButton(self.video_options_tab)
        self.pause_button.setObjectName("pause_button")

        self.gridLayout_11.addWidget(self.pause_button, 3, 1, 1, 1)

        self.current_frame_label = QLabel(self.video_options_tab)
        self.current_frame_label.setObjectName("current_frame_label")

        self.gridLayout_11.addWidget(self.current_frame_label, 0, 0, 1, 1)

        self.start_simvis_button = QPushButton(self.video_options_tab)
        self.start_simvis_button.setObjectName("start_simvis_button")

        self.gridLayout_11.addWidget(self.start_simvis_button, 4, 0, 1, 1)

        self.end_simvis_button = QPushButton(self.video_options_tab)
        self.end_simvis_button.setObjectName("end_simvis_button")

        self.gridLayout_11.addWidget(self.end_simvis_button, 4, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

        self.gridLayout_11.addItem(self.verticalSpacer_2, 9, 0, 1, 1)

        self.current_frame_spinBox = QSpinBox(self.video_options_tab)
        self.current_frame_spinBox.setObjectName("current_frame_spinBox")

        self.gridLayout_11.addWidget(self.current_frame_spinBox, 0, 1, 1, 1)

        self.current_frame_comboBox = QComboBox(self.video_options_tab)
        self.current_frame_comboBox.setObjectName("current_frame_comboBox")

        self.gridLayout_11.addWidget(self.current_frame_comboBox, 1, 0, 1, 2)

        self.frame_slider = QSlider(self.video_options_tab)
        self.frame_slider.setObjectName("frame_slider")
        self.frame_slider.setOrientation(Qt.Horizontal)

        self.gridLayout_11.addWidget(self.frame_slider, 5, 0, 1, 2)

        self.main_toolBox.addItem(self.video_options_tab, "Video Options")

        self.gridLayout_12.addWidget(self.main_toolBox, 0, 0, 1, 1)

        self.scrollArea_options.setWidget(self.scrollAreaWidgetContents_5)

        self.gridLayout.addWidget(self.scrollArea_options, 0, 0, 1, 2)

        self.output_textbox = QTextEdit(self.centralwidget)
        self.output_textbox.setObjectName("output_textbox")
        sizePolicy9 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy9.setHorizontalStretch(5)
        sizePolicy9.setVerticalStretch(1)
        sizePolicy9.setHeightForWidth(
            self.output_textbox.sizePolicy().hasHeightForWidth()
        )
        self.output_textbox.setSizePolicy(sizePolicy9)
        self.output_textbox.setMinimumSize(QSize(0, 75))
        self.output_textbox.setStyleSheet(
            "background-color: rgb(58, 64, 85);\n" "color: rgb(255, 255, 255);"
        )

        self.gridLayout.addWidget(self.output_textbox, 2, 0, 1, 2)

        self.console_label = QLabel(self.centralwidget)
        self.console_label.setObjectName("console_label")
        sizePolicy10 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(
            self.console_label.sizePolicy().hasHeightForWidth()
        )
        self.console_label.setSizePolicy(sizePolicy10)
        self.console_label.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout.addWidget(self.console_label, 1, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        font3 = QFont()
        font3.setFamilies(["Arial"])
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
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "CrystalAspects", None)
        )
        self.actionOpen_Simulations.setText(
            QCoreApplication.translate("MainWindow", "Open Simulations", None)
        )
        self.actionOpen_XYZs.setText(
            QCoreApplication.translate("MainWindow", "Open XYZs", None)
        )
        self.actionOpen_Outputs.setText(
            QCoreApplication.translate("MainWindow", "Open Outputs", None)
        )
        self.actionAmber.setText(
            QCoreApplication.translate("MainWindow", "Amber", None)
        )
        self.actionBlue.setText(QCoreApplication.translate("MainWindow", "Blue", None))
        self.actionCyan.setText(QCoreApplication.translate("MainWindow", "Cyan", None))
        self.actionCyan_500.setText(
            QCoreApplication.translate("MainWindow", "Cyan-500", None)
        )
        self.actionLight_green.setText(
            QCoreApplication.translate("MainWindow", "Light-green", None)
        )
        self.actionPink.setText(QCoreApplication.translate("MainWindow", "Pink", None))
        self.actionPurple.setText(
            QCoreApplication.translate("MainWindow", "Purple", None)
        )
        self.actionRed_2.setText(QCoreApplication.translate("MainWindow", "Red", None))
        self.actionTeal.setText(QCoreApplication.translate("MainWindow", "Teal", None))
        self.actionYellow.setText(
            QCoreApplication.translate("MainWindow", "Yellow", None)
        )
        self.actionAmber_2.setText(
            QCoreApplication.translate("MainWindow", "Amber", None)
        )
        self.actionBlue_2.setText(
            QCoreApplication.translate("MainWindow", "Blue", None)
        )
        self.actionCyan_2.setText(
            QCoreApplication.translate("MainWindow", "Cyan", None)
        )
        self.actionLight_green_2.setText(
            QCoreApplication.translate("MainWindow", "Light-green", None)
        )
        self.actionPink_2.setText(
            QCoreApplication.translate("MainWindow", "Pink", None)
        )
        self.actionPurple_2.setText(
            QCoreApplication.translate("MainWindow", "Purple", None)
        )
        self.actionRed.setText(QCoreApplication.translate("MainWindow", "Red", None))
        self.actionTeal_2.setText(
            QCoreApplication.translate("MainWindow", "Teal", None)
        )
        self.actionCyan_501.setText(
            QCoreApplication.translate("MainWindow", "Cyan-500", None)
        )
        self.actionLight_green_3.setText(
            QCoreApplication.translate("MainWindow", "Light-green", None)
        )
        self.actionPink_3.setText(
            QCoreApplication.translate("MainWindow", "Pink", None)
        )
        self.actionPurple_3.setText(
            QCoreApplication.translate("MainWindow", "Purple", None)
        )
        self.actionRed_3.setText(QCoreApplication.translate("MainWindow", "Red", None))
        self.actionTeal_3.setText(
            QCoreApplication.translate("MainWindow", "Teal", None)
        )
        self.actionYellow_2.setText(
            QCoreApplication.translate("MainWindow", "Yellow", None)
        )
        self.action_5.setText(QCoreApplication.translate("MainWindow", "-5", None))
        self.action_4.setText(QCoreApplication.translate("MainWindow", "-4", None))
        self.action_6.setText(QCoreApplication.translate("MainWindow", "-3", None))
        self.action_7.setText(QCoreApplication.translate("MainWindow", "-2", None))
        self.action_1.setText(QCoreApplication.translate("MainWindow", "-1", None))
        self.action0.setText(QCoreApplication.translate("MainWindow", "0", None))
        self.action1.setText(QCoreApplication.translate("MainWindow", "1", None))
        self.action2.setText(QCoreApplication.translate("MainWindow", "2", None))
        self.action3.setText(QCoreApplication.translate("MainWindow", "3", None))
        self.action4.setText(QCoreApplication.translate("MainWindow", "4", None))
        self.action5.setText(QCoreApplication.translate("MainWindow", "5", None))
        self.actionDensity_2.setText(
            QCoreApplication.translate("MainWindow", "Density", None)
        )
        self.actionStyle.setText(
            QCoreApplication.translate("MainWindow", "Style", None)
        )
        self.action_8.setText(QCoreApplication.translate("MainWindow", "-4", None))
        self.action_9.setText(QCoreApplication.translate("MainWindow", "-3", None))
        self.action_10.setText(QCoreApplication.translate("MainWindow", "-2", None))
        self.action_11.setText(QCoreApplication.translate("MainWindow", "-1", None))
        self.action0_2.setText(QCoreApplication.translate("MainWindow", "0", None))
        self.action1_2.setText(QCoreApplication.translate("MainWindow", "1", None))
        self.action2_2.setText(QCoreApplication.translate("MainWindow", "2", None))
        self.action3_2.setText(QCoreApplication.translate("MainWindow", "3", None))
        self.action4_2.setText(QCoreApplication.translate("MainWindow", "4", None))
        self.action_12.setText(QCoreApplication.translate("MainWindow", "-3", None))
        self.action_13.setText(QCoreApplication.translate("MainWindow", "-2", None))
        self.action_14.setText(QCoreApplication.translate("MainWindow", "-1", None))
        self.action0_3.setText(QCoreApplication.translate("MainWindow", "0", None))
        self.action1_3.setText(QCoreApplication.translate("MainWindow", "1", None))
        self.action2_3.setText(QCoreApplication.translate("MainWindow", "2", None))
        self.action3_3.setText(QCoreApplication.translate("MainWindow", "3", None))
        self.main_toolBox.setItemText(
            self.main_toolBox.indexOf(self.batch_analysis_tab),
            QCoreApplication.translate("MainWindow", "Batch Analysis", None),
        )
        self.main_toolBox.setItemText(
            self.main_toolBox.indexOf(self.plotting_tab),
            QCoreApplication.translate("MainWindow", "Plotting", None),
        )
        self.ml_label.setText(
            QCoreApplication.translate("MainWindow", "Medium/Long:", None)
        )
        self.crystal_savol_label.setText(
            QCoreApplication.translate("MainWindow", "Surface Area:Volume:", None)
        )
        self.spacegroup_label.setText(
            QCoreApplication.translate("MainWindow", "Space group:", None)
        )
        self.crystal_ar_label.setText(
            QCoreApplication.translate("MainWindow", "Aspect Ratio", None)
        )
        self.show_info_button.setText(
            QCoreApplication.translate("MainWindow", "Show Information", None)
        )
        self.sm_label.setText(
            QCoreApplication.translate("MainWindow", "Short/Medium:", None)
        )
        self.crystal_vol_label.setText(
            QCoreApplication.translate(
                "MainWindow", "Crystal Volume (nm<sup>2</sup>):", None
            )
        )
        self.fname_label.setText(
            QCoreApplication.translate("MainWindow", "Filename:", None)
        )
        self.crystal_sa_label.setText(
            QCoreApplication.translate(
                "MainWindow", "Crystal Surface Area (nm<sup>2</sup>):", None
            )
        )
        self.shape_label.setText(
            QCoreApplication.translate("MainWindow", "General Shape:", None)
        )
        self.main_toolBox.setItemText(
            self.main_toolBox.indexOf(self.crystal_info_tab),
            QCoreApplication.translate("MainWindow", "Crystal Information", None),
        )
        self.EVariable_title_label_2.setText(
            QCoreApplication.translate("MainWindow", "Variables:", None)
        )
        self.select_summary_slider_button.setText(
            QCoreApplication.translate("MainWindow", "Select Summary File", None)
        )
        self.main_toolBox.setItemText(
            self.main_toolBox.indexOf(self.variables_tab),
            QCoreApplication.translate("MainWindow", "Variables", None),
        )
        self.saveFrame_button.setText(
            QCoreApplication.translate("MainWindow", "Save Frame", None)
        )
        self.display_options_label.setText(
            QCoreApplication.translate("MainWindow", "Display Options", None)
        )
        self.zoom_label.setText(QCoreApplication.translate("MainWindow", "Zoom", None))
        self.pointsize_label.setText(
            QCoreApplication.translate("MainWindow", "Point Size", None)
        )
        self.brightness_label.setText(
            QCoreApplication.translate("MainWindow", "Brightness", None)
        )
        self.resolution_label.setText(
            QCoreApplication.translate("MainWindow", "Resolution", None)
        )
        self.point_type_label.setText(
            QCoreApplication.translate("MainWindow", "Point Type", None)
        )
        self.colour_mode_label.setText(
            QCoreApplication.translate("MainWindow", "Colour Mode", None)
        )
        self.colour_label.setText(
            QCoreApplication.translate("MainWindow", "Colour", None)
        )
        self.colour_label_2.setText(
            QCoreApplication.translate("MainWindow", "Background Colour", None)
        )
        self.main_toolBox.setItemText(
            self.main_toolBox.indexOf(self.vis_options_tab),
            QCoreApplication.translate("MainWindow", "Visualiser Options", None),
        )
        self.play_button.setText(QCoreApplication.translate("MainWindow", "Play", None))
        self.pause_button.setText(
            QCoreApplication.translate("MainWindow", "Pause", None)
        )
        self.current_frame_label.setText(
            QCoreApplication.translate("MainWindow", "Current Frame", None)
        )
        self.start_simvis_button.setText(
            QCoreApplication.translate("MainWindow", "Start", None)
        )
        self.end_simvis_button.setText(
            QCoreApplication.translate("MainWindow", "End", None)
        )
        self.main_toolBox.setItemText(
            self.main_toolBox.indexOf(self.video_options_tab),
            QCoreApplication.translate("MainWindow", "Video Options", None),
        )
        self.console_label.setText(
            QCoreApplication.translate("MainWindow", "Console", None)
        )

    # retranslateUi
