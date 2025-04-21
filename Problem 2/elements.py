from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui     import QPainterPath, QPen
from PyQt5.QtCore    import QRectF

class CircuitElement(QGraphicsItem):
    def __init__(self, node1, node2):
        super().__init__()
        self.p1 = node1
        self.p2 = node2
        self.path = QPainterPath()
        self._build_path()

    def boundingRect(self):
        return self.path.boundingRect()

    def paint(self, painter, option, widget):
        painter.setPen(QPen())
        painter.drawPath(self.path)

    def _build_path(self):
        raise NotImplementedError("Subclasses must implement _build_path")

class Resistor(CircuitElement):
    def _build_path(self):
        x1,y1 = self.p1.x, self.p1.y
        x2,y2 = self.p2.x, self.p2.y
        if y1 == y2:
            length = x2 - x1
            zig = 6
            step = length/(zig*2)
            x = x1
            self.path.moveTo(x,y1)
            for i in range(zig*2):
                x += step
                y = y1 + (10 if i%2 else -10)
                self.path.lineTo(x,y)
            self.path.lineTo(x2,y1)
        else:
            length = y2 - y1
            zig = 6
            step = length/(zig*2)
            y = y1
            self.path.moveTo(x1,y)
            for i in range(zig*2):
                y += step
                x = x1 + (10 if i%2 else -10)
                self.path.lineTo(x,y)
            self.path.lineTo(x1,y2)

class Inductor(CircuitElement):
    def _build_path(self):
        x1,y1 = self.p1.x, self.p1.y
        x2,y2 = self.p2.x, self.p2.y
        loops = 4
        r = 10
        if y1 == y2:
            x = x1
            self.path.moveTo(x,y1)
            seg = (x2 - x1 - 2*r*loops)/2
            self.path.lineTo(x+seg, y1)
            x += seg
            for _ in range(loops):
                self.path.arcTo(x, y1-r, 2*r, 2*r, 180, -180)
                x += 2*r
            self.path.lineTo(x+seg, y1)
        else:
            y = y1
            self.path.moveTo(x1,y)
            seg = (y2 - y1 - 2*r*loops)/2
            self.path.lineTo(x1, y+seg)
            y += seg
            for _ in range(loops):
                self.path.arcTo(x1-r, y, 2*r, 2*r, 90, -180)
                y += 2*r
            self.path.lineTo(x1, y+seg)

class Capacitor(CircuitElement):
    def _build_path(self):
        x1,y1 = self.p1.x, self.p1.y
        x2,y2 = self.p2.x, self.p2.y
        gap = 10
        length = abs((x2-x1) if y1==y2 else (y2-y1))
        seg = (length - gap)/2
        line_len = 20
        if y1 == y2:
            self.path.moveTo(x1,y1)
            self.path.lineTo(x1+seg, y1)
            self.path.moveTo(x1+seg, y1-line_len/2)
            self.path.lineTo(x1+seg, y1+line_len/2)
            self.path.moveTo(x2-seg, y1-line_len/2)
            self.path.lineTo(x2-seg, y1+line_len/2)
            self.path.moveTo(x2, y1)
            self.path.lineTo(x2, y2)
        else:
            self.path.moveTo(x1,y1)
            self.path.lineTo(x1, y1+seg)
            self.path.moveTo(x1-line_len/2, y1+seg)
            self.path.lineTo(x1+line_len/2, y1+seg)
            self.path.moveTo(x1-line_len/2, y2-seg)
            self.path.lineTo(x1+line_len/2, y2-seg)
            self.path.moveTo(x1, y2)
            self.path.lineTo(x2, y2)

class VoltageSource(CircuitElement):
    def _build_path(self):
        x1,y1 = self.p1.x, self.p1.y
        x2,y2 = self.p2.x, self.p2.y
        r = 15
        if y1 == y2:
            self.path.moveTo(x1,y1)
            seg = (x2 - x1 - 2*r)/2
            self.path.lineTo(x1+seg, y1)
            self.path.addEllipse(x1+seg, y1-r, 2*r, 2*r)
            self.path.moveTo(x2-seg, y1)
            self.path.lineTo(x2, y2)
        else:
            self.path.moveTo(x1,y1)
            seg = (y2 - y1 - 2*r)/2
            self.path.lineTo(x1, y1+seg)
            self.path.addEllipse(x1-r, y1+seg, 2*r, 2*r)
            self.path.moveTo(x1, y2-seg)
            self.path.lineTo(x2, y2)