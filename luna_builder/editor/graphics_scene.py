import math
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class QLGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, scene, parent=None):
        super(QLGraphicsScene, self).__init__(parent)
        self.scene = scene

        # Settings
        self.grid_size = 20
        self.grid_squares = 5
        self.scene_width = self.scene_height = 64000
        # Colors
        self._color_background = QtGui.QColor("#393939")
        self._color_light = QtGui.QColor("#2f2f2f")
        self._color_dark = QtGui.QColor("#292929")
        self._pen_light = QtGui.QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QtGui.QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

    # ======== Events ========= #
    def dragMoveEvent(self, event):
        # Disable parent event
        pass

    # ======== Methods ========= #

    def set_scene_size(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super(QLGraphicsScene, self).drawBackground(painter, rect)
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        firt_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # Compute line drawing
        lines_light, lines_dark = [], []
        for x in range(firt_left, right, self.grid_size):
            if (x % (self.grid_size * self.grid_squares)):
                lines_light.append(QtCore.QLine(x, top, x, bottom))
            else:
                lines_dark.append(QtCore.QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if (y % (self.grid_size * self.grid_squares)):
                lines_light.append(QtCore.QLine(left, y, right, y))
            else:
                lines_dark.append(QtCore.QLine(left, y, right, y))

        # Draw lines
        painter.setPen(self._pen_light)
        painter.drawLines(lines_light)
        painter.setPen(self._pen_dark)
        painter.drawLines(lines_dark)
