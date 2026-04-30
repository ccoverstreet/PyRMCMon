from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import  QWidget, QVBoxLayout

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

    def clear_plot(self):
        self.axes.clear()
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.update_plot()
