import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
import luna_rig
import luna.interface.shared_widgets as shared_widgets
import luna.utils.pysideFn as pysideFn
from luna_rig.importexport import driven_pose


class DrivenPoseExporter(QtWidgets.QDialog):

    INSTANCE = None  # type: DrivenPoseExporter
    GEOMETRY = None

    def __init__(self, parent=pysideFn.maya_main_window()):
        super(DrivenPoseExporter, self).__init__(parent)
        self.setWindowTitle("Driven pose exporter")
        self.setProperty("saveWindowPref", True)
        self.resize(500, 500)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Post init
        self.restoreGeometry(DrivenPoseExporter.GEOMETRY)

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = cls()
        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show()
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    def create_widgets(self):
        self.pose_name_field = shared_widgets.StringFieldWidget("Pose name:", button=False)
        self.pose_name_field.line_edit.setValidator(pysideFn.ReValidators.no_space)
        self.driver_field = shared_widgets.StringFieldWidget("Driver:", button_text="Set")
        self.driver_field.button.setMinimumWidth(40)
        self.driver_field.line_edit.setReadOnly(True)
        self.driver_value_field = shared_widgets.NumericFieldWidget("Driver value:", data_type="double", default_value=10.0)
        self.components_list = shared_widgets.ComponentsListing()
        self.controls_list = shared_widgets.ControlsList(self.components_list)
        self.export_button = QtWidgets.QPushButton("Export")

    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.pose_name_field)
        form_layout.addRow(self.driver_field)
        form_layout.addRow(self.driver_value_field)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(form_layout)
        self.main_layout.addWidget(self.components_list)
        self.main_layout.addWidget(self.controls_list)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.export_button)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.driver_field.button.clicked.connect(self.set_driver)
        self.export_button.clicked.connect(self.export_pose)
        self.pose_name_field.line_edit.textChanged.connect(self.update_export_button)
        self.driver_field.line_edit.textChanged.connect(self.update_export_button)
        self.components_list.list.currentItemChanged.connect(self.update_export_button)

    def set_driver(self):
        selection = pm.selected()
        # Get valid selection
        if not selection:
            selection = self.controls_list.list.selectedItems()
        if not selection:
            pm.displayWarning("Select control in the scene or from controls list.")
            return
        selection = selection[-1]
        # Get controls transform if list selection
        if isinstance(selection, QtWidgets.QListWidgetItem):
            selection = selection.data(1).transform
        if luna_rig.Control.is_control(selection):
            self.driver_field.line_edit.setText(selection.name())
        else:
            pm.displayError("{0} is not a valid control.".format(selection))

    def export_pose(self):
        pose_manager = driven_pose.DrivenPoseManager()
        # Verify component selection
        if self.components_list.list.currentItem():
            current_component = self.components_list.list.currentItem().data(1)
        else:
            pm.displayError("Select a component to export pose for.")
            return
        if not isinstance(current_component, luna_rig.AnimComponent):
            pm.displayError("Invalid component selection, must be of type: {0}".format(luna_rig.AnimComponent))
            return
        # Get controls to export
        if not self.controls_list.list.selectedItems():
            export_controls = current_component.controls
        else:
            export_controls = [item.data(1) for item in self.controls_list.list.selectedItems()]
        # Do export
        pose_manager.export_pose(current_component,
                                 export_controls,
                                 driver_ctl=self.driver_field.line_edit.text(),
                                 pose_name=self.pose_name_field.text(),
                                 driver_value=self.driver_value_field.value())

    @QtCore.Slot()
    def update_export_button(self):
        conditions = [self.driver_field.line_edit.text(),
                      self.pose_name_field.text(),
                      self.driver_value_field.value(),
                      self.components_list.list.selectedItems()]
        self.export_button.setEnabled(all(conditions))


if __name__ == "__main__":
    DrivenPoseExporter.display()
