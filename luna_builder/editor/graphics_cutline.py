from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLCutLine(QtWidgets.QGraphicsItem):
    def __init__(self, parent=None):
        super(QLCutLine, self).__init__(parent)

        self.line_points = []
        self._pen = QtGui.QPen(QtCore.Qt.white)
        self._pen.setWidthF(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):

        if len(self.line_points) > 1:
            path = QtGui.QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QtGui.QPainterPath(QtCore.QPointF(0.0, 0.0))
            path.lineTo(QtCore.QPointF(1.0, 1.0))
        return path

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QtGui.QPolygonF(self.line_points)
        painter.drawPolyline(poly)
