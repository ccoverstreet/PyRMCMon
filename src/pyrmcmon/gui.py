import sys
import os

from PyQt6.QtCore import (pyqtSignal, pyqtSlot, QSettings)
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QHBoxLayout, QTabWidget, QVBoxLayout, QFileDialog, QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QTextEdit
import pyqtgraph as pg
from dataclasses import dataclass
import numpy as np

from .stog_gui import StoGPage
from .util_gui import PlotWidget

SETTINGS = QSettings("CCO", "PyRMCMon")

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

        self.main_tabs = QTabWidget()

        self.monitor_page = MonitorPage()
        self.main_tabs.addTab(self.monitor_page, "Monitor")

        self.stog_page = StoGPage()
        self.main_tabs.addTab(self.stog_page, "StoG")

        self.hbox.addWidget(self.main_tabs)

        self.container.setLayout(self.hbox)


        self.setCentralWidget(self.container)

        self.setMinimumSize(1000, 700)



class MonitorPage(QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super().__init__()

        self.hbox = QHBoxLayout()
        self.left_widget = QWidget()
        self.left_widget.setMaximumWidth(200)
        self.vbox_left = QVBoxLayout(self.left_widget)

        self.controls = ControlPane()
        self.vbox_left.addWidget(self.controls)
        self.rmc_data_file_label = QLabel("")
        self.rmc_data_file_label.setWordWrap(True)
        self.vbox_left.addWidget(self.rmc_data_file_label)

        self.hbox.addWidget(self.left_widget)


        self.tabs = QTabWidget()

        self.SQTab = SQTab()
        self.PartialSQTab = PartialSQTab()
        self.BraggTab = BraggTab()
        self.PDFTab = PDFTab()
        self.PartialPDFTab = PartialPDFTab()
        self.Chi2Tab = Chi2Tab()
        self.ConfigFileTab = ConfigFileTab()
        self.RMC6FTab = RMC6FTab()
        self.tabs.addTab(self.SQTab, "S(Q)")
        self.tabs.addTab(self.PartialSQTab, "S(Q) Partials")
        self.tabs.addTab(self.BraggTab, "Bragg")
        self.tabs.addTab(self.PDFTab, "PDF")
        self.tabs.addTab(self.PartialPDFTab, "PDF Partials")
        self.tabs.addTab(self.Chi2Tab, "Convergence")
        self.tabs.addTab(self.ConfigFileTab, "RMC Config")
        self.tabs.addTab(self.RMC6FTab, "RMC6F")

        self.hbox.addWidget(self.tabs)

        self.controls.rmc_file_selected.connect(self.handle_rmc_file_selected)
        self.controls.rmc_file_selected.connect(self.SQTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.PartialSQTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.BraggTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.PDFTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.PartialPDFTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.Chi2Tab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.ConfigFileTab.plot_rmc)
        self.controls.rmc_file_selected.connect(self.RMC6FTab.plot_rmc)

        self.setLayout(self.hbox)

    @pyqtSlot(str)
    def handle_rmc_file_selected(self, filename):
        print(f"RMC file selected: {filename}")
        self.rmc_data_file_label.setText(filename)


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

        self.vbox.addStretch(1)

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
            self.data = np.genfromtxt(SQ1_filename, delimiter=",", skip_header=1)
        except Exception as e:
            print(e)
            return

        self.plot.axes.plot(self.data[:, 0], self.data[:, 2], label="Data",
                            color="k")
        self.plot.axes.plot(self.data[:, 0], self.data[:, 1], label="RMC",
                            color="tab:red", ls="--")

        # Difference
        v_max = np.max(self.data[:, 1:3])
        v_min = np.min(self.data[:, 1:3])
        diff = v_max - v_min
        print(diff, v_max, v_min)
        self.plot.axes.axhline(v_min - 0.1*diff, color="k", ls=":")
        self.plot.axes.plot(self.data[:, 0],
                            self.data[:, 2] - self.data[:, 1] + v_min - 0.1*(diff),
                            color="tab:green")

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
        self.plot.update_plot()
        dirname, stem = get_dir_and_stem(file)
        SQ1_filename = f"{dirname}/{stem}_bragg.csv"
        try:
            self.data = np.genfromtxt(SQ1_filename, delimiter=",", skip_header=1)
        except Exception as e:
            print(e)
            return


        self.plot.axes.plot(self.data[:, 0], self.data[:, 2], label="Data",
                            color="k")
        self.plot.axes.plot(self.data[:, 0], self.data[:, 1], label="RMC",
                            color="tab:red", ls="--")

        # Difference
        v_max = np.max(self.data[:, 1:3])
        v_min = np.min(self.data[:, 1:3])
        diff = v_max - v_min
        self.plot.axes.axhline(v_min - 0.1*diff, color="k", ls=":")
        self.plot.axes.plot(self.data[:, 0],
                            self.data[:, 2] - self.data[:, 1] + v_min - 0.1*(diff),
                            color="tab:green")

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
            self.data = np.genfromtxt(filename, delimiter=",", skip_header=1)
        except Exception as e:
            print(e)
            return

        self.plot.axes.plot(self.data[:, 0], self.data[:, 2], label="Data",
                            color="k")
        self.plot.axes.plot(self.data[:, 0], self.data[:, 1], label="RMC",
                            color="tab:red", ls="--")

        # Difference
        v_max = np.max(self.data[:, 1:3])
        v_min = np.min(self.data[:, 1:3])
        diff = v_max - v_min
        self.plot.axes.axhline(v_min - 0.1*diff, color="k", ls=":")
        self.plot.axes.plot(self.data[:, 0],
                            self.data[:, 2] - self.data[:, 1] + v_min - 0.1*(diff),
                            color="tab:green")

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

class Chi2Tab(QWidget):
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
        self.plot.fig.clear()
        dirname, stem = get_dir_and_stem(file)
        filename = f"{dirname}/{stem}.chi2"
        try:
            self.data = np.genfromtxt(filename, skip_header=1)
        except Exception as e:
            print(e)
            return

        header = []
        with open(filename) as f:
            for line in f:
                header = line.replace("\n", "").split(",")
                break


        [ax1, ax2] = self.plot.fig.subplots(1, 2)
        ax1.plot(self.data[:, 1],
              color="k", label="Generated")
        ax1.plot(self.data[:, 2],
              color="tab:blue", ls="--", label="Tested")
        ax1.plot(self.data[:, 0],
              color="tab:green", ls="--", label="Accepted")

        ax1.set_xlabel(r"Index", fontsize=16)
        ax1.set_ylabel(r"Moves", fontsize=16)
        ax1.legend()

        index_log = np.arange(0, len(self.data), 1) + 1
        ax2.plot(index_log, self.data[:, 3], color="k")
        ax2.set_xlabel(r"log(Index)", fontsize=16)
        ax2.set_ylabel(r"$log(\chi^2$)", fontsize=16)
        ax2.set_xscale("log")
        ax2.set_yscale("log")

        self.plot.fig.tight_layout()
        self.plot.update_plot()



class ConfigFileTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)

        self.layout.addWidget(self.editor)

        self.setLayout(self.layout)

    def plot_rmc(self, file):
        self.editor.setText("")
        with open(file) as f:
            contents = f.read()

        self.editor.setText(contents)

class RMC6FTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.editor = QTextEdit()
        self.editor.setReadOnly(True)

    def plot_rmc(self, file):
        self.editor.setText("")
        dirname, stem = get_dir_and_stem(file)
        filename = f"{dirname}/{stem}.rmc6f"
        try:
            with open(filename) as f:
                contents = f.read()
        except Exception as e:
            print(e)
            return


        self.editor.setText(contents)
        self.layout.addWidget(self.editor)

        self.setLayout(self.layout)

