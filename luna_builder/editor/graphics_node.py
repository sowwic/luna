from luna import Logger
from luna import Config
from luna import BuilderVars
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLGraphicsTitle(QtWidgets.QGraphicsTextItem):

    @property
    def height(self):
        return self.boundingRect().height()

    @property
    def width(self):
        return self.boundingRect().width()

    def __init__(self, gr_node, text='', is_editable=False):
        super(QLGraphicsTitle, self).__init__(text, gr_node)
        self.gr_node = gr_node
        self.is_editable = is_editable

    def edit(self):
        line_edit = QtWidgets.QLineEdit()
        line_edit_proxy = QtWidgets.QGraphicsProxyWidget(self)
        line_edit_proxy.setWidget(line_edit)
        line_edit.editingFinished.connect(lambda: self.apply_edit(line_edit.text()))
        line_edit.editingFinished.connect(line_edit_proxy.deleteLater)
        line_edit.setFont(self.font())

        line_edit.setMaximumWidth(self.gr_node.width)
        line_edit.setText(self.toPlainText())
        line_edit.setFocus(QtCore.Qt.MouseFocusReason)

    def apply_edit(self, new_text):
        new_text = new_text.strip()
        if new_text == self.gr_node.title:
            return
        self.gr_node.node.signals.title_edited.emit(new_text)


class QLGraphicsNode(QtWidgets.QGraphicsItem):

    TEXT_ZOOM_OUT_LIMIT = 2

    def __init__(self, node, parent=None):
        super(QLGraphicsNode, self).__init__(parent)
        self.node = node

        # Init flags
        self._was_moved = False

        self.init_sizes()
        self.init_assets()

        self.init_ui()

    def init_ui(self):
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)

        self.init_title()
        self.init_content()

    @property
    def title(self):
        return self.title_item.toPlainText()

    @title.setter
    def title(self, value):
        self.title_item.setPlainText(value)

    @property
    def title_height(self):
        return self.title_item.height

    @property
    def title_width(self):
        return self.title_item.width

    @property
    def title_color(self):
        return QtGui.QColor(self.node.TITLE_COLOR) if not isinstance(self.node.TITLE_COLOR, QtGui.QColor) else self.node.TITLE_COLOR

    def init_sizes(self):
        self.width = self.node.MIN_WIDTH
        self.height = self.node.MIN_HEIGHT
        self.one_side_horizontal_padding = 20.0
        self.edge_roundness = 10.0
        self.edge_padding = 10.0
        self.title_horizontal_padding = 4.0
        self.title_vertical_padding = 4.0
        self.lower_padding = 8.0

    def init_assets(self):
        # Fonts colors
        self._title_color = QtCore.Qt.white
        self._title_font = QtGui.QFont(*Config.get(BuilderVars.title_font, default=['Roboto', 10], cached=True))
        self._title_font.setBold(True)

        # Pens, Brushes
        self._pen_default = QtGui.QPen(QtGui.QColor("#7F000000"))
        self._pen_selected = QtGui.QPen(QtGui.QColor("#FFA637"))
        self._brush_background = QtGui.QBrush(QtGui.QColor("#E3212121"))
        self._brush_title = QtGui.QBrush(self.title_color)

    def init_title(self):
        self.title_item = QLGraphicsTitle(self, is_editable=self.node.TITLE_EDITABLE)
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self.title_horizontal_padding, 0)

    def init_content(self):
        pass

    def paint(self, painter, option, widget=None):
        self.title_item.setVisible(self.node.scene.view.zoom > self.TEXT_ZOOM_OUT_LIMIT)

        # title
        path_title = QtGui.QPainterPath()
        path_title.setFillRule(QtCore.Qt.WindingFill)
        path_title.addRoundedRect(0, 0, self.width, self.title_height, self.edge_roundness, self.edge_roundness)
        path_title.addRect(0, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        path_title.addRect(self.width - self.edge_roundness, self.title_height - self.edge_roundness, self.edge_roundness, self.edge_roundness)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QtGui.QPainterPath()
        path_content.setFillRule(QtCore.Qt.WindingFill)
        path_content.addRoundedRect(0, self.title_height, self.width, self.height - self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(0, self.title_height, self.edge_roundness, self.edge_roundness)
        path_content.addRect(self.width - self.edge_roundness, self.title_height, self.edge_roundness, self.edge_roundness)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())

        # outline
        # TODO: Paint prominent outline if exec input is connected
        path_outline = QtGui.QPainterPath()
        path_outline.addRoundedRect(-1, -1, self.width + 2, self.height + 2, self.edge_roundness, self.edge_roundness)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(path_outline.simplified())

    def boundingRect(self):
        return QtCore.QRectF(0,
                             0,
                             self.width,
                             self.height).normalized()

    # Events
    def mouseMoveEvent(self, event):
        super(QLGraphicsNode, self).mouseMoveEvent(event)
        for node in self.scene().scene.selected_nodes:
            node.update_connected_edges()
        self._was_moved = True

    def mouseReleaseEvent(self, event):
        super(QLGraphicsNode, self).mouseReleaseEvent(event)
        if self._was_moved:
            self._was_moved = False
            self.node.scene.history.store_history('Node moved', set_modified=True)
