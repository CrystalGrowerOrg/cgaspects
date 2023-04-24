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

    def __init__(self):
        super(Replotting, self).__init__()
        self.equations_list = []

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
        if info.Energies and info.PCA and info.Equations == True:
            for interaction in interactions:
                for equation in equations:
                    plot_list.append("Morphology Map filter energy " + interaction + " " + equation)
        if info.CDA == True:
            plot_list.append("CDA Aspect Ratio")
        if info.CDA and info.Energies == True:
            for interaction in interactions:
                plot_list.append("CDA Aspect Ratio " + interaction)
        if info.SAVol == True:
            plot_list.append("Surface Area vs Volume")
        if info.SAVol and info.Energies == True:
            for interaction in interactions:
                plot_list.append("Surface Area vs Volume vs Energy " + interaction)
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

        return plot_list, equations

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
            '''else:
                eq_problem = QMessageBox()
                eq_problem.setText("File incorrect.\n"
                                   "Please select file named: CDA_equations.txt")
                eq_problem.setIcon(QMessageBox.Critical)
                eq_problem.setStandardButtons(QMessageBox.Retry)
                eq_problem.exec_()
                if QMessageBox.Retry:
                    # User clicked "Retry"
                    self.read_equations()
                    return'''

        print("equations_list :  ")
        print(equations_list)
        self.equations_list = equations_list
        print("self.equations_list ======")
        print(self.equations_list)

        return equations_list

    def plotting_called(self, csv, selected, plot_frame, equations_list):
        print("entering plotting called")
        # Reading the dataframe
        df = pd.read_csv(csv)
        print(df)
        # Reading self.current_plots() coming from self.SelectPlots.currentText()
        selected = selected
        # Finding interactions in data frame if there are any
        interactions = [
            col
            for col in df.columns
            if col.startswith("interaction") or col.startswith("tile")
        ]
        print(interactions)
        print(selected)
        # Finding extended CDA in data frame if there are any
        extended = [col for col in df.columns
                    if col.startswith("AspectRatio")]
        print(extended)
        # Create horizontal layout
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(plot_frame)
        # Create Canvas
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        # End canvas
        # Add canvas
        self.horizontalLayout_4.addWidget(self.canvas)
        # End of horizontal layout

        if selected == "PCA Morphology Map":
            #self.figure.clear()
            print("Entering PCA Morphology Map")
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

        print("printing selected:   ")
        print(selected)

        for interaction in interactions:
            if selected.startswith("Morphology Map vs " + interaction) \
                    or selected.startswith("CDA Aspect Ratio " + interaction)\
                    or selected.startswith("Extended CDA " + interaction)\
                    or selected.startswith("Surface Area vs Volume vs Energy" + interaction):
                self.figure.clear()
                print(interaction)
                print("Entering Morphology Map vs " + interaction)
                self.axes = self.figure.add_subplot(111)
                c_df = df[interaction]
                colour = list(set(c_df))
                if selected.startswith("Morphology Map vs "):
                    x_data = df['S:M']
                    y_data = df['M:L']
                    self.axes.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
                    self.axes.axhline(y=0.66, color='black', linestyle='--')
                    self.axes.axvline(x=0.66, color='black', linestyle='--')
                    self.axes.set_xlabel('S: M')
                    self.axes.set_ylabel('M: L')
                    self.axes.set_xlim(0.0, 1.0)
                    self.axes.set_ylim(0.0, 1.0)
                if selected.startswith("CDA Aspect Ratio "):
                    x_data = df['S/M']
                    y_data = df['M/L']
                    self.axes.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
                    self.axes.axhline(y=0.66, color='black', linestyle='--')
                    self.axes.axvline(x=0.66, color='black', linestyle='--')
                    self.axes.set_xlabel('S/ M')
                    self.axes.set_ylabel('M/ L')
                    self.axes.set_xlim(0.0, 1.0)
                    self.axes.set_ylim(0.0, 1.0)
                if selected.startswith("Extended CDA "):
                    print("extended CDA")
                    x_data = df[extended[0]]
                    y_data = df[extended[1]]
                    print(x_data)
                    self.axes.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
                    '''self.axes.axhline(y=0.66, color='black', linestyle='--')
                    self.axes.axvline(x=0.66, color='black', linestyle='--')'''
                    self.axes.set_xlabel(extended[0])
                    self.axes.set_ylabel(extended[1])
                if selected.startswith("Surface Area vs Volume vs Energy"):
                    print('Entered Surface Area vs Volume Plotting:  ')
                    x_data = df["Volume (Vol)"]
                    y_data = df["Surface_Area (SA)"]
                    self.axes.scatter(x_data, y_data, c=c_df, cmap="plasma", s=1.2)
                    self.axes.set_xlabel(r"Volume ($nm^3$)")
                    self.axes.set_ylabel(r"Surface Area ($nm^2$)")
                    # Plot the data
                self.canvas.draw()

        if selected.startswith("Morphology Map filtered by "):
            print("Morphology Map filtered by:   ")
            equation_integer = ''
            print(equations_list)
            for item in equations_list:
                if selected.endswith(item):
                    equation_integer = equations_list.index(item)
                    print(equation_integer)
            self.axes = self.figure.add_subplot(111)
            equation_df = df[df["CDA_Equation"] == equation_integer+1]
            x_data = equation_df["S:M"]
            y_data = equation_df["M:L"]
            self.axes.scatter(x_data, y_data, s=1.2)
            self.axes.axhline(y=0.66, color='black', linestyle='--')
            self.axes.axvline(x=0.66, color='black', linestyle='--')
            self.axes.set_xlabel('S: M')
            self.axes.set_ylabel('M: L')
            self.axes.set_xlim(0.0, 1.0)
            self.axes.set_ylim(0.0, 1.0)
            self.canvas.draw()

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



