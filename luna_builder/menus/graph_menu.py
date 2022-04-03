from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import luna.utils.pysideFn as pysideFn
import luna_builder.editor.node_edge as node_edge


class GraphMenu(QtWidgets.QMenu):
    def __init__(self, main_window, parent=None):
        super(GraphMenu, self).__init__("&Graph", parent)
        self.main_window = main_window

        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    @property
    def executor(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.scene.executor

    @property
    def node_scene(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.scene

    @property
    def gr_view(self):
        editor = self.main_window.current_editor
        if not editor:
            return None
        return editor.gr_view

    def create_actions(self):
        # Edge type
        # TODO: Possibly automate?
        self.edge_type_group = QtWidgets.QActionGroup(self)
        self.edge_type_bezier_action = QtWidgets.QAction('Bezier', self)
        self.edge_type_direct_action = QtWidgets.QAction('Direct', self)
        self.edge_type_square_action = QtWidgets.QAction('Square', self)

        self.edge_type_group.addAction(self.edge_type_direct_action)
        self.edge_type_group.addAction(self.edge_type_bezier_action)
        self.edge_type_group.addAction(self.edge_type_square_action)

        self.edge_type_bezier_action.setCheckable(True)
        self.edge_type_direct_action.setCheckable(True)
        self.edge_type_square_action.setCheckable(True)
        # Execution
        self.reset_stepped_execution = QtWidgets.QAction("&Reset stepped execution", self)
        self.execute_step_action = QtWidgets.QAction("&Execute Step", self)
        self.execute_action = QtWidgets.QAction(pysideFn.get_QIcon('execute.png'), "&Execute", self)

        self.execute_step_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F6))
        self.execute_action.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_F5))

    def create_connections(self):
        self.main_window.mdi_area.subWindowActivated.connect(self.update_actions_state)
        self.aboutToShow.connect(self.update_actions_state)
        # Edge type
        self.scene_edge_type_menu.aboutToShow.connect(self.update_edge_type_menu)
        self.edge_type_direct_action.toggled.connect(self.on_direct_edge_toggled)
        self.edge_type_bezier_action.toggled.connect(self.on_bezier_edge_toggled)
        self.edge_type_square_action.toggled.connect(self.on_square_edge_toggled)

        # Actions
        self.reset_stepped_execution.triggered.connect(self.on_reset_stepped_execution)
        self.execute_step_action.triggered.connect(self.on_execute_step)
        self.execute_action.triggered.connect(self.on_execute)

    def create_sub_menus(self):
        self.scene_edge_type_menu = QtWidgets.QMenu("Edge style")

    def populate(self):
        self.addMenu(self.scene_edge_type_menu)
        self.scene_edge_type_menu.addAction(self.edge_type_direct_action)
        self.scene_edge_type_menu.addAction(self.edge_type_bezier_action)
        self.scene_edge_type_menu.addAction(self.edge_type_square_action)

        self.addSection('Execution')
        self.addAction(self.reset_stepped_execution)
        self.addAction(self.execute_step_action)
        self.addSeparator()
        self.addAction(self.execute_action)

    def update_actions_state(self):
        is_scene_set = self.node_scene is not None
        self.scene_edge_type_menu.setEnabled(is_scene_set)
        self.reset_stepped_execution.setEnabled(is_scene_set)
        self.execute_step_action.setEnabled(is_scene_set)
        self.execute_action.setEnabled(is_scene_set)

    def update_edge_type_menu(self):
        if not self.main_window.current_editor:
            self.edge_type_bezier_action.setEnabled(False)
            self.edge_type_direct_action.setEnabled(False)
            self.edge_type_square_action.setEnabled(False)
            return

        self.edge_type_bezier_action.setEnabled(True)
        self.edge_type_direct_action.setEnabled(True)
        self.edge_type_square_action.setEnabled(True)
        if self.node_scene.edge_type == node_edge.Edge.Type.BEZIER:
            self.edge_type_bezier_action.setChecked(True)
        elif self.node_scene.edge_type == node_edge.Edge.Type.DIRECT:
            self.edge_type_direct_action.setChecked(True)
        if self.node_scene.edge_type == node_edge.Edge.Type.SQUARE:
            self.edge_type_square_action.setChecked(True)

    def on_bezier_edge_toggled(self, state):
        if not self.main_window.current_editor or not state:
            return
        self.node_scene.edge_type = node_edge.Edge.Type.BEZIER

    def on_direct_edge_toggled(self, state):
        if not self.main_window.current_editor or not state:
            return
        self.node_scene.edge_type = node_edge.Edge.Type.DIRECT

    def on_square_edge_toggled(self, state):
        if not self.main_window.current_editor or not state:
            return
        self.node_scene.edge_type = node_edge.Edge.Type.SQUARE

    def on_execute(self):
        if self.executor is not None:
            self.executor.execute_graph()

    def on_execute_step(self):
        if self.executor is not None:
            self.executor.execute_step()

    def on_reset_stepped_execution(self):
        if self.executor is not None:
            self.executor.reset_stepped_execution()
