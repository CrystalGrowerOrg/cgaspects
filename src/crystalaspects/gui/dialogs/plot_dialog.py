import logging
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                               QFileDialog, QGridLayout, QHBoxLayout,
                               QInputDialog, QLabel, QMessageBox, QPushButton,
                               QSizePolicy, QSpinBox, QVBoxLayout, QWidget)

matplotlib.use("QT5Agg")

logger = logging.getLogger("CA:PlotDialog")


class PlottingDialog(QDialog):
    def __init__(self, csv, signals=None):
        super().__init__()
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 600)

        # Set the dialog to be non-modal
        self.setWindowModality(QtCore.Qt.NonModal)

        self.create_widgets()
        self.create_layout()
        self.annot = None
        self.trendline = None
        self.trendline_text = None
        self.signals = signals

        self.selected_plot = None
        self.plot_objects = {}

        self.plotting_info(csv)
        self.plot_list_combo_box.clear()
        self.plot_list_combo_box.addItems(self.plots_list)

    def plotting_info(self, csv):
        self.csv = csv
        df = pd.read_csv(self.csv)
        logger.debug("Dataframe read:\n%s", df)
        plotting = ""
        for col in df.columns:
            if col.startswith("Supersaturation"):
                plotting = "Growth Rates"
        self.growth_rate = None
        # Identify interaction columns
        interaction_columns = [
            col
            for col in df.columns
            if col.startswith(
                ("interaction", "tile", "temperature", "starting_delmu", "excess")
            )
        ]
        logger.debug("Interaction energy columns: %s", interaction_columns)

        # List to store the results
        plot_types = []

        # Check each column heading
        for column in df.columns:
            if column.startswith("OBA") and "OBA" not in plot_types:
                plot_types.append("OBA")
            elif column.startswith("PCA") and "PCA" not in plot_types:
                plot_types.append("PCA")
            elif (
                column == "Surface Area: Volume Ratio"
                and "Surface Area: Volume Ratio" not in plot_types
            ):
                plot_types.append("Surface Area: Volume Ratio")
            elif column.startswith("M/L") and "CDA" not in plot_types:
                plot_types.append("CDA")
            elif column.startswith("AspectRatio") and "CDA Extended" not in plot_types:
                plot_types.append("CDA Extended")

        # Get equations
        for column in df.columns:
            if column.startswith("CDA_Equation"):
                equations = set(df["CDA_Equation"])
                for equation in equations:
                    plot_types.append(f"OBA vs CDA Equation {equation}")
                    plot_types.append(f"PCA vs CDA Equation {equation}")

        self.plots_list = []
        for plot_type in plot_types:
            # Add the basic plot
            self.plots_list.append(plot_type)

            # Add plots with interaction
            for interaction_col in interaction_columns:
                self.plots_list.append(f"{plot_type} vs {interaction_col}")

        if plotting == "Growth Rates":
            self.plotting = "Scatter+Line"
            self.growth_rate = True
            directions = []
            for col in df.columns:
                if col.startswith(" "):
                    directions.append(col)
            self.directions = directions
            self.plots_list = ["Growth Rates"]

    def create_widgets(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.figure.canvas.mpl_connect('button_press_event', self.on_click)


        self.label_pointsize = QLabel("Point Size:")
        self.label_plotstyle = QLabel("Plot Style:")
        self.label_plottype = QLabel("Plot Type:")
        self.spin_point_size = QSpinBox()
        self.spin_point_size.setRange(1, 100)

        self.button_add_trendline = QPushButton("Add Trendline")
        self.button_save = QPushButton("Save")

        # Initialize the variables
        self.point_size = 12
        self.spin_point_size.setValue(self.point_size)
        self.colorbar = False
        self.scatter = None


        # Initialize checkboxes
        self.checkbox_grid = QCheckBox("Show Grid")
        self.checkbox_trendline = QCheckBox("Add Trendline")

        self.button_save.clicked.connect(self.save)
        self.canvas.mpl_connect(
            "motion_notify_event", lambda event: self.on_hover(event)
        )

        # Create the plot type combo box
        self.plot_type_combo_box = QComboBox()
        self.plot_type_combo_box.addItems(["Scatter", "Line", "Scatter+Line"])

        self.plot_list_combo_box = QComboBox()
        self.plot_list_combo_box.setMaxVisibleItems(5)
        self.plot_list_combo_box.show()

        self.button_save.clicked.connect(self.save)
        self.checkbox_grid.stateChanged.connect(self.toggle_grid)
        self.button_add_trendline.clicked.connect(self.toggle_trendline)
        self.spin_point_size.valueChanged.connect(self.set_point_size)
        self.plot_type_combo_box.currentIndexChanged.connect(self.change_plot_type)
        self.plot_list_combo_box.currentIndexChanged.connect(self.change_plot_from_list)

        # Initialize the plot type
        self.plot_type = "scatter"

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.checkbox_grid)
        hbox1.addWidget(self.label_pointsize)
        hbox1.addWidget(self.spin_point_size)
        hbox1.addWidget(self.label_plotstyle)
        hbox1.addWidget(self.plot_type_combo_box)
        hbox1.addWidget(self.label_plottype)
        hbox1.addWidget(self.plot_list_combo_box)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.button_save)
        hbox2.addWidget(self.button_add_trendline)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)

        # Set window properties
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 600)
        self.setLayout(layout)

    def set_point_size(self, value):
        self.point_size = self.spin_point_size.value()
        if self.scatter is not None:
            self.scatter.set_sizes([self.point_size] * len(self.scatter.get_offsets()))
        self.canvas.draw()
    
    def toggle_grid(self, state):
        self.plot()

    def change_plot_type(self):
        plot_type = self.plot_type

        if plot_type == "Scatter":
            self.plot_type = "scatter"
            self.plot()
        if plot_type == "Scatter+Line":
            self.plot_type = "scatter_line"
            self.plot()
        if plot_type == "Line":
            self.plot_type = "line"
            self.plot()        

    def change_plot_from_list(self):
        self.selected_plot = self.plot_list_combo_box.currentText()
        self.plot()

    def plot(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.canvas.draw()
        logger.info("Plotting called for: %s", self.selected_plot)
        # Reading the dataframe
        df = pd.read_csv(self.csv)
        self.df = df
        self.plot_objects = {}
        # Finding interactions in data frame if there are any
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction")
            or col.startswith("tile")
            or col.startswith("starting_delmu")
            or col.startswith("temperature_celcius")
            or col.startswith("excess")
        ]

        equation_plot = False
        for col in df.columns:
            if col.startswith("CDA_Equation"):
                equations = set(df["CDA_Equation"])
                equation_plot = True

        for col in df.columns:
            if col.startswith("interaction") or col.startswith("tile"):
                cbar_legend = r"$\Delta G_{Cryst}$ (kcal/mol)"
            if col.startswith("starting_delmu"):
                cbar_legend = r"$\Delta G_{Cryst}$ (kcal/mol)"
                plot_title = "Aspect Ratio vs Supersaturation"
            if col.startswith("temperature_celcius"):
                cbar_legend = "Temperature (℃)"
                plot_title = "Aspect Ratio vs Temperature"
            if col.startswith("excess"):
                cbar_legend = r"$\Delta G_{Cryst}$ (kcal/mol)"
                plot_title = "Aspect Ratio vs Excess Supersaturation"

        if self.selected_plot == "OBA":
            x_data = df["OBA S:M"]
            y_data = df["OBA M:L"]

            logger.info(
                "Plotting x[ OBA S:M %s], y[ OBA M:L %s]", x_data.shape, y_data.shape
            )
            # Plot the data
            self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
            # When creating a scatter plot without colour data
            self.plot_objects[f""] = (None, self.scatter, None, None)
            self.ax.axhline(y=0.66, color="black", linestyle="--")
            self.ax.axvline(x=0.66, color="black", linestyle="--")
            self.ax.set_xlabel("S:M")
            self.ax.set_ylabel("M:L")
            self.ax.set_xlim(0, 1.0)
            self.ax.set_ylim(0, 1.0)
            self.ax.set_title("OBA Zingg Diagram")

        if self.selected_plot == "PCA":
            x_data = df["PCA S:M"]
            y_data = df["PCA M:L"]

            logger.info(
                "Plotting x[ PCA S:M %s], y[ PCA M:L %s]", x_data.shape, y_data.shape
            )
            # Plot the data
            self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
            # When creating a scatter plot without colour data
            self.plot_objects[f""] = (None, self.scatter, None, None)
            self.ax.axhline(y=0.66, color="black", linestyle="--")
            self.ax.axvline(x=0.66, color="black", linestyle="--")
            self.ax.set_xlabel("S:M")
            self.ax.set_ylabel("M:L")
            self.ax.set_xlim(0, 1.0)
            self.ax.set_ylim(0, 1.0)
            self.ax.set_title("PCA Zingg Diagram")

        if self.selected_plot == "Surface Area: Volume Ratio":
            x_data = df["Surface Area (SA)"]
            y_data = df["Volume (Vol)"]

            logger.info(
                "Plotting x[ Surface Area (SA) %s], y[ Volume (Vol) %s]",
                x_data.shape,
                y_data.shape,
            )
            # Plot the data
            self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
            # When creating a scatter plot without colour data
            self.plot_objects[f""] = (None, self.scatter, None, None)
            self.ax.set_xlabel("Surface Area (nm2)")
            self.ax.set_ylabel("Volume (nm3)")
            self.ax.set_title("Surface Area: Volume")

        if self.selected_plot == "CDA":
            x_data = df["S/M"]
            y_data = df["M/L"]

            logger.info("Plotting x[ S/M %s], y[ M/L %s]", x_data.shape, y_data.shape)
            # Plot the data
            self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
            # When creating a scatter plot without colour data
            self.plot_objects[f""] = (None, self.scatter, None, None)
            self.ax.set_xlabel("CDA S/M")
            self.ax.set_ylabel("CDA M/L")
            self.ax.set_xlim(0, 1.0)
            self.ax.set_ylim(0, 1.0)
            self.ax.set_title("CDA Zingg Diagram")

        if self.selected_plot == "CDA Extended":
            x_data = None
            y_data = None
            x_column_name = None
            y_column_name = None
            # Counter for 'AspectRatio' columns
            aspect_ratio_count = 0
            for column in df.columns:
                if column.startswith("AspectRatio"):
                    aspect_ratio_count += 1
                    if aspect_ratio_count == 1:
                        x_name = column
                        x_data = df[column]
                        x_column_name = column
                    elif aspect_ratio_count == 2:
                        y_name = column
                        y_data = df[column]
                        y_column_name = column
                        break

            logger.info(
                "Plotting x[ %s %s], y[ %s %s]",
                x_name,
                x_data.shape,
                y_name,
                y_data.shape,
            )
            # Plot the data
            self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
            # When creating a scatter plot without colour data
            self.plot_objects[f""] = (None, self.scatter, None, None)
            self.ax.set_xlabel(x_column_name)
            self.ax.set_ylabel(y_column_name)
            self.ax.set_title("Extended CDA")
            self.canvas.draw()

        # Plotting each interaction separately
        for interaction in interactions:
            if self.selected_plot.startswith("OBA vs " + interaction):
                x_data = df["OBA S:M"]
                y_data = df["OBA M:L"]
                logger.info(
                    "Plotting x[ OBA S:M %s], y[ OBA M:L %s] c[ Interaction %s ]",
                    x_data.shape,
                    y_data.shape,
                    interaction,
                )
                colour_data = df[interaction]
                # Check if colour_data is numerical or needs conversion
                if colour_data.dtype.kind not in "biufc":  # Check if not a number
                    colour_data = pd.factorize(colour_data)[0]
                # Plot the data
                self.scatter = self.ax.scatter(
                    x_data, y_data, c=colour_data, cmap="plasma", s=self.point_size
                )
                # When creating a scatter plot with colour data
                self.plot_objects[f"Plot {interaction}"] = (
                    None,
                    self.scatter,
                    colour_data,
                    interaction,
                )
                self.ax.axhline(y=0.66, color="black", linestyle="--")
                self.ax.axvline(x=0.66, color="black", linestyle="--")
                self.ax.set_xlabel("S:M")
                self.ax.set_ylabel("M:L")
                self.ax.set_xlim(0.0, 1.0)
                self.ax.set_ylim(0.0, 1.0)
                self.ax.set_title(f"OBA {interaction}")
                # Add colorbar and other customizations as needed
                cbar = self.figure.colorbar(self.scatter)
                cbar.set_label(cbar_legend)
                cbar.ax.set_zorder(-1)
                self.canvas.draw()

            if self.selected_plot.startswith("PCA vs " + interaction):
                x_data = df["PCA S:M"]
                y_data = df["PCA M:L"]
                colour_data = df[interaction]
                logger.info(
                    "Plotting x[ PCA S:M %s], y[ PCA M:L %s] c[ Interaction %s ]",
                    x_data.shape,
                    y_data.shape,
                    interaction,
                )
                # Check if colour_data is numerical or needs conversion
                if colour_data.dtype.kind not in "biufc":  # Check if not a number
                    colour_data = pd.factorize(colour_data)[0]
                # Plot the data
                self.scatter = self.ax.scatter(
                    x_data, y_data, c=colour_data, cmap="plasma", s=self.point_size
                )
                # When creating a scatter plot with colour data
                self.plot_objects[f"Plot {interaction}"] = (
                    None,
                    self.scatter,
                    colour_data,
                    interaction,
                )
                self.ax.axhline(y=0.66, color="black", linestyle="--")
                self.ax.axvline(x=0.66, color="black", linestyle="--")
                self.ax.set_xlabel("S:M")
                self.ax.set_ylabel("M:L")
                self.ax.set_xlim(0.0, 1.0)
                self.ax.set_ylim(0.0, 1.0)
                self.ax.set_title(f"PCA {interaction}")
                # Add colorbar and other customizations as needed
                cbar = self.figure.colorbar(self.scatter)
                cbar.set_label(cbar_legend)
                cbar.ax.set_zorder(-1)
                self.canvas.draw()

            if self.selected_plot.startswith(
                "Surface Area: Volume Ratio vs " + interaction
            ):
                x_data = df["Surface Area (SA)"]
                y_data = df["Volume (Vol)"]
                colour_data = df[interaction]
                logger.info(
                    "Plotting x[ Surface Area (SA) %s], y[ Volume (Vol) %s] c[ Interaction %s ]",
                    x_data.shape,
                    y_data.shape,
                    interaction,
                )
                # Check if colour_data is numerical or needs conversion
                if colour_data.dtype.kind not in "biufc":  # Check if not a number
                    colour_data = pd.factorize(colour_data)[0]
                # Plot the data
                self.scatter = self.ax.scatter(
                    x_data, y_data, c=colour_data, cmap="plasma", s=self.point_size
                )
                # When creating a scatter plot with colour data
                self.plot_objects[f"Plot {interaction}"] = (
                    None,
                    self.scatter,
                    colour_data,
                    interaction,
                )
                self.ax.set_xlabel("Surface Area (nm2)")
                self.ax.set_ylabel("Volume (nm3)")
                self.ax.set_title(f"Surface Area: Volume {interaction}")
                # Add colorbar and other customizations as needed
                cbar = self.figure.colorbar(self.scatter)
                cbar.set_label(cbar_legend)
                cbar.ax.set_zorder(-1)
                self.canvas.draw()

            if self.selected_plot.startswith("CDA vs " + interaction):
                x_data = df["S/M"]
                y_data = df["M/L"]
                colour_data = df[interaction]
                logger.info(
                    "Plotting x[ CDA S/M %s], y[ CDA M/L %s] c[ Interaction %s ]",
                    x_data.shape,
                    y_data.shape,
                    interaction,
                )
                # Check if colour_data is numerical or needs conversion
                if colour_data.dtype.kind not in "biufc":  # Check if not a number
                    colour_data = pd.factorize(colour_data)[0]
                # Plot the data
                self.scatter = self.ax.scatter(
                    x_data, y_data, c=colour_data, cmap="plasma", s=self.point_size
                )
                # When creating a scatter plot with colour data
                self.plot_objects[f"Plot {interaction}"] = (
                    None,
                    self.scatter,
                    colour_data,
                    interaction,
                )
                self.ax.axhline(y=0.66, color="black", linestyle="--")
                self.ax.axvline(x=0.66, color="black", linestyle="--")
                self.ax.set_xlabel("CDA S/M")
                self.ax.set_ylabel("CDA M/L")
                self.ax.set_xlim(0.0, 1.0)
                self.ax.set_ylim(0.0, 1.0)
                self.ax.set_title(f"CDA {interaction}")
                # Add colorbar and other customizations as needed
                cbar = self.figure.colorbar(self.scatter)
                cbar.set_label(cbar_legend)
                cbar.ax.set_zorder(-1)
                self.canvas.draw()

            if self.selected_plot.startswith("CDA Extended vs " + interaction):
                x_data = None
                y_data = None
                x_column_name = None
                y_column_name = None
                # Counter for 'AspectRatio' columns
                aspect_ratio_count = 0
                for column in df.columns:
                    if column.startswith("AspectRatio"):
                        aspect_ratio_count += 1
                        if aspect_ratio_count == 1:
                            x_name = column
                            x_data = df[column]
                            x_column_name = column
                        elif aspect_ratio_count == 2:
                            y_name = column
                            y_data = df[column]
                            y_column_name = column
                            break

                logger.info(
                    "Plotting x[ %s %s], y[ %s %s] c[ Interaction %s]",
                    x_name,
                    x_data.shape,
                    y_name,
                    y_data.shape,
                    interaction,
                )
                colour_data = df[interaction]
                # Check if colour_data is numerical or needs conversion
                if colour_data.dtype.kind not in "biufc":  # Check if not a number
                    colour_data = pd.factorize(colour_data)[0]
                # Plot the data
                self.scatter = self.ax.scatter(
                    x_data, y_data, c=colour_data, cmap="plasma", s=self.point_size
                )
                # When creating a scatter plot with colour data
                self.plot_objects[f"Plot {interaction}"] = (
                    None,
                    self.scatter,
                    colour_data,
                    interaction,
                )
                self.ax.set_xlabel(x_column_name)
                self.ax.set_ylabel(y_column_name)
                self.ax.set_title(f"Extended CDA {interaction}")
                # Add colorbar and other customizations as needed
                cbar = self.figure.colorbar(self.scatter)
                cbar.set_label(cbar_legend)
                cbar.ax.set_zorder(-1)
                self.canvas.draw()

        if equation_plot:
            for equation in equations:
                if self.selected_plot.startswith(f"OBA vs CDA Equation {equation}"):
                    df = df[df["CDA_Equation"] == equation]
                    x_data = df["OBA S:M"]
                    y_data = df["OBA M:L"]
                    logger.info(
                        "Plotting x[ OBA S:M %s], y[ OBA M:L %s] c[ Interaction %s ]",
                        x_data.shape,
                        y_data.shape,
                        interaction,
                    )
                    # Plot the data
                    self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
                    # When creating a scatter plot without colour data
                    self.plot_objects[f""] = (None, self.scatter, None, None)
                    self.ax.axhline(y=0.66, color="black", linestyle="--")
                    self.ax.axvline(x=0.66, color="black", linestyle="--")
                    self.ax.set_xlabel("S:M")
                    self.ax.set_ylabel("M:L")
                    self.ax.set_xlim(0.0, 1.0)
                    self.ax.set_ylim(0.0, 1.0)
                    self.ax.set_title(f"OBA vs CDA Equation {equation}")
                    self.canvas.draw()

                if self.selected_plot.startswith(f"PCA vs CDA Equation {equation}"):
                    df = df[df["CDA_Equation"] == equation]
                    x_data = df["PCA S:M"]
                    y_data = df["PCA M:L"]
                    logger.info(
                        "Plotting x[ PCA S:M %s], y[ PCA M:L %s] c[ Interaction %s ]",
                        x_data.shape,
                        y_data.shape,
                        interaction,
                    )
                    # Plot the data
                    self.scatter = self.ax.scatter(x_data, y_data, s=self.point_size)
                    # When creating a scatter plot without colour data
                    self.plot_objects[f""] = (None, self.scatter, None, None)
                    self.ax.axhline(y=0.66, color="black", linestyle="--")
                    self.ax.axvline(x=0.66, color="black", linestyle="--")
                    self.ax.set_xlabel("S:M")
                    self.ax.set_ylabel("M:L")
                    self.ax.set_xlim(0.0, 1.0)
                    self.ax.set_ylim(0.0, 1.0)
                    self.ax.set_title(f"PCA vs CDA Equation {equation}")
                    self.canvas.draw()

        if self.growth_rate:
            x_data = df["Supersaturation"]
            # Store plot objects for reference (both line and scatter)
            self.plot_objects = {}

            # Define the on_legend_click function here
            def on_legend_click(event):
                legline = event.artist
                origline, origscatter, _, _ = self.plot_objects[legline.get_label()]
                vis = not origline.get_visible()
                origline.set_visible(vis)
                origscatter.set_visible(vis)
                legline.set_alpha(1.0 if vis else 0.2)
                self.canvas.draw()

            for i in self.directions:
                self.scatter = self.ax.scatter(x_data, df[i], s=6)
                (line,) = self.ax.plot(x_data, df[i], label=f" {i}")
                self.plot_objects[f" {i}"] = (line, self.scatter, None, None)
                self.ax.set_xlabel("Supersaturation (kcal/mol)")
                self.ax.set_ylabel("Growth Rate")
                self.ax.set_title("Growth Rates")

            # Create a legend
            legend = self.ax.legend()

            for legline in legend.get_lines():
                legline.set_picker(5)  # Enable clicking on the legend line
                legline.figure.canvas.mpl_connect("pick_event", on_legend_click)

            self.canvas.draw()

        if self.colorbar:
            cbar = self.figure.colorbar(self.scatter)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")

        if self.checkbox_grid.isChecked():
            self.ax.grid()

        self.annot = self.ax.annotate(
            "",
            xy=(-1, -1),
            xytext=(-20, 20),
            textcoords="offset points",
            ha="center",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
            zorder=20,
        )
        self.annot.set_visible(False)

        self.canvas.draw()

    def update_annot(self, scatter, colour_data, column_name, ind):
        pos = scatter.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        x, y = pos

        # Check if colour_data is available
        if colour_data is not None:
            color_val = colour_data[ind["ind"][0]]
            text = (
                f"Sim Number: {ind['ind'][0] + 1}\n"
                f" x: {x:.2f}'\n"
                f" y: {y:.2f}\n"
                f" {column_name}: {color_val:.2f}"
            )
        else:
            text = f"Sim Number: {ind['ind'][0] + 1}\n" f" x: {x:.2f}\n" f" y: {y:.2f}"

        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)

    def on_hover(self, event):
        if self.annot:
            vis = self.annot.get_visible()
        try:
            if event.inaxes == self.ax:
                for _, plot_data in self.plot_objects.items():
                    # Unpack the plot data
                    line, scatter, colour_data, column_name = plot_data

                    # Check if scatter plot exists and handle hover event
                    if scatter is not None:
                        cont, ind = scatter.contains(event)
                        if cont:
                            self.update_annot(scatter, colour_data, column_name, ind)
                            self.annot.set_visible(True)
                            self.figure.canvas.draw_idle()
                            break

                # Hide annotation if no scatter plot contains the event
                if not cont and vis:
                    self.annot.set_visible(False)
                    self.figure.canvas.draw_idle()
        except NameError:
            pass

    def on_click(self, event):
        if event.inaxes == self.ax:
            for _, plot_data in self.plot_objects.items():
                # Unpack the plot data
                line, scatter, colour_data, column_name = plot_data

                # Check if scatter plot exists and handle click event
                if scatter is not None:
                    cont, ind = scatter.contains(event)
                    if cont:
                        self.handle_click(scatter, colour_data, column_name, ind)
                        break
    def handle_click(self, scatter, colour_data, column_name, ind):
        # index of the clicked point
        point_index = ind["ind"][0]

        # Extracting the x and y data of the clicked point
        x, y = scatter.get_offsets()[point_index]

        # Access the row in the self.df
        if self.df is not None and point_index < len(self.df):
            row_data = self.df.iloc[point_index]
            if self.signals:
                self.signals.sim_id.emit(int(row_data["Simulation Number"] - 1))
            logger.info(f"Clicked on row {point_index}: {row_data}")
        else:
            logger.debug(f"Clicked on point {point_index} with coordinates (x={x}, y={y})")

    def toggle_trendline(self):
        if not self.trendline:
            if self.scatter is None:
                self.statusBar().showMessage("Error: No scatter plot to add trendline to.")
                return

            x = self.scatter.get_offsets()[:, 0]
            y = self.scatter.get_offsets()[:, 1]

            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            self.trendline, = self.ax.plot(x, p(x), "r--")  # Store the trendline object

            equation_text = f"y = {z[0]:.2f}x + {z[1]:.2f}"
            self.trendline_text = self.ax.text(  # Store the text object
                0.05, 0.95, equation_text, transform=self.ax.transAxes, fontsize=12, verticalalignment="top")

            self.canvas.draw()
            self.button_add_trendline.setText("Remove Trendline")
        else:
            # Remove the trendline and its text from the plot
            if self.trendline:
                self.trendline.remove()
                self.trendline = None

            if hasattr(self, 'trendline_text') and self.trendline_text:
                self.trendline_text.remove()
                self.trendline_text = None

            self.canvas.draw()
            self.button_add_trendline.setText("Add Trendline")

    def save(self):
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("png")
        file_dialog.setNameFilters(["PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*)"])
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog.setDirectory("~/")
        file_dialog.setWindowTitle("Save Plot")

        if file_dialog.exec() == QDialog.Accepted:
            file_name = file_dialog.selectedFiles()[0]

            if file_name:
                transparent = (
                    QMessageBox.question(
                        self,
                        "Transparent Background",
                        "Do you want a transparent background?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No,
                    )
                    == QMessageBox.Yes
                )

                try:
                    if transparent:
                        self.figure.savefig(file_name, transparent=True, dpi=600)
                    else:
                        self.figure.savefig(file_name, dpi=600)
                except Exception as e:
                    logger.error("Error saving file: %s", e)
