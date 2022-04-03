import imp
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from luna import Logger
import luna.utils.enumFn as enumFn
import luna_builder.editor.node_edge_dragging as node_edge_dragging
import luna_builder.editor.node_edge as node_edge
import luna_builder.editor.node_socket as node_socket
import luna_builder.editor.graphics_socket as graphics_socket
import luna_builder.editor.graphics_node as graphics_node
import luna_builder.editor.graphics_edge as graphics_edge
import luna_builder.editor.graphics_cutline as graphics_cutline
imp.reload(node_socket)


class QLGraphicsView(QtWidgets.QGraphicsView):

    # Constant settings
    EDGE_DRAG_START_THRESHOLD = 50
    HIGH_QUALITY_ZOOM = 4

    class EdgeMode(enumFn.Enum):
        NOOP = 1
        DRAG = 2
        CUT = 3

    def __init__(self, gr_scene, parent=None):
        super(QLGraphicsView, self).__init__(parent)

        # Flags
        self.is_view_dragging = False

        self.gr_scene = gr_scene
        self.zoom_in_factor = 1.25
        self.zoom_clamp = True
        self.zoom = 10
        self.zoom_step = 1
        self.zoom_range = (-5.0, 10.0)

        self.last_lmb_click_pos = QtCore.QPointF(0.0, 0.0)
        self.last_scene_mouse_pos = QtCore.QPointF(0.0, 0.0)
        self.rubberband_dragging_rect = False

        self.edge_mode = QLGraphicsView.EdgeMode.NOOP
        self.dragging = node_edge_dragging.EdgeDrag(self)

        # Cutline
        self.cutline = graphics_cutline.QLCutLine()
        self.gr_scene.addItem(self.cutline)

        self.init_ui()
        self.setScene(self.gr_scene)
        self.update_render_hints()
        self.update_edge_width()

    def init_ui(self):
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        # Enable dropping
        self.setAcceptDrops(True)

    @property
    def scene(self):
        return self.gr_scene.scene

    def update_render_hints(self):
        if self.zoom > self.HIGH_QUALITY_ZOOM:
            self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)
        else:
            self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)

    # =========== Qt Events overrides =========== #

    def dragEnterEvent(self, event):
        self.scene.signals.item_drag_entered.emit(event)

    def dropEvent(self, event):
        self.scene.signals.item_dropped.emit(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middle_mouse_press(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_mouse_press(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_mouse_press(event)
        else:
            super(QLGraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.middle_mouse_release(event)
        elif event.button() == QtCore.Qt.LeftButton:
            self.left_mouse_release(event)
        elif event.button() == QtCore.Qt.RightButton:
            self.right_mouse_release(event)
        else:
            super(QLGraphicsView, self).mouseReleaseEvent(event)

    def wheelEvent(self, event):
        zoom_out_factor = 1.0 / self.zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = self.zoom_in_factor
            self.zoom += self.zoom_step
        else:
            zoom_factor = zoom_out_factor
            self.zoom -= self.zoom_step

        clamped = False
        if self.zoom < self.zoom_range[0]:
            self.zoom, clamped = self.zoom_range[0], True
        if self.zoom > self.zoom_range[1]:
            self.zoom, clamped = self.zoom_range[1], True

        # Set actual scale
        if not clamped or not self.zoom_clamp:
            self.scale(zoom_factor, zoom_factor)
            self.update_edge_width()
            self.update_render_hints()

    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        self.is_view_dragging = not self.isInteractive()

        try:
            if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
                pos = scene_pos
                pos.setX(pos.x() - 1.0)
                self.dragging.update_positions(pos.x(), pos.y())

            if self.edge_mode == QLGraphicsView.EdgeMode.CUT and self.cutline is not None:
                self.cutline.line_points.append(scene_pos)
                self.cutline.update()

        except Exception:
            Logger.exception('mouseMoveEvent exception')

        self.last_scene_mouse_pos = scene_pos

        super(QLGraphicsView, self).mouseMoveEvent(event)

    # =========== Handling button presses =========== #
    def middle_mouse_press(self, event):
        item = self.get_item_at_click(event)
        if event.modifiers() & QtCore.Qt.ControlModifier:
            self.log_scene_objects(item)

    def middle_mouse_release(self, event):
        pass

    def left_mouse_press(self, event):

        item = self.get_item_at_click(event)
        # Store click position for future use
        self.last_lmb_click_pos = self.mapToScene(event.pos())

        # Handle socket click
        if isinstance(item, graphics_socket.QLGraphicsSocket):
            if self.edge_mode == QLGraphicsView.EdgeMode.NOOP:
                self.edge_mode = QLGraphicsView.EdgeMode.DRAG
                self.dragging.start_edge_drag(item)
                return

        if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
            result = self.dragging.end_edge_drag(item)
            if result:
                return

        if not item:
            if event.modifiers() & QtCore.Qt.ControlModifier:
                self.edge_mode = QLGraphicsView.EdgeMode.CUT
                fake_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                               QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
                super(QLGraphicsView, self).mouseReleaseEvent(fake_event)
                return
            else:
                self.rubberband_dragging_rect = True

        super(QLGraphicsView, self).mousePressEvent(event)

    def left_mouse_release(self, event):
        item = self.get_item_at_click(event)

        try:
            if self.edge_mode == QLGraphicsView.EdgeMode.DRAG:
                if self.check_lmb_release_delta(event):
                    result = self.dragging.end_edge_drag(item)
                    if result:
                        return

            if self.edge_mode == QLGraphicsView.EdgeMode.CUT:
                self.cut_intersecting_edges()
                self.cutline.line_points = []
                self.cutline.update()
                self.edge_mode = QLGraphicsView.EdgeMode.NOOP
                return

            if self.rubberband_dragging_rect:
                self.rubberband_dragging_rect = False
                self.scene.on_selection_change()
                return

        except Exception:
            Logger.exception('Left mouse release exception')

        super(QLGraphicsView, self).mouseReleaseEvent(event)

    def right_mouse_press(self, event):
        releaseEvent = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                         QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
        super(QLGraphicsView, self).mouseReleaseEvent(releaseEvent)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setInteractive(False)
        fake_event = QtGui.QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                       QtCore.Qt.LeftButton, event.buttons() | QtCore.Qt.LeftButton, event.modifiers())
        super(QLGraphicsView, self).mousePressEvent(fake_event)

    def right_mouse_release(self, event):
        fake_event = QtGui.QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                       QtCore.Qt.LeftButton, event.buttons() & ~QtCore.Qt.LeftButton, event.modifiers())
        super(QLGraphicsView, self).mouseReleaseEvent(fake_event)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setInteractive(True)

    # =========== Supporting methods =========== #
    def reset_edge_mode(self):
        self.edge_mode = QLGraphicsView.EdgeMode.NOOP

    def update_edge_width(self):
        graphics_edge.QLGraphicsEdge.WIDTH = ((self.zoom - self.zoom_range[0]) / (self.zoom_range[1] - self.zoom_range[0])) * \
            (graphics_edge.QLGraphicsEdge.MIN_WIDTH - graphics_edge.QLGraphicsEdge.MAX_WIDTH) + graphics_edge.QLGraphicsEdge.MAX_WIDTH

    def get_item_at_click(self, event):
        """Object at click event position

        :param event: Mouse click event
        :type event: QMouseEvent
        :return: Item clicked
        :rtype: QtWidgets.QGraphicsItem
        """
        item = self.itemAt(event.pos())  # type: QtWidgets.QGraphicsItem
        return item

    def check_lmb_release_delta(self, event):
        """Measures if LMB release position is greater then distance threshold.

        :param event: Left mouse click event
        :type event: QMouseEvent
        :return: Distance between clicked release positions is greater than threshold
        :rtype: bool
        """
        # Check if mouse was moved far enough from start socket and handle release if true
        new_lmb_releas_scene_pos = self.mapToScene(event.pos())
        click_release_delta = new_lmb_releas_scene_pos - self.last_lmb_click_pos
        return (click_release_delta.x() ** 2 + click_release_delta.y() ** 2) > QLGraphicsView.EDGE_DRAG_START_THRESHOLD ** 2

    def log_scene_objects(self, item):
        if isinstance(item, graphics_socket.QLGraphicsSocket):
            Logger.debug(item.socket)
            Logger.debug('  Data Class: {0}'.format(item.socket.data_class))
            Logger.debug('  Value: {0}'.format(item.socket.value()))
            Logger.debug('  Connected edge: {0}'.format(item.socket.edges))
        elif isinstance(item, graphics_node.QLGraphicsNode):
            Logger.debug(item.node)
            Logger.debug('-- Inputs')
            for insocket in item.node.inputs:
                Logger.debug(insocket)
            Logger.debug('-- Required Inputs')
            for insocket in item.node._required_inputs:
                Logger.debug(insocket)
            Logger.debug('-- Outputs')
            for outsocket in item.node.outputs:
                Logger.debug(outsocket)
        elif isinstance(item, graphics_edge.QLGraphicsEdge):
            Logger.debug(item.edge)
            Logger.debug('  Start: {0}, End:{1}'.format(item.edge.start_socket, item.edge.end_socket))

        if not item:
            Logger.debug('SCENE:')
            Logger.debug('VARS: {0}'.format(self.scene.vars._vars))
            Logger.debug('  Nodes:')
            for node in self.gr_scene.scene.nodes:
                Logger.debug('    {0}'.format(node))
            Logger.debug('  Edges:')
            for edge in self.gr_scene.scene.edges:
                Logger.debug('    {0}'.format(edge))

    def debug_modifiers(self, event):
        """Helper function get string if we hold Ctrl, Shift or Alt modifier keys"""
        out = "MODS: "
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            out += "SHIFT "
        if event.modifiers() & QtCore.Qt.ControlModifier:
            out += "CTRL "
        if event.modifiers() & QtCore.Qt.AltModifier:
            out += "ALT "
        Logger.debug(out)

    def cut_intersecting_edges(self):
        cut_result = False
        for ix in range(len(self.cutline.line_points) - 1):
            pt1 = self.cutline.line_points[ix]
            pt2 = self.cutline.line_points[ix + 1]

            # TODO: Should be optimized as gets slow with large scenes
            for edge in self.scene.edges[:]:
                if edge.gr_edge.intersects_with(pt1, pt2):
                    edge.remove()
                    cut_result = True
        if cut_result:
            self.scene.history.store_history('Edges cut', set_modified=True)
