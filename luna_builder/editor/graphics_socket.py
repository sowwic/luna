from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore

from luna import Logger
from luna import Config
from luna import BuilderVars


class QLGraphicsSocket(QtWidgets.QGraphicsItem):

    TEXT_ZOOM_OUT_LIMIT = 2
    SOCKET_ZOOM_OUT_LIMIT = 2

    def __init__(self, socket):
        self.socket = socket
        super(QLGraphicsSocket, self).__init__(socket.node.gr_node)

        self.init_sizes()
        self.init_assets()
        self.init_inner_classes()

    def init_sizes(self):
        self.radius = 6.0
        self.empty_radius = 3.0
        self.outline_width = 1.0

    def init_assets(self):
        self._color_empty = QtGui.QColor('#141413')
        self._color_background = self.socket.data_type.get('color')
        self._color_outline = QtGui.QColor("#FF000000")
        self._pen = QtGui.QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QtGui.QBrush(self._color_background)
        self._brush_empty = QtGui.QBrush(self._color_empty)
        self._label_font = QtGui.QFont(*Config.get(BuilderVars.socket_font, default=['Roboto', 10], cached=True))

    def init_inner_classes(self):
        self.init_label()

    def init_label(self):
        # Add text label
        self.text_item = QtWidgets.QGraphicsTextItem(self.socket.label, parent=self)
        self.text_item.setFont(self._label_font)
        if self.socket.node_position in [self.socket.Position.RIGHT_TOP, self.socket.Position.RIGHT_BOTTOM]:
            self.align_text_right()

    def paint(self, painter, option=None, widget=None):
        self.text_item.setVisible(self.socket.node.scene.view.zoom > self.TEXT_ZOOM_OUT_LIMIT)
        if self.socket.node.scene.view.zoom < self.SOCKET_ZOOM_OUT_LIMIT:
            return
        # Update background color
        self._brush.setColor(self._color_background)

        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        if not self.socket.has_edge():
            painter.setBrush(self._brush_empty)
            painter.drawEllipse(-self.empty_radius, -self.empty_radius, 2 * self.empty_radius, 2 * self.empty_radius)

    def boundingRect(self):
        return QtCore.QRectF(
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width)
        )

    def align_text_right(self):
        fmt = QtGui.QTextBlockFormat()
        fmt.setAlignment(QtCore.Qt.AlignRight)
        cursor = self.text_item.textCursor()  # type: QtGui.QTextCursor
        cursor.select(QtGui.QTextCursor.Document)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        self.text_item.setTextCursor(cursor)
