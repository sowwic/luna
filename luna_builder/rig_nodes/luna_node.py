
from PySide2 import QtCore
from PySide2 import QtGui
import luna.static.directories as directories
import luna_builder.editor.node_node as node_node
import luna_builder.editor.graphics_node as graphics_node


class LunaGraphicsNode(graphics_node.QLGraphicsNode):

    ICON_DRAW_ZOOM_LIMIT = 2

    def init_assets(self):
        super(LunaGraphicsNode, self).init_assets()
        self.status_icons = QtGui.QImage(directories.get_icon_path('status_icons.png'))

    def paint(self, painter, option, widget=None):
        super(LunaGraphicsNode, self).paint(painter, option, widget=widget)
        if self.node.scene.view.zoom < self.ICON_DRAW_ZOOM_LIMIT:
            return

        if self.node.is_invalid():
            icon_offset = 48.0
            self.paint_status_icon(painter, icon_offset)

        elif self.node.STATUS_ICON or self.node.IS_EXEC:
            icon_offset = 24.0
            if not self.node.is_compiled():
                icon_offset = 0.0
            self.paint_status_icon(painter, icon_offset)

    def paint_status_icon(self, painter, offset):
        painter.drawImage(
            QtCore.QRectF(-13.0, -13.0, 24.0, 24.0),
            self.status_icons,
            QtCore.QRectF(offset, 0, 24.0, 24.0)
        )


class LunaNode(node_node.Node):

    GRAPHICS_CLASS = LunaGraphicsNode
    ICON = None
    STATUS_ICON = True
    DEFAULT_TITLE = 'Luna Node'
    TITLE_EDITABLE = False
    UNIQUE = False
    CATEGORY = 'Utils'
