import logging
from itertools import permutations
import matplotlib
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6 import QtCore
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


from crystalaspects.gui.dialogs.plotsavedialog import PlotSaveDialog
from crystalaspects.gui.widgets.plot_axes_widget import (
    PlotAxesComboBoxes,
    CheckableComboBox,
)

matplotlib.use("QTAgg")

logger = logging.getLogger("CA:PlotDialog")


class NavigationToolbar(NavigationToolbar2QT):
    toolitems = (
        ("Home", "Reset original view", "home", "home"),
        ("Back", "Back to previous view", "back", "back"),
        ("Forward", "Forward to next view", "forward", "forward"),
        (None, None, None, None),
        (
            "Pan",
            "Left button pans, Right button zooms\n"
            "x/y fixes axis, CTRL fixes aspect",
            "move",
            "pan",
        ),
        ("Zoom", "Zoom to rectangle\nx/y fixes axis", "zoom_to_rect", "zoom"),
    )


class PlottingDialog(QDialog):
    def __init__(self, csv, signals=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 600)

        # Set the dialog to be non-modal
        self.setWindowModality(QtCore.Qt.NonModal)

        self.annot = None
        self.trendline = None
        self.trendline_text = None
        self.signals = signals

        self.selected_plot = None
        self.plot_objects = {}
        self.plot_types = []
        self.directions = []
        self.permutations = ["None"]
        self.interaction_columns = ["None"]

        self.plotting_info(csv)
        self.create_widgets()
        self.create_layout()

    def plotting_info(self, csv):
        self.csv = csv
        self.df = pd.read_csv(self.csv)
        logger.debug("Dataframe read:\n%s", self.df)
        plotting = None
        for col in self.df.columns:
            if col.startswith("Supersaturation"):
                plotting = "Growth Rates"
        self.growth_rate = None

        self.interaction_columns = [
            col
            for col in self.df.columns
            if col.startswith(
                ("interaction", "tile", "temperature", "starting_delmu", "excess")
            )
        ]
        logger.debug("Interaction energy columns: %s", self.interaction_columns)

        # List to store the results
        self.plot_types = []
        self.directions = []
        # Check each column heading
        for column in self.df.columns:
            if column in ["PC1", "PC2", "PC3"] and "Zingg" not in self.plot_types:
                self.plot_types.append("Zingg")
            if column == "SA:Vol Ratio" and "SA:Vol Ratio" not in self.plot_types:
                self.plot_types.append("SA:Vol Ratio")
            if column.startswith("Ratio"):
                column = column.replace("Ratio_", "")
                directions = column.split(":")
                for direction in directions:
                    if direction not in self.directions:
                        self.directions.append(direction)
                if "CDA" not in self.plot_types:
                    self.plot_types.append("CDA")

        self.permutations = list(permutations(self.directions))

        if plotting == "Growth Rates":
            self.growth_rate = True
            self.directions = []
            for col in self.df.columns:
                if col.startswith(" "):
                    self.directions.append(col)
            self.plot_types = ["Growth Rates"]

        logger.info("Default plot types found: %s", self.plot_types)

    def create_widgets(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)
        self.label_pointsize = QLabel("Point Size: ")

        # Main plotting classes
        self.plot_types_label = QLabel("Plot: ")
        self.plot_types_combobox = QComboBox(self)
        self.plot_types_combobox.addItems(self.plot_types)

        # self.plot_permutations_label = None
        # self.plot_permutations_combobox = None
        # self.label_variables = None
        # self.variables_combobox = None

        # if "CDA" in self.plot_types:
        self.plot_permutations_label = QLabel("Permutations: ")
        self.plot_permutations_label.setToolTip(
            "Crystallographic face-to-face distance ratios in ascending order"
        )
        self.plot_permutations_combobox = QComboBox(self)
        self.plot_permutations_combobox.addItems(self.permutations)

        # if len(self.interaction_columns) > 1:
        self.variables_label = QLabel("Colour with variable: ")
        self.variables_combobox = QComboBox(self)
        self.variables_combobox.addItems(self.interaction_columns)

        self.default_plots_checkbox = QCheckBox(self)
        self.custom_plots_checkbox = QCheckBox(self)

        self.custom_plot_widget = PlotAxesComboBoxes()
        self.custom_plot_widget.x_axis_combobox.addItems(self.df.columns)
        self.custom_plot_widget.y_axis_combobox.addItems(self.df.columns)
        self.custom_plot_widget.color_combobox.addItems(self.df.columns)

        self.spin_point_size = QSpinBox()
        self.spin_point_size.setRange(1, 100)

        self.button_add_trendline = QPushButton("Add Trendline")
        self.button_save = QPushButton("Save", parent=self)

        # Initialize the variables
        self.point_size = 12
        self.spin_point_size.setValue(self.point_size)
        self.colorbar = False
        self.scatter = None

        # Initialize checkboxes
        self.checkbox_grid = QCheckBox("Show Grid")
        self.checkbox_trendline = QCheckBox("Add Trendline")

        self.canvas.mpl_connect(
            "motion_notify_event", lambda event: self.on_hover(event)
        )

        self.button_save.clicked.connect(self.save)
        self.checkbox_grid.stateChanged.connect(self.toggle_grid)
        self.button_add_trendline.clicked.connect(self.toggle_trendline)
        self.spin_point_size.valueChanged.connect(self.set_point_size)
        self.default_plots_checkbox.stateChanged.connect(self.change_mode)
        self.custom_plots_checkbox.stateChanged.connect(self.change_mode)
        self.plot_types_combobox.currentIndexChanged.connect(self.trigger_plot)
        if self.plot_permutations_combobox is not None:
            self.plot_permutations_combobox.currentIndexChanged.connect(
                self.trigger_plot
            )
        if self.variables_combobox is not None:
            self.variables_combobox.currentIndexChanged.connect(self.trigger_plot)
        self.custom_plot_widget.plot_button.clicked.connect(self.trigger_plot)

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.checkbox_grid)
        hbox1.addWidget(self.label_pointsize)
        hbox1.addWidget(self.spin_point_size)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.default_plots_checkbox)
        hbox2.addWidget(self.plot_types_label)
        hbox2.addWidget(self.plot_types_combobox)
        hbox2.addWidget(self.plot_permutations_label)
        hbox2.addWidget(self.plot_permutations_combobox)
        hbox2.addWidget(self.variables_label)
        hbox2.addWidget(self.variables_combobox)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.custom_plots_checkbox)
        hbox3.addWidget(self.custom_plot_widget)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.button_save)
        hbox4.addWidget(self.button_add_trendline)

        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addLayout(hbox3)
        layout.addLayout(hbox4)

        # Set window properties
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 650)
        self.setLayout(layout)

    def set_point_size(self, value):
        self.point_size = self.spin_point_size.value()
        if self.scatter is not None:
            self.scatter.set_sizes([self.point_size] * len(self.scatter.get_offsets()))
        self.canvas.draw()

    def toggle_grid(self, state):
        self.plot()

    def change_mode(self, state):
        if self.sender() == self.default_plots_checkbox and state == QtCore.Qt.Checked:
            self.custom_plots_checkbox.setChecked(False)
        elif self.sender() == self.custom_plots_checkbox and state == QtCore.Qt.Checked:
            self.default_plots_checkbox.setChecked(False)

    def trigger_plot(self):
        pass

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

        _sim_id = "N/A"
        if self.df is not None and ind["ind"][0] < len(self.df):
            row_data = self.df.iloc[ind["ind"][0]]
            try:
                _sim_id = int(row_data["Simulation Number"] - 1)
            except KeyError:
                _sim_id = "N/A"

        # Check if colour_data is available
        if colour_data is not None:
            color_val = colour_data[ind["ind"][0]]
            text = (
                f"Sim Number: {_sim_id}\n"
                f" x: {x:.2f}'\n"
                f" y: {y:.2f}\n"
                f" {column_name}: {color_val:.2f}"
            )
        else:
            text = f"Sim Number: {_sim_id}\n" f" x: {x:.2f}\n" f" y: {y:.2f}"

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
            try:
                _sim_id = int(row_data["Simulation Number"] - 1)
            except KeyError:
                _sim_id = None
            if self.signals:
                self.signals.sim_id.emit(_sim_id)
            logger.info(f"Clicked on row {point_index}: {row_data}")
        else:
            logger.debug(
                f"Clicked on point {point_index} with coordinates (x={x}, y={y})"
            )

    def toggle_trendline(self):
        if not self.trendline:
            if self.scatter is None:
                self.statusBar().showMessage(
                    "Error: No scatter plot to add trendline to."
                )
                return

            x = self.scatter.get_offsets()[:, 0]
            y = self.scatter.get_offsets()[:, 1]

            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            (self.trendline,) = self.ax.plot(x, p(x), "r--")

            equation_text = f"y = {z[0]:.2f}x + {z[1]:.2f}"
            self.trendline_text = self.ax.text(  # Store the text object
                0.05,
                0.95,
                equation_text,
                transform=self.ax.transAxes,
                fontsize=12,
                verticalalignment="top",
            )

            self.canvas.draw()
            self.button_add_trendline.setText("Remove Trendline")
        else:
            # Remove the trendline and its text from the plot
            if self.trendline:
                self.trendline.remove()
                self.trendline = None

            if hasattr(self, "trendline_text") and self.trendline_text:
                self.trendline_text.remove()
                self.trendline_text = None

            self.canvas.draw()
            self.button_add_trendline.setText("Add Trendline")

    def save(self):
        file_dialog = PlotSaveDialog(self.figure)
        if file_dialog.exec() == QDialog.Accepted:
            logger.debug("Closing PlotSaveDialog: accepted")
        else:
            logger.debug("Closing PlotSaveDialog: not accepted")
