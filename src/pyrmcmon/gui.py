import sys
import os

from PyQt6.QtCore import (pyqtSignal, pyqtSlot)
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QTabWidget, QVBoxLayout, QFileDialog
import pyqtgraph as pg
from dataclasses import dataclass
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

def get_dir_and_stem(file):
    dirname = os.path.dirname(file)
    stem = os.path.splitext(os.path.basename(file))[0]

    return (dirname, stem)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyRMCMon")

        self.container = QWidget()

        self.hbox = QHBoxLayout()

        self.controls = ControlPane()
        self.hbox.addWidget(self.controls)

        self.tabs = QTabWidget()

        self.SQTab = SQTab()
        self.PartialSQTab = PartialSQTab()
        self.BraggTab = BraggTab()
        self.PDFTab = PDFTab()
        self.PartialPDFTab = PartialPDFTab()
        self.tabs.addTab(self.SQTab, "S(Q)")
        self.tabs.addTab(self.PartialSQTab, "S(Q) Partials")
        self.tabs.addTab(self.BraggTab, "Bragg")
        self.tabs.addTab(self.PDFTab, "PDF")
        self.tabs.addTab(self.PartialPDFTab, "PDF Partials")

        self.hbox.addWidget(self.tabs)

        self.container.setLayout(self.hbox)

        self.controls.rmc_file_selected.connect(self.handle_rmc_file_selected)
        self.controls.rmc_file_selected.connect(self.SQTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.PartialSQTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.BraggTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.PDFTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.PartialPDFTab.plot_rmc)

        self.setCentralWidget(self.container)


    @pyqtSlot(str)
    def handle_rmc_file_selected(self, filename):
        print(f"RMC file selected: {filename}")

class ControlPane(QWidget):
    rmc_file_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.vbox = QVBoxLayout()

        self.select_button = QPushButton("Select RMC .dat file")
        self.select_button.clicked.connect(self.select_rmc_dat_file)
        self.vbox.addWidget(self.select_button)

        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.refresh_data)
        self.vbox.addWidget(self.refresh_button)

        self.rmc_file = ""


        self.setLayout(self.vbox)

    def select_rmc_dat_file(self):
        file = QFileDialog.getOpenFileName(self, "Select RMC .dat file")

        # No file selected
        if file[0] == "":
            return

        self.rmc_file = file[0]
        self.rmc_file_selected.emit(self.rmc_file)

    def refresh_data(self):
        self.rmc_file_selected.emit(self.rmc_file)


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure()
        self.fig = fig
        self.axes = fig.add_subplot(111)
        super().__init__(fig)   

    def update_plot(self):
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.canvas = MplCanvas()
        self.fig = self.canvas.fig
        self.axes = self.canvas.axes
        self.toolbar = NavigationToolbar2QT(self.canvas)

        layout = QVBoxLayout()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self):
        self.canvas.update_plot()

class SQTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.plot = PlotWidget()
        self.layout.addWidget(self.plot)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def plot_rmc(self, file):
        self.plot.axes.clear()
        self.plot.update_plot()
        dirname, stem = get_dir_and_stem(file)
        SQ1_filename = f"{dirname}/{stem}_SQ1.csv"
        try:
            self.data = np.genfromtxt(SQ1_filename, delimiter=",")
        except Exception as e:
            print(e)
            return

        self.plot.axes.plot(self.data[:, 0], self.data[:, 2], label="Data",
                            color="k")
        self.plot.axes.plot(self.data[:, 0], self.data[:, 1], label="RMC",
                            color="tab:red", ls="--")
        self.plot.axes.set_xlabel(r"Q [$\AA^{-1}$]", fontsize=16)
        self.plot.axes.set_ylabel(r"S(Q)", fontsize=16)
        self.plot.axes.legend()
        
        self.plot.update_plot()


class PartialSQTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.plot = PlotWidget()
        self.layout.addWidget(self.plot)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def plot_rmc(self, file):
        self.plot.axes.clear()
        self.plot.update_plot()
        dirname, stem = get_dir_and_stem(file)
        filename = f"{dirname}/{stem}_SQ1partials.csv"
        try: 
            self.data = np.genfromtxt(filename, delimiter=",", skip_header=1)
        except Exception as e:
            print(e)
            return


        header = []
        with open(filename) as f:
            for line in f:
                header = line.replace("\n", "").split(",")
                break


        for i in range(1, len(header)):
            self.plot.axes.plot(self.data[:, 0], self.data[:, i], label=header[i])

        self.plot.axes.set_xlabel(r"Q [$\AA^{-1}$]", fontsize=16)
        self.plot.axes.set_ylabel(r"S(Q)", fontsize=16)
        self.plot.axes.legend()

        self.plot.update_plot()



class BraggTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.plot = PlotWidget()
        self.layout.addWidget(self.plot)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def plot_rmc(self, file):
        self.plot.axes.clear()
        dirname, stem = get_dir_and_stem(file)
        SQ1_filename = f"{dirname}/{stem}_bragg.csv"
        try:
            self.data = np.genfromtxt(SQ1_filename, delimiter=",")
        except Exception as e:
            print(e)
            return


        self.plot.axes.plot(self.data[:, 0], self.data[:, 2], label="Data",
                            color="k")
        self.plot.axes.plot(self.data[:, 0], self.data[:, 1], label="RMC",
                            color="tab:red", ls="--")
        self.plot.axes.set_xlabel(r"TOF or 2$\theta$", fontsize=16)
        self.plot.axes.set_ylabel(r"Intensity", fontsize=16)
        self.plot.axes.legend()
        
        self.plot.update_plot()


class PDFTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.plot = PlotWidget()
        self.layout.addWidget(self.plot)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def plot_rmc(self, file):
        self.plot.axes.clear()
        self.plot.update_plot()
        dirname, stem = get_dir_and_stem(file)
        filename = f"{dirname}/{stem}_PDF1.csv"
        try:
            self.data = np.genfromtxt(filename, delimiter=",")
        except Exception as e:
            print(e)
            return

        self.plot.axes.plot(self.data[:, 0], self.data[:, 2], label="Data",
                            color="k")
        self.plot.axes.plot(self.data[:, 0], self.data[:, 1], label="RMC",
                            color="tab:red", ls="--")
        self.plot.axes.set_xlabel(r"r [$\AA$]", fontsize=16)
        self.plot.axes.set_ylabel(r"G(r), D(r), or T(r)", fontsize=16)
        self.plot.axes.legend()
        
        self.plot.update_plot()

class PartialPDFTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.plot = PlotWidget()
        self.layout.addWidget(self.plot)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def plot_rmc(self, file):
        self.plot.axes.clear()
        self.plot.update_plot()
        dirname, stem = get_dir_and_stem(file)
        filename = f"{dirname}/{stem}_PDFpartials.csv"
        try:
            self.data = np.genfromtxt(filename, delimiter=",", skip_header=1)
        except Exception as e:
            print(e)
            return

        header = []
        with open(filename) as f:
            for line in f:
                header = line.replace("\n", "").split(",")
                break


        for i in range(1, len(header)):
            self.plot.axes.plot(self.data[:, 0], self.data[:, i], label=header[i])

        self.plot.axes.set_xlabel(r"r [$\AA$]", fontsize=16)
        self.plot.axes.set_ylabel(r"G(r), D(r), or T(r)", fontsize=16)
        self.plot.axes.legend()

        self.plot.update_plot()
