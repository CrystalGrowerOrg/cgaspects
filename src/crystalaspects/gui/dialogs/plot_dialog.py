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
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QGridLayout,
)
from PySide6.QtGui import QIcon


from crystalaspects.gui.dialogs.plotsavedialog import PlotSaveDialog
from crystalaspects.gui.widgets.plot_axes_widget import (
    PlotAxesWidget,
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

        self.signals = signals
        self.annot = None
        self.trendline = None
        self.trendline_text = None

        self.selected_plot = None
        self.plot_obj_tuple = namedtuple(
            "Plot",
            ["scatter", "line", "trendline"],
        )
        self.plot_objects = {}
        self.plot_types = []
        self.directions = []
        self.permutations = []
        self.permutation_labels = []
        self.interaction_columns = []
        self.trendline_text = []
        self.plotting_mode = "default"

        self.setPlotDefaults()
        self.create_widgets()
        self.create_layout()
        self.setCSV(csv)
        self.trigger_plot()

    def setPlotDefaults(self):
        self.grid = None
        self.cbar = None
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

    def setCSV(self, csv):
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
        self.updatePlotWidgets()

    def updatePlotWidgets(self):
        self.custom_plot_widget.xAxisListWidget.clear()
        self.custom_plot_widget.yAxisListWidget.clear()
        self.custom_plot_widget.colorListWidget.clear()
        self.plot_permutations_combobox.clear()
        self.plot_types_combobox.clear()
        self.variables_combobox.clear()

        self.plot_permutations_combobox.addItems(self.permutation_labels)
        self.plot_types_combobox.addItems(self.plot_types)
        self.variables_combobox.addItems(self.interaction_columns)

        if self.df is not None:
            self.custom_plot_widget.xAxisListWidget.addItems(self.df.columns)
            self.custom_plot_widget.yAxisListWidget.addItems(self.df.columns)
            self.custom_plot_widget.colorListWidget.addItems(["None"])
            self.custom_plot_widget.colorListWidget.addItems(self.df.columns)

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

        # if "CDA" in self.plot_types:
        self.plot_permutations_label = QLabel("Permutations: ")
        self.plot_permutations_label.setAlignment(QtCore.Qt.AlignRight)
        self.plot_permutations_label.setToolTip(
            "Crystallographic face-to-face distance ratios in ascending order"
        )
        self.plot_permutations_combobox = QComboBox(self)

        self.variables_label = QLabel("Variable: ")
        self.variables_label.setAlignment(QtCore.Qt.AlignRight)
        self.variables_combobox = QComboBox(self)

        self.custom_plot_widget = PlotAxesWidget()

        self.spin_point_size = QSpinBox()
        self.spin_point_size.setRange(1, 100)

        self.button_save = QPushButton("Export...")
        self.exportIcon = QIcon(
            ":material_icons/material_icons/png/content-save-custom.png"
        )
        self.button_save.setIcon(self.exportIcon)
        self.button_add_trendline = QPushButton("Add Trendline")

        # Initialize the variables
        self.point_size = 12
        self.spin_point_size.setValue(self.point_size)
        self.colorbar = False

        # Initialize checkboxes
        self.checkbox_grid = QCheckBox("Show Grid")
        self.checkbox_legend = QCheckBox("Show Legend")

        self.canvas.mpl_connect(
            "motion_notify_event", lambda event: self.on_hover(event)
        )

        self.button_save.clicked.connect(self.save)
        self.checkbox_grid.stateChanged.connect(self.trigger_plot)
        self.checkbox_legend.stateChanged.connect(self.trigger_plot)
        self.button_add_trendline.clicked.connect(self.toggle_trendline)
        self.spin_point_size.valueChanged.connect(self.set_point_size)
        self.plot_types_combobox.currentIndexChanged.connect(self.trigger_plot)

        if self.plot_permutations_combobox is not None:
            self.plot_permutations_combobox.currentIndexChanged.connect(
                self.trigger_plot
            )
        if self.variables_combobox is not None:
            self.variables_combobox.currentIndexChanged.connect(self.trigger_plot)

        self.custom_plot_widget.xAxisListWidget.currentItemChanged.connect(
            self.trigger_plot
        )
        self.custom_plot_widget.yAxisListWidget.itemCheckedStateChanged.connect(
            self.trigger_plot
        )
        self.custom_plot_widget.colorListWidget.currentItemChanged.connect(
            self.trigger_plot
        )

    def create_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.toolbar)
        hbox1.addWidget(self.checkbox_legend)
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
        for plot in self.plot_objects.values():
            if plot.scatter is not None:
                plot.scatter.set_sizes(
                    [self.point_size] * len(plot.scatter.get_offsets())
                )
        self.canvas.draw()

    def change_mode(self, mode):
        if mode == "Custom":
            self.plot_permutations_label.setEnabled(False)
            self.plot_permutations_combobox.setEnabled(False)
            self.plot_permutations_combobox.setCurrentIndex(0)
            self.variables_label.setEnabled(False)
            self.variables_combobox.setEnabled(False)
            self.variables_combobox.setCurrentIndex(0)
            self.custom_plot_widget.show()

        if mode != "Custom":
            self.plot_permutations_label.setEnabled(True)
            self.plot_permutations_combobox.setEnabled(True)
            self.variables_label.setEnabled(True)
            self.variables_combobox.setEnabled(True)
            self.custom_plot_widget.hide()

    def trigger_plot(self):
        self.setPlotDefaults()
        self.grid = self.checkbox_grid.isChecked()
        self.show_legend = self.checkbox_legend.isChecked()
        self.point_size = self.spin_point_size.value()
        self.plot_type = self.plot_types_combobox.currentText()
        self.permutation = int(self.plot_permutations_combobox.currentIndex())
        self.variable = self.variables_combobox.currentText()
        (
            self.custom_x,
            self.custom_y,
            self.custom_c,
        ) = self.custom_plot_widget.get_selections()
        self.custom_y = [tmp[1] for tmp in self.custom_y]

        self.change_mode(mode=self.plot_type)
        self._set_data()
        self._set_c()
        self._mask_with_permutation()
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
        if self.plot_type == "Growth Rates":
            self.x_data = self.df["Supersaturation"]
            self.y_data = self.df[self.directions]
        if self.plot_type == "Custom":
            self.x_data = None
            self.y_data = None
            try:
                self.x_data = self.df[self.custom_x]
                self.y_data = self.df[self.custom_y]
            except KeyError as exc:
                logger.warning(
                    "X and Y data not been set, invalid axis title!\n%s", exc
                )

        self.y_data = self._ensure_pd_series(self.y_data)

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
        if self.plot_type == "Growth Rates":
            self.x_label = "Supersaturation (kcal/mol)"
            self.y_label = "Relative Growth Rate"
            self.title = "Growth Rates vs supersaturation"
        if self.plot_type == "Custom":
            self.title = ""
            self.x_label = self.custom_x
            self.y_label = ""

            if len(self.custom_y) == 1:
                self.y_label = self.custom_y[0]
            elif len(self.custom_y) <= 3:
                self.y_label = ", ".join(self.custom_y)
            else:
                self.y_label = "Multiple columns..."

    def _set_c(self):
        self.c_data = None
        self.c_name = None
        if self.plot_type != "Custom":
            self.custom_c = "None"
        if self.plot_type == "Custom":
            self.variable = "None"

        if self.custom_c == "None" and self.variable == "None":
            return
        if self.custom_c == "None":
            self.c_data = self.df[self.variable]
            self.c_name = self.variable
        if self.variable == "None":
            self.c_data = self.df[self.custom_c]
            self.c_name = self.custom_c
        if self.variable == "None" and self.plot_type != "Custom":
            self.c_data = None
            self.c_name = None

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
        self.plot_objects = {}
        logger.info("Plotting called!")
        logger.info(
            "Plot Called!\nType: %s, Permutation: %s, Variable: %s, \nCustom X: %s, Custom Y: %s, Custom C: %s, \nGrid: %s, Legend: %s, Point Size: %s, ",
            self.plot_type,
            self.permutation,
            self.variable,
            self.custom_x,
            self.custom_y,
            self.custom_c,
            self.grid,
            self.show_legend,
            self.point_size,
        )
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.clear()
        self.canvas.draw()

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

        if self.x_data is None or self.y_data is None:
            logger.warning("No data for plotting!")
            return

        markers = [
            "o",  # Circle
            "^",  # Triangle up
            "s",  # Square
            "D",  # Diamond
            "v",  # Triangle down
            "p",  # Pentagon
            "*",  # Star
            "h",  # Hexagon
            "+",  # Plus
            "x",  # Cross
        ]

        # Plot the data
        if self.y_data.ndim == 1:
            # 1D y_data
            self._plot(x=self.x_data, y=self.y_data, c=self.c_data)
        if self.y_data.ndim == 2 and self.y_data.shape[1] > 1:
            # y_data with multiple columns
            line = True if self.plot_type == "Growth Rates" else False
            for i, y in enumerate(self.y_data):
                self._plot(
                    x=self.x_data,
                    y=self._ensure_pd_series(self.df[y]),
                    c=self.c_data,
                    add_line=line,
                    label=y,
                    marker=markers[i % len(markers)],
                )
            self._set_legend() if self.show_legend else None

        if self.plot_type == "Zingg":
            self.ax.axhline(y=0.66, color="black", linestyle="--")
            self.ax.axvline(x=0.66, color="black", linestyle="--")
            self.ax.set_xlim(0, 1.0)
            self.ax.set_ylim(0, 1.0)

        # Add colorbar after plotting all data
        if self.c_data is not None and self.plot_objects:
            # Take the frist scatter object to attach the colorbar
            scatter = list(self.plot_objects.values())[0].scatter
            self.cbar = self.figure.colorbar(scatter)
            self.cbar.set_label(self.c_label)
            self.cbar.ax.set_zorder(-1)

        self.canvas.draw()

    def _plot(
        self, x, y, c=None, cmap="plasma", add_line=False, label=None, marker="o"
    ):
        cmap = None if c is None else cmap
        label = y.name if label is None else label
        line = None
        logger.info("X SIZE: %s    Y SIZE: %s", self.x_data.size, self.y_data.size)
        scatter = self.ax.scatter(
            x=x,
            y=y,
            c=c,
            cmap=cmap,
            s=self.point_size,
            label=label if self.plot_type != "Growth Rates" else None,
            marker=marker,
        )
        if add_line:
            (line,) = self.ax.plot(x, y, label=label)

        plot_object = self.plot_obj_tuple(scatter=scatter, line=line, trendline=None)
        self.plot_objects[label] = plot_object

    def _set_legend(self):
        # Create a legend
        legend = self.ax.legend()

        for legend_line in legend.get_lines():
            legend_line.set_picker(5)
            legend_line.figure.canvas.mpl_connect("pick_event", self.on_legend_click)

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
            if event.inaxes != self.ax:
                return

            cont = False

            # Function to handle hover event for a scatter plot
            def handle_hover(scatter):
                nonlocal cont
                cont, ind = scatter.contains(event)
                if cont:
                    self.update_annot(
                        scatter,
                        self.c_data,
                        self.c_name,
                        ind,
                    )
                    self.annot.set_visible(True)
                    self.figure.canvas.draw_idle()

            for plot in self.plot_objects.values():
                handle_hover(scatter=plot.scatter)

            # Hide annotation if no scatter plot contains the event
            if not cont and vis:
                self.annot.set_visible(False)
                self.figure.canvas.draw_idle()

        except NameError:
            pass

    def on_legend_click(self, event):
        legend_line = event.artist
        p = self.plot_objects[legend_line.get_label()]
        vis = not p.line.get_visible()
        p.line.set_visible(vis)
        p.scatter.set_visible(vis)
        legend_line.set_alpha(1.0 if vis else 0.2)

    def on_click(self, event):
        if event.inaxes != self.ax:
            return
        cont = False

        def handle_scatter(scatter):
            # Check if scatter plot exists and handle click event
            if scatter is not None:
                cont, ind = scatter.contains(event)
                if cont:
                    self.handle_click(scatter, self.c_data, self.c_name, ind)

        for plot in self.plot_objects.values():
            handle_scatter(scatter=plot.scatter)

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
        logger.info(self.trendline_text)
        if not self.trendline:
            for i, (name, plot) in enumerate(self.plot_objects.items()):
                if plot.scatter is None:
                    return

                x = plot.scatter.get_offsets()[:, 0]
                y = plot.scatter.get_offsets()[:, 1]

                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                (trendline,) = self.ax.plot(x, p(x), "r--")
                self.plot_objects[name] = plot._replace(trendline=trendline)

                # Calculate the Pearson correlation coefficient
                r = np.corrcoef(x, y)[0, 1]

                equation_text = f"y = {z[0]:.2f}x + {z[1]:.2f}  [R={r:.2f}]"

                self.trendline_text.append(
                    self.ax.text(
                        0.05,
                        1 - (0.08 * i),
                        equation_text,
                        transform=self.ax.transAxes,
                        fontsize=10,
                        verticalalignment="top",
                    )
                )
            self.trendline = True
            self.canvas.draw()
            self.button_add_trendline.setText("Remove Trendline")
        else:
            for name, plot in self.plot_objects.items():
                # Remove the trendline from the plot
                if plot.trendline:
                    plot.trendline.remove()
                    self.plot_objects[name] = plot._replace(trendline=None)

            # Remove the trendline text from the plot
            for text in self.trendline_text:
                text.remove()
            self.trendline_text = []

            self.canvas.draw()
            self.trendline = False
            self.button_add_trendline.setText("Add Trendline")

    def save(self):
        file_dialog = PlotSaveDialog(self.figure)
        if file_dialog.exec() == QDialog.Accepted:
            logger.debug("Closing PlotSaveDialog: accepted")
        else:
            logger.debug("Closing PlotSaveDialog: not accepted")

    def _ensure_pd_series(self, data):
        """
        Ensure the data is a Pandas Series.
        - If the input is a mutiple-column DataFrame, it's returned as is.
        - If the input is a single-column DataFrame, it's converted to a Series.
        - If the input is already a Series or 1D array, it's returned as is.
        """
        if isinstance(data, pd.DataFrame) and data.shape[1] == 1:
            return data.iloc[:, 0]
        return data
