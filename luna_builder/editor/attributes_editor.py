from luna import Logger
from PySide2 import QtWidgets
import luna_builder.editor.node_scene_vars as node_scene_vars


class AttributesEditor(QtWidgets.QWidget):
    def __init__(self, main_window, parent=None):
        super(AttributesEditor, self).__init__(parent)
        self.main_window = main_window
        self._current_widget = None  # type: QtWidgets.QWidget
        self.setMinimumWidth(250)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    @property
    def current_editor(self):
        return self.main_window.current_editor

    @property
    def current_widget(self):
        return self._current_widget

    @current_widget.setter
    def current_widget(self, widget):
        self._current_widget = widget
        self.main_layout.addWidget(self._current_widget)
        self._current_widget.show()

    def update_current_node_widget(self):
        self.clear()
        if not self.main_window.current_editor:
            return

        selected = self.current_editor.scene.selected_nodes
        if not selected:
            return

        node = selected[-1]
        widget = node.get_attrib_widget()
        if widget:
            self.current_widget = widget

    def update_current_var_widget(self, list_item):
        self.clear()
        if not list_item or not self.current_editor:
            return
        var_widget = node_scene_vars.VarAttribWidget(list_item, self.current_editor.scene)
        self.current_widget = var_widget
        var_widget.data_type_switched.connect(self.update_current_var_widget)

    def clear(self):
        if self.current_widget:
            self.main_layout.removeWidget(self.current_widget)
            self.current_widget.close()
            self.current_widget.deleteLater()
            self._current_widget = None
