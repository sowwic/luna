import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
import luna_rig
import luna.interface.shared_widgets as shared_widgets
import luna.utils.pysideFn as pysideFn


class CustomSpaceTool(QtWidgets.QDialog):

    INSTANCE = None  # type: CustomSpaceTool
    GEOMETRY = None

    def closeEvent(self, event):
        CustomSpaceTool.GEOMETRY = self.saveGeometry()
        super(CustomSpaceTool, self).closeEvent(event)

    def __init__(self, parent=pysideFn.maya_main_window()):
        super(CustomSpaceTool, self).__init__(parent)
        self.setWindowTitle("Custom space tool")
        self.setProperty("saveWindowPref", True)
        self.resize(400, 200)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Post init
        self.restoreGeometry(CustomSpaceTool.GEOMETRY)

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = cls()
        cls.INSTANCE.restoreGeometry(cls.GEOMETRY)
        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show()
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    def create_widgets(self):
        self.control_field = shared_widgets.StringFieldWidget("Control:", button_text="Set")
        self.space_obj_field = shared_widgets.StringFieldWidget("Space object:", button_text="Set")
        self.space_name_field = shared_widgets.StringFieldWidget("Name:", button=False)
        self.add_space_button = QtWidgets.QPushButton("Add")
        self.method_combobox = QtWidgets.QComboBox()
        self.update_methods_list()

    def create_layouts(self):
        spaces_layout = QtWidgets.QVBoxLayout()
        spaces_layout.addWidget(self.space_name_field)
        spaces_layout.addWidget(self.control_field)
        spaces_layout.addWidget(self.space_obj_field)

        methods_layout = QtWidgets.QHBoxLayout()
        methods_layout.addWidget(QtWidgets.QLabel("Method:"))
        methods_layout.addWidget(self.method_combobox)
        methods_layout.addStretch()

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(spaces_layout)
        self.main_layout.addLayout(methods_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.add_space_button)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.control_field.button.clicked.connect(self.set_control)
        self.space_obj_field.button.clicked.connect(self.set_space_object)
        self.add_space_button.clicked.connect(self.add_space)

    def update_methods_list(self):
        self.method_combobox.clear()
        if int(pm.about(version=True)) < 2020:
            self.method_combobox.addItem("constr")
        else:
            self.method_combobox.addItems(["matrix", "constr"])

    @QtCore.Slot()
    def set_control(self):
        selection = pm.ls(sl=True, type="transform")
        if not selection or not luna_rig.Control.is_control(selection[-1]):
            return
        self.control_field.line_edit.setText(selection[-1].name())

    @QtCore.Slot()
    def set_space_object(self):
        selection = pm.ls(sl=True, type="transform")
        if not selection:
            return
        if selection[-1].name() == self.control_field.text():
            return

        self.space_obj_field.line_edit.setText(selection[-1].name())

    @QtCore.Slot()
    def add_space(self):
        space_object = self.space_obj_field.text()
        space_name = self.space_name_field.text()
        control_name = self.control_field.text()

        if not pm.objExists(control_name) or not pm.objExists(space_object) or not space_name:
            return

        ctl = luna_rig.Control(control_name)
        ctl.add_space(space_object, space_name, method=self.method_combobox.currentText())


if __name__ == "__main__":
    CustomSpaceTool.display()
