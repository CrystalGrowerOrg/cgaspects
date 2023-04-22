import numpy as np
import pandas as pd
from pathlib import Path
import ast

# PyQt imports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QMessageBox, QInputDialog

# Matplotlib import
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('QT5Agg')

from CrystalAspects.data.find_data import Find
from CrystalAspects.data.growth_rates import GrowthRate
from CrystalAspects.data.aspect_ratios import AspectRatio
from CrystalAspects.visualisation.plot_data import Plotting


class Replotting:
    '''def __init__(self):
        pass'''

    def __init__(self):
        super(Replotting, self).__init__()

    def calculate_plots(self, csv="", info=""):
        print("Info:  ")
        print(info)
        print("Entered calculate plots")
        if csv != "":
            folderpath = Path(csv).parents[0]
            df = pd.read_csv(csv)
        plot_list = []
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]
        print(interactions)
        number_interactions = len(interactions)
        print(number_interactions)
        equations = []
        if info.Equations == True:
            equations = self.read_equations()

        if info.PCA == True:
            plot_list.append("Morphology Map")
        if info.Energies and info.PCA == True:
            for interaction in interactions:
                plot_list.append("Morphology Map vs " + interaction)
        if info.PCA and info.Equations == True:
            for equation in equations:
                plot_list.append("Morphology Map filtered by " + equation)
        if info.CDA == True:
            plot_list.append("CDA Aspect Ratio")
        if info.CDA and info.Energies == True:
            for interaction in interactions:
                plot_list.append("CDA Aspect Ratio " + interaction)
        if info.SAVol == True:
            plot_list.append("Surface Area vs Volume")
        if info.SAVol and info.Energies == True:
            for interaction in interactions:
                plot_list.extend("Surface area vs Volume " + interaction)
        if info.CDA_Extended == True:
            plot_list.append("Extended CDA")
        if info.CDA_Extended and info.Energies == True:
            for interaction in interactions:
                plot_list.append("Extended CDA " + interaction)
        if info.CDA and info.Temperature == True:
            plot_list.append("CDA Aspect Ratio vs Temperature")
        if info.Temperature and info.PCA == True:
            plot_list.append("Morphology Map vs Temperature")
        if info.GrowthRates == True:
            plot_list.append("Growth Rates")
        print("List of plots =====")
        print(plot_list)

        return plot_list

    def read_equations(self):
        print("Entering Read Equations")
        msg = QMessageBox()
        msg.setText("CDA Equations found. Please open CDA_equations.txt")
        msg.setIcon(QMessageBox.Question)
        msg.exec_()
        equations_list = []

        equations_txt, _ = QtWidgets.QFileDialog.getOpenFileName(
                None, "Select CDA_Equations .csv"
            )

        with open(equations_txt, "r", encoding="utf-8") as eq_txt:
            eq_line = eq_txt.read()
            if eq_line.startswith("Equation Number1"):
                eq_msg = QMessageBox()
                eq_msg.setText(eq_line)
                eq_msg.exec_()
                with open(equations_txt, "r", encoding="utf-8") as eq_file:
                    equation_lines = eq_file.readlines()
                    print(equation_lines)
                    for line in equation_lines:
                        tuple_str = line.split(':')[1].strip()
                        tuple_obj = ast.literal_eval(tuple_str)
                        equation_obj = tuple_obj[0] + ' : ' \
                                       + tuple_obj[1] + ' : ' \
                                       + tuple_obj[2]
                        equations_list.append(equation_obj)
            else:
                eq_problem = QMessageBox()
                eq_problem.setText("File incorrect.\n"
                                   "Please select file named: CDA_equations.txt")
                eq_problem.setIcon(QMessageBox.Critical)
                eq_problem.setStandardButtons(QMessageBox.Retry)
                eq_problem.exec_()
                if QMessageBox.Retry:
                    # User clicked "Retry"
                    self.read_equations()
                    return

        print("equations_list :  ")
        print(equations_list)
        return equations_list

    def plotting_called(self, csv, selected, frame):
        print("entering plotting called")
        df = pd.read_csv(csv)
        print(df)
        selected = selected
        print(selected)
        # Creat horizontal layout
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(frame)
        # Create Canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        # End canvas
        # Add canvas
        self.horizontalLayout_4.addWidget(self.canvas)
        # End of horizontal layout

        if selected == "Morphology Map":
            #self.figure.clear()
            print("Entering Morphology Map")
            x_data = df['S:M']
            y_data = df['M:L']
            # Plot the data
            plt.scatter(x_data, y_data, s=1.2)
            plt.axhline(y=0.66, color='black', linestyle='--')
            plt.axvline(x=0.66, color='black', linestyle='--')
            plt.xlabel('S:M')
            plt.ylabel('M:L')
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            self.canvas.draw()

            # Refresh canvas
            #self.canvas.draw()


    def replot_AR(self, csv, info, selected):
        print('Entered Plotting')
        print(csv, info, selected)
        folderpath = Path(csv)
        df = pd.read_csv(csv)
        #savefolder = self.create_plots_folder(folderpath)
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        x_data = df["S:M"]
        y_data = df["M:L"]
        print(x_data)

        # Clear figure
        self.figure.clear()

        # Plot the data
        plt.scatter(x_data, y_data, s=1.2)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlabel('S:M')
        plt.ylabel('M:L')
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)

        # Refresh canvas
        self.canvas.draw()

        for interaction in interactions:
            c_df = df[interaction]
            colour = list(set(c_df))
            textstr = interaction
            props = dict(boxstyle="square", facecolor="white")

            plt.figure()
            print("FIG")
            plt.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
            plt.axhline(y=0.66, color="black", linestyle="--")
            plt.axvline(x=0.66, color="black", linestyle="--")
            plt.title(textstr)
            plt.xlabel("S: M")
            plt.ylabel("M: L")
            plt.xlim(0.0, 1.0)
            plt.ylim(0.0, 1.0)
            cbar = plt.colorbar(ticks=colour)
            cbar.set_label(r"$\Delta G_{Cryst}$ (kcal/mol)")
            #pylustrator.start()
            #plt.show()

        """
        CDA
        CDA + Eq
        CDA + Int
        Cryst D + Int
        PCA
        PCA + CDA Eq
        PCA + Int 
        """

    def replot_GrowthRate(self, csv, info, selected, savepath):
        plt.close()
        print(csv, info, selected)
        gr_df = pd.read_csv(csv)
        x_data = gr_df["Supersaturation"]
        print(selected)
        for i in selected:
            print(selected)
            plt.scatter(x_data, gr_df[i], s=1.2)
            plt.plot(x_data, gr_df[i], label=i)
            plt.legend()
            plt.xlabel("Supersaturation (kcal/mol)")
            plt.ylabel("Growth Rate")
            plt.tight_layout()
            #pylustrator.start()
            plt.show()



    def replot_SAVAR(self, csv):
        pass

class testing:

    def __init__(self):
        super(testing, self).__init__()


    def testplot(self, parent=None, width=5, height=4, dpi=100):
        print(csv, info, selected)
        folderpath = Path(csv)
        df = pd.read_csv(csv)
        # savefolder = self.create_plots_folder(folderpath)
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]

        x_data = df["S:M"]
        y_data = df["M:L"]
        print(x_data)

        # Clear figure
        self.figure.clear()

        # Plot the data
        plt.scatter(x_data, y_data, s=1.2)
        plt.axhline(y=0.66, color='black', linestyle='--')
        plt.axvline(x=0.66, color='black', linestyle='--')
        plt.xlabel('S:M')
        plt.ylabel('M:L')
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)

        # Refresh canvas
        self.canvas.draw()



