import logging
from itertools import permutations
from collections import namedtuple
import matplotlib
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6 import QtCore
from PySide6.QtWidgets import (
    QWidget,
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
    QGridLayout,
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
        self.plot_obj_tuple = namedtuple(
            "Plot", ["line", "scatter", "colour", "interaction"]
        )
        self.plot_objects = ()
        self.plot_types = []
        self.directions = []
        self.permutations = []
        self.permutation_labels = []
        self.interaction_columns = []
        self.plotting_mode = "default"

        self.grid = None
        self.point_size = None
        self.plot_type = None
        self.permutation = None
        self.variable = None
        self.custom_x = None
        self.custom_y = None
        self.custom_c = None

        self.x_data = None
        self.y_data = None
        self.c_data = None
        self.c_name = None
        self.c_label = None
        self.x_label = None
        self.y_label = None
        self.title = ""

        self.plotting_info(csv)
        self.create_widgets()
        self.create_layout()
        self.trigger_plot()

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
        self.interaction_columns.insert(0, "None")
        logger.debug("Interaction energy columns: %s", self.interaction_columns)

        # List to store the results
        self.plot_types = []
        self.directions = []
        # Check each column heading
        for column in self.df.columns:
            if column in ["PC1", "PC2", "PC3"] and "Zingg" not in self.plot_types:
                self.plot_types.append("Zingg")
            if column.startswith("Ratio"):
                column = column.replace("Ratio_", "")
                directions = column.split(":")
                for direction in directions:
                    if direction not in self.directions:
                        self.directions.append(direction)
                if "CDA" not in self.plot_types:
                    self.plot_types.append("CDA")
            if column == "SA:Vol Ratio" and "SA:Vol Ratio" not in self.plot_types:
                self.plot_types.append("SA:Vol Ratio")

        self.permutation_labels = ["None"]
        if len(self.directions) == 3:
            self.permutations = list(permutations(self.directions))
            for permutation in self.permutations:
                p_str = f"({permutation[0].strip()}) : ({permutation[1].strip()}) : ({permutation[2].strip()})"
                self.permutation_labels.append(p_str)

        if plotting == "Growth Rates":
            self.growth_rate = True
            self.directions = []
            for col in self.df.columns:
                if col.startswith(" "):
                    self.directions.append(col)
            self.plot_types = ["Growth Rates"]

        logger.info("Default plot types found: %s", self.plot_types)
        logger.info("Directions found: %s", self.directions)

        self.plot_types.append("Custom")

    def create_widgets(self):
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)
        self.label_pointsize = QLabel("Point Size: ")

        # Main plotting classes
        self.plot_types_label = QLabel("Plot Type: ")
        self.plot_types_label.setAlignment(QtCore.Qt.AlignRight)
        self.plot_types_combobox = QComboBox(self)
        self.plot_types_combobox.addItems(self.plot_types)

        # if "CDA" in self.plot_types:
        self.plot_permutations_label = QLabel("Permutations: ")
        self.plot_permutations_label.setAlignment(QtCore.Qt.AlignRight)
        self.plot_permutations_label.setToolTip(
            "Crystallographic face-to-face distance ratios in ascending order"
        )
        self.plot_permutations_combobox = QComboBox(self)
        self.plot_permutations_combobox.addItems(self.permutation_labels)

        # if len(self.interaction_columns) > 1:
        self.variables_label = QLabel("Variable: ")
        self.variables_label.setAlignment(QtCore.Qt.AlignRight)
        self.variables_combobox = QComboBox(self)
        self.variables_combobox.addItems(self.interaction_columns)

        self.custom_plot_widget = PlotAxesComboBoxes()
        self.custom_plot_widget.x_axis_combobox.addItems(self.df.columns)
        self.custom_plot_widget.y_axis_combobox.addItems(self.df.columns)
        self.custom_plot_widget.color_combobox.addItems(self.df.columns)

        self.spin_point_size = QSpinBox()
        self.spin_point_size.setRange(1, 100)

        self.button_save = QPushButton("Save")
        self.button_add_trendline = QPushButton("Add Trendline")

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
        self.checkbox_grid.stateChanged.connect(self.trigger_plot)
        self.button_add_trendline.clicked.connect(self.toggle_trendline)
        self.spin_point_size.valueChanged.connect(self.set_point_size)
        self.plot_types_combobox.currentIndexChanged.connect(self.trigger_plot)
        if self.plot_permutations_combobox is not None:
            self.plot_permutations_combobox.currentIndexChanged.connect(
                self.trigger_plot
            )
        if self.variables_combobox is not None:
            self.variables_combobox.currentIndexChanged.connect(self.trigger_plot)

        self.custom_plot_widget.x_axis_combobox.currentIndexChanged.connect(
            self.trigger_plot
        )
        self.custom_plot_widget.y_axis_combobox.itemCheckedStateChanged.connect(
            self.trigger_plot
        )
        self.custom_plot_widget.color_combobox.currentIndexChanged.connect(
            self.trigger_plot
        )

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.toolbar)
        hbox1.addWidget(self.checkbox_grid)
        hbox1.addWidget(self.label_pointsize)
        hbox1.addWidget(self.spin_point_size)
        hbox1.addWidget(self.button_add_trendline)
        hbox1.addWidget(self.button_save)

        grid1 = QGridLayout()
        grid1.addWidget(self.plot_types_label, 0, 0)
        grid1.addWidget(self.plot_types_combobox, 0, 1)
        grid1.addWidget(self.plot_permutations_label, 0, 2)
        grid1.addWidget(self.plot_permutations_combobox, 0, 3)
        grid1.addWidget(self.variables_label, 0, 4)
        grid1.addWidget(self.variables_combobox, 0, 5)
        grid1.addWidget(self.custom_plot_widget, 1, 0, 1, 6)
        # Set alignment to right for all labels and combo boxes
        for i in range(grid1.rowCount()):
            for j in range(grid1.columnCount()):
                widget = grid1.itemAtPosition(i, j).widget()
                if widget:
                    grid1.setAlignment(widget, QtCore.Qt.AlignRight)

        # Create a QWidget to hold grid1
        widget1 = QWidget()
        widget1.setLayout(hbox1)
        widget2 = QWidget()
        widget2.setLayout(grid1)

        # Add the widget containing grid1 to the main grid
        layout.addWidget(widget1)
        layout.addWidget(widget2)

        # # Set window properties
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 650)
        self.setLayout(layout)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def set_point_size(self, value):
        self.point_size = self.spin_point_size.value()
        if self.scatter is not None:
            self.scatter.set_sizes([self.point_size] * len(self.scatter.get_offsets()))
        self.canvas.draw()

    def change_mode(self, mode):
        if mode == "Custom":
            self.plot_permutations_label.setEnabled(False)
            self.plot_permutations_combobox.setEnabled(False)
            self.plot_permutations_combobox.setCurrentIndex(0)
            self.variables_label.setEnabled(False)
            self.variables_combobox.setEnabled(False)
            self.variables_combobox.setCurrentIndex(0)
            self.custom_plot_widget.setEnabled(True)

        if mode != "Custom":
            self.plot_permutations_label.setEnabled(True)
            self.plot_permutations_combobox.setEnabled(True)
            self.variables_label.setEnabled(True)
            self.variables_combobox.setEnabled(True)
            self.custom_plot_widget.setEnabled(False)

    def trigger_plot(self):
        self.grid = self.checkbox_grid.isChecked()
        self.point_size = self.spin_point_size.value()
        self.plot_type = self.plot_types_combobox.currentText()
        self.permutation = int(self.plot_permutations_combobox.currentIndex())
        self.variable = self.variables_combobox.currentText()
        (
            self.custom_x,
            self.custom_y,
            self.custom_c,
        ) = self.custom_plot_widget.get_selections()

        self.change_mode(mode=self.plot_type)
        self._set_data()
        self._mask_with_permutation()
        self._set_c()
        self._set_labels()
        self._set_c_label()
        self.plot()

    def _set_data(self):
        if self.plot_type == "Zingg":
            self.x_data = self.df["S:M"]
            self.y_data = self.df["M:L"]
        if self.plot_type == "CDA":
            ratio_columns = [col for col in self.df.columns if col.startswith("Ratio_")]
            self.x_data = self.df[ratio_columns[0]]
            self.y_data = self.df[ratio_columns[1]]
        if self.plot_type == "SA:Vol Ratio":
            self.x_data = self.df["Surface Area"]
            self.y_data = self.df["Volume"]
        if self.plot_type == "Custom":
            self.x_data = self.df[self.custom_x]
            self.y_data = self.df[self.custom_y][-1]

    def _mask_with_permutation(self):
        if self.permutation == 0:
            self._set_data()
            return
        mask = self.df["CDA_Permutation"] == int(self.permutation)
        self.x_data = self.x_data[mask]
        self.y_data = self.y_data[mask]
        if self.c_data is not None:
            self.c_data = self.c_data[mask]

    def _set_labels(self):
        if self.plot_type == "Zingg":
            self.x_label = "S:M"
            self.y_label = "M:L"
            self.title = "Zingg Diagram"
        if self.plot_type == "CDA":
            ratio_columns = [col for col in self.df.columns if col.startswith("Ratio_")]
            self.x_label = ratio_columns[0].replace("Ratio_", "")
            self.y_label = ratio_columns[1].replace("Ratio_", "")
            self.title = "Crystallographic Face-to-Face Distance Ratios"
        if self.plot_type == "SA:Vol Ratio":
            self.x_label = "Surface Area"
            self.y_label = "Volume"
            self.title = "Surface Area to Volume Ratio"
        if self.plot_type == "Custom":
            self.x_label = self.custom_x
            self.y_label = self.custom_y[-1]
            self.title = ""

    def _set_c(self):
        self.c_data = None
        self.c_name = None
        if self.custom_c == "None" and self.variable == "None":
            return
        if self.custom_c == "None":
            self.c_data = self.df[self.variable]
            self.c_name = self.variable
        if self.variable == "None":
            self.c_data = self.df[self.custom_c]
            self.c_name = self.custom_c

        if self.c_data is None:
            return
        # if c_data is not numerical
        if self.c_data.dtype.kind not in "biufc":
            self.c_data = pd.factorize(self.c_data)[0]

    def _set_c_label(self):
        variable = self.variable
        if self.plot_type == "Custom":
            variable = self.custom_c

        self.c_label = ""
        if variable.startswith("interaction") or variable.startswith("tile"):
            self.c_label = r"$\Delta G_{Cryst}$ (kcal/mol)"
        if variable.startswith("starting_delmu"):
            self.c_label = r"$\Delta G_{Cryst}$ (kcal/mol)"
        if variable.startswith("temperature_celcius"):
            self.c_label = "Temperature (℃)"
        if variable.startswith("excess"):
            self.c_label = r"$\Delta G_{Cryst}$ (kcal/mol)"

    def plot(self):
        logger.info("Plotting called!")
        logger.info(
            "Plot Type: %s, Permutation: %s, Variable: %s, Custom X: %s, Custom Y: %s, Custom C: %s, Grid: %s, Point Size: %s, ",
            self.plot_type,
            self.permutation,
            self.variable,
            self.custom_x,
            self.custom_y,
            self.custom_c,
            self.grid,
            self.point_size,
        )
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.canvas.draw()
        self.scatter = None

        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_title(self.title)

        if self.grid:
            self.ax.grid(True)
        else:
            self.ax.grid(False)

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

        if self.plot_type == "Growth Rates":
            self.x_data = self.df["Supersaturation"]
            # Store plot objects for reference (both line and scatter)
            self.plot_objects = {}

            for i in self.directions:
                self.scatter = self.ax.scatter(
                    self.x_data, self.df[i], s=self.point_size
                )
                (line,) = self.ax.plot(self.x_data, self.df[i], label=f"[{i}]")
                self.plot_objects[f"[{i}]"] = (line, self.scatter, None, None)
                self.ax.set_xlabel("Supersaturation (kcal/mol)")
                self.ax.set_ylabel("Growth Rate")
                self.ax.set_title("Growth Rates")

            # Create a legend
            legend = self.ax.legend()

            for legline in legend.get_lines():
                legline.set_picker(5)  # Enable clicking on the legend line
                legline.figure.canvas.mpl_connect("pick_event", self.on_legend_click)

            return

        # Capture bad calls to plot
        if self.x_data is None:
            return
        if self.x_data.size == 0 or self.y_data.size == 0:
            return

        # Plot the data
        if self.c_data is not None:
            self.scatter = self.ax.scatter(
                self.x_data,
                self.y_data,
                c=self.c_data,
                cmap="plasma",
                s=self.point_size,
            )
            # Add colorbar
            cbar = self.figure.colorbar(self.scatter)
            cbar.set_label(self.c_label)
            cbar.ax.set_zorder(-1)

        if self.c_data is None:
            self.scatter = self.ax.scatter(self.x_data, self.y_data, s=self.point_size)

        if self.plot_type == "Zingg":
            self.ax.axhline(y=0.66, color="black", linestyle="--")
            self.ax.axvline(x=0.66, color="black", linestyle="--")
            self.ax.set_xlim(0, 1.0)
            self.ax.set_ylim(0, 1.0)

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
                f" x: {x:.2f}\n"
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
                # Check if scatter plot exists and handle hover event
                if self.scatter is not None:
                    cont, ind = self.scatter.contains(event)
                    if cont:
                        self.update_annot(
                            self.scatter,
                            self.c_data,
                            self.c_name,
                            ind,
                        )
                        self.annot.set_visible(True)
                        self.figure.canvas.draw_idle()

                # Hide annotation if no scatter plot contains the event
                if not cont and vis:
                    self.annot.set_visible(False)
                    self.figure.canvas.draw_idle()
        except NameError:
            pass

    def on_legend_click(self, event):
        legline = event.artist
        origline, origscatter, _, _ = self.plot_objects[legline.get_label()]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        origscatter.set_visible(vis)
        legline.set_alpha(1.0 if vis else 0.2)

    def on_click(self, event):
        if event.inaxes == self.ax:
            # Check if scatter plot exists and handle click event
            if self.scatter is not None:
                cont, ind = self.scatter.contains(event)
                if cont:
                    self.handle_click(self.scatter, self.c_data, self.c_name, ind)

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
