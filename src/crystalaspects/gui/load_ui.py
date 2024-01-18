# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'window.ui'
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
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QSlider,
    QSpacerItem, QSpinBox, QStatusBar, QTabWidget,
    QToolButton, QVBoxLayout, QWidget)
from crystalaspects.gui.utils import qticons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1280, 790)
        icon = QIcon()
        icon.addFile(u":/app_icons/app_icons/CrystalAspects.icns", QSize(), QIcon.Normal, QIcon.Off)
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
        self.actionImport = QAction(MainWindow)
        self.actionImport.setObjectName(u"actionImport")
        self.actionResults_Directory = QAction(MainWindow)
        self.actionResults_Directory.setObjectName(u"actionResults_Directory")
        self.actionResults_Directory.setEnabled(False)
        self.actionImport_CSV_for_Plotting = QAction(MainWindow)
        self.actionImport_CSV_for_Plotting.setObjectName(u"actionImport_CSV_for_Plotting")
        self.actionPlotting_Dialog = QAction(MainWindow)
        self.actionPlotting_Dialog.setObjectName(u"actionPlotting_Dialog")
        self.actionPlotting_Dialog.setEnabled(False)
        self.actionInput_Directory = QAction(MainWindow)
        self.actionInput_Directory.setObjectName(u"actionInput_Directory")
        self.actionInput_Directory.setEnabled(False)
        self.actionImport_Summary_File = QAction(MainWindow)
        self.actionImport_Summary_File.setObjectName(u"actionImport_Summary_File")
        self.actionImport_Summary_File.setEnabled(False)
        self.actionRender = QAction(MainWindow)
        self.actionRender.setObjectName(u"actionRender")
        self.actionRender.setEnabled(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.vis_scrollArea = QScrollArea(self.centralwidget)
        self.vis_scrollArea.setObjectName(u"vis_scrollArea")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.vis_scrollArea.sizePolicy().hasHeightForWidth())
        self.vis_scrollArea.setSizePolicy(sizePolicy)
        self.vis_scrollArea.setFrameShape(QFrame.NoFrame)
        self.vis_scrollArea.setFrameShadow(QFrame.Plain)
        self.vis_scrollArea.setLineWidth(0)
        self.vis_scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 901, 722))
        self.gridLayout_3 = QGridLayout(self.scrollAreaWidgetContents_4)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.main_frame = QFrame(self.scrollAreaWidgetContents_4)
        self.main_frame.setObjectName(u"main_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(5)
        sizePolicy1.setHeightForWidth(self.main_frame.sizePolicy().hasHeightForWidth())
        self.main_frame.setSizePolicy(sizePolicy1)
        self.gl_vLayout = QGridLayout(self.main_frame)
        self.gl_vLayout.setObjectName(u"gl_vLayout")
        self.gl_vLayout.setContentsMargins(0, 0, 0, 0)

        self.gridLayout_3.addWidget(self.main_frame, 0, 0, 1, 2)

        self.movie_controls_frame = QFrame(self.scrollAreaWidgetContents_4)
        self.movie_controls_frame.setObjectName(u"movie_controls_frame")
        self.movie_controls_frame.setStyleSheet(u"")
        self.movie_controls_frame.setFrameShape(QFrame.StyledPanel)
        self.movie_controls_frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.movie_controls_frame)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.playPauseButton = QToolButton(self.movie_controls_frame)
        self.playPauseButton.setObjectName(u"playPauseButton")
        self.playPauseButton.setMinimumSize(QSize(0, 0))
        icon1 = QIcon()
        icon1.addFile(u":/material_icons/material_icons/png/play-custom.png", QSize(), QIcon.Normal, QIcon.Off)
        self.playPauseButton.setIcon(icon1)

        self.horizontalLayout_5.addWidget(self.playPauseButton)

        self.frameCurrentLabel = QLabel(self.movie_controls_frame)
        self.frameCurrentLabel.setObjectName(u"frameCurrentLabel")

        self.horizontalLayout_5.addWidget(self.frameCurrentLabel)

        self.frame_spinBox = QSpinBox(self.movie_controls_frame)
        self.frame_spinBox.setObjectName(u"frame_spinBox")

        self.horizontalLayout_5.addWidget(self.frame_spinBox)

        self.frameZeroLabel = QLabel(self.movie_controls_frame)
        self.frameZeroLabel.setObjectName(u"frameZeroLabel")

        self.horizontalLayout_5.addWidget(self.frameZeroLabel)

        self.frame_slider = QSlider(self.movie_controls_frame)
        self.frame_slider.setObjectName(u"frame_slider")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_slider.sizePolicy().hasHeightForWidth())
        self.frame_slider.setSizePolicy(sizePolicy2)
        self.frame_slider.setMaximum(60)
        self.frame_slider.setPageStep(1000000)
        self.frame_slider.setOrientation(Qt.Horizontal)
        self.frame_slider.setTickPosition(QSlider.TicksAbove)
        self.frame_slider.setTickInterval(1)

        self.horizontalLayout_5.addWidget(self.frame_slider)

        self.frameMaxLabel = QLabel(self.movie_controls_frame)
        self.frameMaxLabel.setObjectName(u"frameMaxLabel")

        self.horizontalLayout_5.addWidget(self.frameMaxLabel)


        self.gridLayout_3.addWidget(self.movie_controls_frame, 1, 0, 1, 2)

        self.vis_scrollArea.setWidget(self.scrollAreaWidgetContents_4)

        self.gridLayout.addWidget(self.vis_scrollArea, 1, 5, 4, 3)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy3)
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setSizeConstraint(QLayout.SetFixedSize)
        self.import_pushButton = QPushButton(self.frame)
        self.import_pushButton.setObjectName(u"import_pushButton")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.import_pushButton.sizePolicy().hasHeightForWidth())
        self.import_pushButton.setSizePolicy(sizePolicy4)
        self.import_pushButton.setBaseSize(QSize(0, 0))
        icon2 = QIcon()
        icon2.addFile(u":/material_icons/material_icons/png/folder-arrow-down-custom.png", QSize(), QIcon.Normal, QIcon.Off)
        self.import_pushButton.setIcon(icon2)

        self.horizontalLayout_7.addWidget(self.import_pushButton)

        self.view_results_pushButton = QPushButton(self.frame)
        self.view_results_pushButton.setObjectName(u"view_results_pushButton")
        self.view_results_pushButton.setEnabled(False)
        sizePolicy4.setHeightForWidth(self.view_results_pushButton.sizePolicy().hasHeightForWidth())
        self.view_results_pushButton.setSizePolicy(sizePolicy4)
        self.view_results_pushButton.setMinimumSize(QSize(0, 0))
        self.view_results_pushButton.setBaseSize(QSize(0, 0))
        icon3 = QIcon()
        icon3.addFile(u":/material_icons/material_icons/png/folder-arrow-right-custom.png", QSize(), QIcon.Normal, QIcon.Off)
        self.view_results_pushButton.setIcon(icon3)

        self.horizontalLayout_7.addWidget(self.view_results_pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout_7)

        self.dataAnalysis_groupBox = QGroupBox(self.frame)
        self.dataAnalysis_groupBox.setObjectName(u"dataAnalysis_groupBox")
        self.dataAnalysis_groupBox.setFlat(False)
        self.verticalLayout_2 = QVBoxLayout(self.dataAnalysis_groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.location_label = QLabel(self.dataAnalysis_groupBox)
        self.location_label.setObjectName(u"location_label")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.location_label.sizePolicy().hasHeightForWidth())
        self.location_label.setSizePolicy(sizePolicy5)

        self.verticalLayout_2.addWidget(self.location_label)

        self.batch_lineEdit = QLineEdit(self.dataAnalysis_groupBox)
        self.batch_lineEdit.setObjectName(u"batch_lineEdit")
        sizePolicy2.setHeightForWidth(self.batch_lineEdit.sizePolicy().hasHeightForWidth())
        self.batch_lineEdit.setSizePolicy(sizePolicy2)
        self.batch_lineEdit.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.batch_lineEdit)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.aspect_ratio_pushButton = QPushButton(self.dataAnalysis_groupBox)
        self.aspect_ratio_pushButton.setObjectName(u"aspect_ratio_pushButton")
        self.aspect_ratio_pushButton.setEnabled(False)
        sizePolicy6 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.aspect_ratio_pushButton.sizePolicy().hasHeightForWidth())
        self.aspect_ratio_pushButton.setSizePolicy(sizePolicy6)

        self.horizontalLayout_2.addWidget(self.aspect_ratio_pushButton)

        self.growth_rate_pushButton = QPushButton(self.dataAnalysis_groupBox)
        self.growth_rate_pushButton.setObjectName(u"growth_rate_pushButton")
        self.growth_rate_pushButton.setEnabled(False)
        sizePolicy6.setHeightForWidth(self.growth_rate_pushButton.sizePolicy().hasHeightForWidth())
        self.growth_rate_pushButton.setSizePolicy(sizePolicy6)

        self.horizontalLayout_2.addWidget(self.growth_rate_pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.plot_label = QLabel(self.dataAnalysis_groupBox)
        self.plot_label.setObjectName(u"plot_label")

        self.verticalLayout_2.addWidget(self.plot_label)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.plot_lineEdit = QLineEdit(self.dataAnalysis_groupBox)
        self.plot_lineEdit.setObjectName(u"plot_lineEdit")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(5)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.plot_lineEdit.sizePolicy().hasHeightForWidth())
        self.plot_lineEdit.setSizePolicy(sizePolicy7)
        self.plot_lineEdit.setStyleSheet(u"")

        self.horizontalLayout_4.addWidget(self.plot_lineEdit)

        self.plot_pushButton = QPushButton(self.dataAnalysis_groupBox)
        self.plot_pushButton.setObjectName(u"plot_pushButton")
        self.plot_pushButton.setEnabled(False)
        icon4 = QIcon()
        icon4.addFile(u":/material_icons/material_icons/png/chart-scatter-plot-custom.png", QSize(), QIcon.Normal, QIcon.Off)
        self.plot_pushButton.setIcon(icon4)

        self.horizontalLayout_4.addWidget(self.plot_pushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.verticalLayout.addWidget(self.dataAnalysis_groupBox)

        self.variablesTabWidget = QTabWidget(self.frame)
        self.variablesTabWidget.setObjectName(u"variablesTabWidget")
        sizePolicy8 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.variablesTabWidget.sizePolicy().hasHeightForWidth())
        self.variablesTabWidget.setSizePolicy(sizePolicy8)
        self.variablesTab = QWidget()
        self.variablesTab.setObjectName(u"variablesTab")
        self.verticalLayout_4 = QVBoxLayout(self.variablesTab)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.simulationVariablesWidget = QWidget(self.variablesTab)
        self.simulationVariablesWidget.setObjectName(u"simulationVariablesWidget")
        self.verticalLayout_3 = QVBoxLayout(self.simulationVariablesWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.xyzWidget = QWidget(self.simulationVariablesWidget)
        self.xyzWidget.setObjectName(u"xyzWidget")
        sizePolicy5.setHeightForWidth(self.xyzWidget.sizePolicy().hasHeightForWidth())
        self.xyzWidget.setSizePolicy(sizePolicy5)
        self.horizontalLayout = QHBoxLayout(self.xyzWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.xyz_id_label = QLabel(self.xyzWidget)
        self.xyz_id_label.setObjectName(u"xyz_id_label")
        self.xyz_id_label.setEnabled(False)

        self.horizontalLayout.addWidget(self.xyz_id_label)

        self.xyz_spinBox = QSpinBox(self.xyzWidget)
        self.xyz_spinBox.setObjectName(u"xyz_spinBox")
        self.xyz_spinBox.setEnabled(False)
        self.xyz_spinBox.setMinimumSize(QSize(0, 0))
        self.xyz_spinBox.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.xyz_spinBox)


        self.verticalLayout_3.addWidget(self.xyzWidget)

        self.xyz_fname_comboBox = QComboBox(self.simulationVariablesWidget)
        self.xyz_fname_comboBox.setObjectName(u"xyz_fname_comboBox")
        self.xyz_fname_comboBox.setEnabled(False)
        sizePolicy9 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy9.setHorizontalStretch(1)
        sizePolicy9.setVerticalStretch(1)
        sizePolicy9.setHeightForWidth(self.xyz_fname_comboBox.sizePolicy().hasHeightForWidth())
        self.xyz_fname_comboBox.setSizePolicy(sizePolicy9)
        self.xyz_fname_comboBox.setMinimumSize(QSize(0, 0))
        self.xyz_fname_comboBox.setStyleSheet(u"")

        self.verticalLayout_3.addWidget(self.xyz_fname_comboBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)


        self.verticalLayout_4.addWidget(self.simulationVariablesWidget)

        self.variablesTabWidget.addTab(self.variablesTab, "")
        self.visualizationTab = QWidget()
        self.visualizationTab.setObjectName(u"visualizationTab")
        self.verticalLayout_6 = QVBoxLayout(self.visualizationTab)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.saveframe_pushButton = QPushButton(self.visualizationTab)
        self.saveframe_pushButton.setObjectName(u"saveframe_pushButton")
        self.saveframe_pushButton.setEnabled(False)
        icon5 = QIcon()
        icon5.addFile(u":/material_icons/material_icons/png/content-save-custom.png", QSize(), QIcon.Normal, QIcon.Off)
        self.saveframe_pushButton.setIcon(icon5)

        self.verticalLayout_6.addWidget(self.saveframe_pushButton)

        self.variablesTabWidget.addTab(self.visualizationTab, "")

        self.verticalLayout.addWidget(self.variablesTabWidget)

        self.crystalInfo_groupBox = QGroupBox(self.frame)
        self.crystalInfo_groupBox.setObjectName(u"crystalInfo_groupBox")
        self.verticalLayout_8 = QVBoxLayout(self.crystalInfo_groupBox)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")

        self.verticalLayout.addWidget(self.crystalInfo_groupBox)


        self.gridLayout.addWidget(self.frame, 1, 0, 4, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(8)
        font.setItalic(True)
        self.statusbar.setFont(font)
        self.statusbar.setCursor(QCursor(Qt.ArrowCursor))
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1280, 24))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuView = QMenu(self.menuBar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuView.menuAction())
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionImport_CSV_for_Plotting)
        self.menuFile.addAction(self.actionImport_Summary_File)
        self.menuFile.addAction(self.actionRender)
        self.menuView.addAction(self.actionInput_Directory)
        self.menuView.addAction(self.actionResults_Directory)
        self.menuView.addAction(self.actionPlotting_Dialog)

        self.retranslateUi(MainWindow)

        self.variablesTabWidget.setCurrentIndex(1)


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
        self.actionImport.setText(QCoreApplication.translate("MainWindow", u"Import", None))
#if QT_CONFIG(shortcut)
        self.actionImport.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+I", None))
#endif // QT_CONFIG(shortcut)
        self.actionResults_Directory.setText(QCoreApplication.translate("MainWindow", u"Results Directory", None))
#if QT_CONFIG(shortcut)
        self.actionResults_Directory.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+R", None))
#endif // QT_CONFIG(shortcut)
        self.actionImport_CSV_for_Plotting.setText(QCoreApplication.translate("MainWindow", u"Import CSV for Plotting", None))
#if QT_CONFIG(shortcut)
        self.actionImport_CSV_for_Plotting.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+I", None))
#endif // QT_CONFIG(shortcut)
        self.actionPlotting_Dialog.setText(QCoreApplication.translate("MainWindow", u"Plot", None))
#if QT_CONFIG(shortcut)
        self.actionPlotting_Dialog.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.actionInput_Directory.setText(QCoreApplication.translate("MainWindow", u"Input Directory", None))
#if QT_CONFIG(shortcut)
        self.actionInput_Directory.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.actionImport_Summary_File.setText(QCoreApplication.translate("MainWindow", u"Import Summary File", None))
        self.actionRender.setText(QCoreApplication.translate("MainWindow", u"Render", None))
        self.playPauseButton.setText(QCoreApplication.translate("MainWindow", u"   Play", None))
#if QT_CONFIG(shortcut)
        self.playPauseButton.setShortcut(QCoreApplication.translate("MainWindow", u"Space", None))
#endif // QT_CONFIG(shortcut)
        self.frameCurrentLabel.setText(QCoreApplication.translate("MainWindow", u"Frame", None))
        self.frameZeroLabel.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.frameMaxLabel.setText(QCoreApplication.translate("MainWindow", u"60", None))
        self.import_pushButton.setText(QCoreApplication.translate("MainWindow", u"   Import", None))
        self.view_results_pushButton.setText(QCoreApplication.translate("MainWindow", u"   View Results Directory", None))
        self.dataAnalysis_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Data Analysis", None))
        self.location_label.setText(QCoreApplication.translate("MainWindow", u"Location", None))
        self.aspect_ratio_pushButton.setText(QCoreApplication.translate("MainWindow", u"Aspect Ratios", None))
        self.growth_rate_pushButton.setText(QCoreApplication.translate("MainWindow", u"Growth Rates", None))
        self.plot_label.setText(QCoreApplication.translate("MainWindow", u"Plotting", None))
#if QT_CONFIG(tooltip)
        self.plot_pushButton.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.plot_pushButton.setText(QCoreApplication.translate("MainWindow", u"   Plot", None))
        self.xyz_id_label.setText(QCoreApplication.translate("MainWindow", u"XYZ ID: ", None))
        self.variablesTabWidget.setTabText(self.variablesTabWidget.indexOf(self.variablesTab), QCoreApplication.translate("MainWindow", u"Variables", None))
#if QT_CONFIG(statustip)
        self.saveframe_pushButton.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.saveframe_pushButton.setText(QCoreApplication.translate("MainWindow", u"Save Frame", None))
        self.variablesTabWidget.setTabText(self.variablesTabWidget.indexOf(self.visualizationTab), QCoreApplication.translate("MainWindow", u"Visualization", None))
        self.crystalInfo_groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Crystal Information", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
    # retranslateUi

