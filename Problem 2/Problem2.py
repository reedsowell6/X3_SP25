import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from parser import load_circuit
from elements import Resistor, Inductor, Capacitor, VoltageSource

ELEMENT_MAP = {
    'resistor':  Resistor,
    'inductor':  Inductor,
    'capacitor': Capacitor,
    'voltage':   VoltageSource,
}

def main():
    app = QApplication(sys.argv)

    # locate the circuit file relative to this script
    base = Path(__file__).parent
    circuit_file = base / 'my_circuit.txt'
    if not circuit_file.exists():
        print(f"Circuit file not found: {circuit_file}")
        sys.exit(1)

    nodes, elems = load_circuit(str(circuit_file))

    scene = QGraphicsScene()

    # draw a small circle for each node
    for n in nodes.values():
        scene.addEllipse(n.x-3, n.y-3, 6, 6)

    # draw each element
    for e in elems:
        cls = ELEMENT_MAP.get(e.type)
        if cls is None:
            print(f"Unknown element type: {e.type}")
            continue
        n1 = nodes[e.from_node]
        n2 = nodes[e.to_node]
        item = cls(n1, n2)
        scene.addItem(item)

    view = QGraphicsView(scene)
    view.setWindowTitle("Circuit Viewer")
    view.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()