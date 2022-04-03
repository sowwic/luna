from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger


class QLGraphicsEdge(QtWidgets.QGraphicsPathItem):

    MAX_WIDTH = 6.0
    MIN_WIDTH = 2.0
    WIDTH = 2.0

    def __init__(self, edge, parent=None):
        super(QLGraphicsEdge, self).__init__(parent)
        self.edge = edge

        # Init flags

        # Init variables
        self.source_position = [0, 0]
        self.destination_position = [200, 100]

        self.init_assets()
        self.init_ui()

    def init_ui(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

    def init_assets(self):
        # Colors and pens
        self._color = QtGui.QColor("#001000")
        self._color_selected = QtGui.QColor("#00ff00")
        self._pen = QtGui.QPen(self._color)
        self._pen_selected = QtGui.QPen(self._color_selected)
        self._pen_dragging = QtGui.QPen(self._color)
        self._pen_dragging.setStyle(QtCore.Qt.DashLine)
        self._pen_selected.setWidthF(3.0)
        self._pen_dragging.setWidthF(2.0)

    # ======== Events ======= #

    # def mouseReleaseEvent(self, event):
    #     super(QLGraphicsEdge, self).mouseReleaseEvent(event)

    # ======== Methods ======= #

    def set_source(self, x, y):
        self.source_position = [x, y]

    def set_destination(self, x, y):
        self.destination_position = [x, y]

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calc_path()

    def paint(self, painter, widget=None, options=None):
        self.setPath(self.calc_path())
        self._pen.setWidthF(self.WIDTH)

        if self.edge.end_socket and self.edge.start_socket:
            self._pen.setColor(self.edge.start_socket.gr_socket._color_background)

        if not self.edge.end_socket or not self.edge.start_socket:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(self.path())

    def calc_path(self):
        """Handle path drawing from point A to point B"""
        raise NotImplementedError("This method has to be overriden in a derived class")

    def intersects_with(self, pt1, pt2):
        cutpath = QtGui.QPainterPath(pt1)
        cutpath.lineTo(pt2)
        path = self.calc_path()
        return cutpath.intersects(path)


class QLGraphicsEdgeDirect(QLGraphicsEdge):
    def calc_path(self):
        path = QtGui.QPainterPath(QtCore.QPointF(*self.source_position))
        path.lineTo(*self.destination_position)
        return path


class QLGraphicsEdgeBezier(QLGraphicsEdge):
    def calc_path(self):
        distance = (self.destination_position[0] - self.source_position[0]) * 0.5
        if self.source_position[0] > self.destination_position[0]:
            distance *= -1
        ctl_point1 = [self.source_position[0] + distance, self.source_position[1]]
        ctl_point2 = [self.destination_position[0] - distance, self.destination_position[1]]

        path = QtGui.QPainterPath(QtCore.QPointF(*self.source_position))
        path.cubicTo(QtCore.QPointF(*ctl_point1), QtCore.QPointF(*ctl_point2), QtCore.QPointF(*self.destination_position))
        return path


class QLGraphicsEdgeSquare(QLGraphicsEdge):

    HANDLE_WEIGHT = 0.5

    def calc_path(self):
        mid_x = self.source_position[0] + ((self.destination_position[0] - self.source_position[0]) * self.HANDLE_WEIGHT)

        path = QtGui.QPainterPath(QtCore.QPointF(*self.source_position))
        path.lineTo(mid_x, self.source_position[1])
        path.lineTo(mid_x, self.destination_position[1])
        path.lineTo(*self.destination_position)
        return path
