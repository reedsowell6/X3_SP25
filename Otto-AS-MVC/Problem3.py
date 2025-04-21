import sys
import numpy as np
from scipy.integrate import quad
from scipy.optimize import fsolve
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Otto cycle model
from Otto import ottoCycleModel
# Air properties
from Air import air, units, StateDataForPlotting

# Diesel cycle model
def dieselCycleModel(p_initial=1e5, V1=1.0, T1=300.0, ratio=18.0, cutoff=2.0):
    units_obj = units()
    a = air()
    a.set(P=p_initial, T=T1)
    a.n = V1 / a.State.v
    S1 = a.set(P=p_initial, T=T1)
    S2 = a.set(v=S1.v/ratio, s=S1.s)
    S3 = a.set(P=S2.P, v=S2.v*cutoff)
    S4 = a.set(v=S1.v, s=S3.s)
    Wc = a.n*(S2.u - S1.u)
    We = a.n*(S3.u - S4.u)
    Qi = a.n*(S3.u - S2.u)
    Eff = (We - Wc)/Qi*100.0
    upper = StateDataForPlotting()
    lower = StateDataForPlotting()
    for v in np.linspace(S1.v, S2.v, 50):
        st = a.set(v=v, s=S1.s)
        lower.add((st.T, st.P, st.u, st.h, st.s, st.v))
    for T in np.linspace(S2.T, S3.T, 50):
        st = a.set(P=S2.P, T=T)
        upper.add((st.T, st.P, st.u, st.h, st.s, st.v))
    for v in np.linspace(S3.v, S4.v, 50):
        st = a.set(v=v, s=S3.s)
        upper.add((st.T, st.P, st.u, st.h, st.s, st.v))
    for T in np.linspace(S4.T, S1.T, 50):
        st = a.set(T=T, v=S1.v)
        upper.add((st.T, st.P, st.u, st.h, st.s, st.v))
    class Model: pass
    model = Model()
    model.units = units_obj
    model.State1, model.State2, model.State3, model.State4 = S1, S2, S3, S4
    model.W_compression, model.W_expansion, model.Q_in, model.Eff = Wc, We, Qi, Eff
    model.lowerCurve, model.upperCurve = lower, upper
    return model

# Main GUI view
class Problem3View(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.units = units()
        self._initUI()

    def _initUI(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        gb_in = QtWidgets.QGroupBox('Cycle Input')
        grid = QtWidgets.QGridLayout(gb_in)
        grid.addWidget(QtWidgets.QLabel('Cycle:'), 0, 0)
        self.comboCycle = QtWidgets.QComboBox(); self.comboCycle.addItems(['Otto','Diesel'])
        grid.addWidget(self.comboCycle, 0, 1)
        grid.addWidget(QtWidgets.QLabel('Units:'), 1, 0)
        self.radioEnglish = QtWidgets.QRadioButton('English'); self.radioEnglish.setChecked(True)
        self.radioMetric = QtWidgets.QRadioButton('Metric')
        hl = QtWidgets.QHBoxLayout(); hl.addWidget(self.radioEnglish); hl.addWidget(self.radioMetric)
        grid.addLayout(hl, 1, 1)
        self.leT1 = self._addRow(grid,'T1 (K/R):','300.0',2)
        self.leP1 = self._addRow(grid,'P1 (Pa/atm):','100000.0',3)
        self.leV1 = self._addRow(grid,'V1 (m^3/ft^3):','1.0',4)
        self.leRatio = self._addRow(grid,'Compression Ratio:','6.0',5)
        self.leThigh = self._addRow(grid,'T_high (K/R):','1500.0',6)
        self.leCutoff = self._addRow(grid,'Cutoff Ratio:','2.0',7)
        self.btnCalc = QtWidgets.QPushButton('Calculate'); grid.addWidget(self.btnCalc,8,0,1,2)
        mainLayout.addWidget(gb_in)
        gb_out = QtWidgets.QGroupBox('Output')
        grid2 = QtWidgets.QGridLayout(gb_out)
        labels = ['T1','T2','T3','T4','Wc','We','Qi','Eff']
        self.outs = []
        for i, lab in enumerate(labels):
            r, c = divmod(i, 2)
            grid2.addWidget(QtWidgets.QLabel(lab+':'), r, c*2)
            le = QtWidgets.QLineEdit(); le.setReadOnly(True)
            grid2.addWidget(le, r, c*2+1)
            self.outs.append(le)
        mainLayout.addWidget(gb_out)
        gb_plot = QtWidgets.QGroupBox('PV')
        vplot = QtWidgets.QVBoxLayout(gb_plot)
        self.fig = Figure(figsize=(5,4)); self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111); vplot.addWidget(self.canvas)
        mainLayout.addWidget(gb_plot)
        self.leCutoff.hide(); gb_in.layout().itemAtPosition(7,0).widget().hide()
        self.show()

    def _addRow(self, layout, label, default, row):
        layout.addWidget(QtWidgets.QLabel(label), row, 0)
        le = QtWidgets.QLineEdit(default); layout.addWidget(le, row, 1)
        return le

    def plotModel(self, m):
        self.ax.clear()
        v1 = m.lowerCurve.getDataCol('v'); p1 = m.lowerCurve.getDataCol('p')
        v2 = m.upperCurve.getDataCol('v'); p2 = m.upperCurve.getDataCol('p')
        self.ax.plot(v1, p1, '-b'); self.ax.plot(v2, p2, '-r')
        u = m.units; self.ax.set_xlabel(f'V ({u.VUnits})'); self.ax.set_ylabel(f'P ({u.PUnits})')
        self.canvas.draw()

    def showResults(self, model):
        SI = self.radioMetric.isChecked(); u = self.units
        Ts = [model.State1.T, model.State2.T, model.State3.T, model.State4.T]
        for i, T in enumerate(Ts): self.outs[i].setText(f"{T if SI else u.CF_T*T:.2f}")
        get_attr = lambda o, names: next((getattr(o, n) for n in names if hasattr(o, n)), 0)
        Wc = get_attr(model, ['W_compression', 'W_Compression'])
        We = get_attr(model, ['W_expansion', 'W_Power'])
        Qi = get_attr(model, ['Q_in', 'Q_In'])
        Eff = model.Eff
        vals = [Wc, We, Qi, Eff]
        for idx, val in enumerate(vals, 4): self.outs[idx].setText(f"{val if (SI or idx==7) else val*u.CF_E:.2f}")
        self.plotModel(model)

class Problem3Controller:
    def __init__(self, view):
        self.view = view
        self.view.comboCycle.currentIndexChanged.connect(self.toggle)
        self.view.btnCalc.clicked.connect(self.calculate)

    def toggle(self):
        isD = self.view.comboCycle.currentText()=='Diesel'
        self.view.leThigh.setVisible(not isD)
        self.view.leCutoff.setVisible(isD)
        grid = self.view.findChild(QtWidgets.QGroupBox).layout()
        grid.itemAtPosition(6,0).widget().setVisible(not isD)
        grid.itemAtPosition(7,0).widget().setVisible(isD)

    def calculate(self):
        SI = self.view.radioMetric.isChecked(); u = self.view.units
        try:
            T1=float(self.view.leT1.text()); P1=float(self.view.leP1.text()); V1=float(self.view.leV1.text()); r=float(self.view.leRatio.text())
            if not SI: T1=u.T_RtoK(T1); P1=P1/u.CF_P; V1=V1/u.CF_V
            if self.view.comboCycle.currentText()=='Otto':
                Th=float(self.view.leThigh.text());
                if not SI: Th=u.T_RtoK(Th)
                model = ottoCycleModel(p_initial=P1, v_cylinder=V1, t_initial=T1, t_high=Th, ratio=r)
                # build Otto PV curves
                a=air()
                model.upperCurve.clear(); model.lowerCurve.clear()
                for v in np.linspace(model.State1.v, model.State2.v, 50):
                    st=a.set(v=v, s=model.State1.s); model.lowerCurve.add((st.T, st.P, st.u, st.h, st.s, st.v))
                for T in np.linspace(model.State2.T, model.State3.T, 50):
                    st=a.set(T=T, v=model.State2.v); model.upperCurve.add((st.T, st.P, st.u, st.h, st.s, st.v))
                for v in np.linspace(model.State3.v, model.State4.v, 50):
                    st=a.set(v=v, s=model.State3.s); model.upperCurve.add((st.T, st.P, st.u, st.h, st.s, st.v))
                for T in np.linspace(model.State4.T, model.State1.T, 50):
                    st=a.set(T=T, v=model.State1.v); model.upperCurve.add((st.T, st.P, st.u, st.h, st.s, st.v))
            else:
                rc=float(self.view.leCutoff.text())
                model=dieselCycleModel(p_initial=P1, V1=V1, T1=T1, ratio=r, cutoff=rc)
            model.units.SI = SI
            self.view.showResults(model)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self.view, 'Error', str(e))

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    view = Problem3View()
    controller = Problem3Controller(view)
    sys.exit(app.exec_())
