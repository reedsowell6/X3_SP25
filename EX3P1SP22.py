# EX3P1SP22.py

import sys
import numpy as np
from scipy.integrate import solve_ivp

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton
)
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui   as qtg

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)

from Problem1 import Ui_Form  # your auto‑gen UI

class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 1) create the input fields + simulate button
        self._create_input_fields()

        # 2) load the circuit picture
        self._setupImageLabel()

        # 3) set up the matplotlib canvas & toolbar
        self._setup_plot_canvas()

        self.show()

    def _create_input_fields(self):
        """
        Add 6 labeled QLineEdits in the grid for R, L, C, amplitude, frequency, phase,
        plus a 'Simulate' button.
        """
        labels = ['R (Ω):', 'L (H):', 'C (F):',
                  'Amplitude (V):', 'Frequency (rad/s):', 'Phase (rad):']
        defaults = ['10', '20', '0.05', '20', '20', '0']

        self.edits = {}
        for row, (text, default) in enumerate(zip(labels, defaults)):
            lbl  = QLabel(text)
            edit = QLineEdit(default)
            self.layout_GridInput.addWidget(lbl,  row, 0)
            self.layout_GridInput.addWidget(edit, row, 1)
            self.edits[text] = edit

        # simulate button spans both columns
        self.btn_sim = QPushButton("Simulate")
        self.layout_GridInput.addWidget(self.btn_sim, len(labels), 0, 1, 2)
        self.btn_sim.clicked.connect(self._run_simulation)

    def _setupImageLabel(self):
        """
        Load your circuit PNG into a QLabel and put it
        right below the inputs in the same grid.
        """
        pix = qtg.QPixmap("Circuit1.png")
        img = qtw.QLabel()
        img.setPixmap(pix)
        # place it one row below the simulate button:
        self.layout_GridInput.addWidget(img, len(self.edits)+1, 0, 1, 2)

    def _setup_plot_canvas(self):
        """
        Create a Matplotlib FigureCanvas + NavigationToolbar
        and add them below the groupbox in the main layout.
        """
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # verticalLayout is the top‑level layout in your Form
        self.verticalLayout.addWidget(self.toolbar)
        self.verticalLayout.addWidget(self.canvas)

    def _run_simulation(self):
        """
        Read parameters, solve the ODE, compute i1/i2, and redraw plot.
        """
        # 1) grab values
        R     = float(self.edits['R (Ω):'].text())
        L     = float(self.edits['L (H):'].text())
        C     = float(self.edits['C (F):'].text())
        A     = float(self.edits['Amplitude (V):'].text())
        ω     = float(self.edits['Frequency (rad/s):'].text())
        ϕ     = float(self.edits['Phase (rad):'].text())

        # 2) define input voltage and the ODE system
        def v_in(t):
            return A * np.sin(ω*t + ϕ)

        def ode(t, y):
            iL, vC = y
            diL = (v_in(t) - vC)/L
            dvC = (iL - vC/R)/C
            return [diL, dvC]

        # 3) simulate
        t_eval = np.linspace(0, 10, 1000)
        sol = solve_ivp(ode, (0, 10), [0, 0], t_eval=t_eval)

        t   = sol.t
        iL  = sol.y[0]
        vC  = sol.y[1]
        i1  = vC/R
        i2  = iL - i1

        # 4) redraw
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(t, i1, label='i₁ (through R)')
        ax.plot(t, i2, label='i₂ (through C)')
        ax.plot(t, vC, label='v_C (capacitor voltage)')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Current (A) / Voltage (V)')
        ax.legend()
        ax.grid(True)

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
