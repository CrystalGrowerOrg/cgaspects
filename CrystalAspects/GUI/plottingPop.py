import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plot Window")
        self.setGeometry(100, 100, 800, 600)
        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.button = QPushButton("Plot")
        self.button.clicked.connect(self.plot)

    def create_layout(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.button)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)

        self.setLayout(hbox)
        self.statusBar().showMessage("Ready")

    def plot(self):
        x = np.linspace(-5, 5, 100)
        y = np.sin(x)

        self.ax.clear()
        self.ax.plot(x, y)
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)

        self.button = QPushButton("Open Plot Window")
        self.button.clicked.connect(self.open_plot_window)

        vbox = QVBoxLayout()
        vbox.addWidget(self.button)

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)

        central_widget = QWidget()
        central_widget.setLayout(hbox)

        self.setCentralWidget(central_widget)
        self.statusBar().showMessage("Ready")

    def open_plot_window(self):
        plot_window = PlotWindow(self)
        plot_window.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
