import pymel.core as pm
from PySide2 import QtWidgets
from PySide2 import QtCore
import luna_rig
import luna.interface.shared_widgets as shared_widgets
import luna.utils.pysideFn as pysideFn
from luna_rig.importexport import sdk_corrective


class SDKCorrectiveExporter(QtWidgets.QDialog):

    INSTANCE = None  # type: SDKCorrectiveExporter
    GEOMETRY = None

    def closeEvent(self, event):
        SDKCorrectiveExporter.GEOMETRY = self.saveGeometry()
        super(SDKCorrectiveExporter, self).closeEvent(event)

    def __init__(self, parent=pysideFn.maya_main_window()):
        super(SDKCorrectiveExporter, self).__init__(parent)
        self.setWindowTitle("SDK corrective exporter")
        self.setProperty("saveWindowPref", True)
        self.resize(500, 500)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Post init
        self.restoreGeometry(SDKCorrectiveExporter.GEOMETRY)

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
        self.pose_name_field = shared_widgets.StringFieldWidget("Pose name:", button=False)
        self.pose_name_field.line_edit.setValidator(pysideFn.ReValidators.no_space)
        self.driver_field = shared_widgets.StringFieldWidget("Driver:", button_text="Set")
        self.driver_field.button.setMinimumWidth(40)
        self.components_list = shared_widgets.ComponentsListing(base_type=luna_rig.components.CorrectiveComponent, general_types_enabled=False)
        self.controls_list = shared_widgets.ControlsList(self.components_list)
        self.export_button = QtWidgets.QPushButton("Export")

    def create_layouts(self):
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.pose_name_field)
        form_layout.addRow(self.driver_field)
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
            pm.displayWarning("Select control in the scene or from controls list.")
            return

        selection = selection[-1]
        self.driver_field.line_edit.setText(selection.name())

    def export_pose(self):
        pose_manager = sdk_corrective.SDKCorrectiveManager()
        # Verify component selection
        if self.components_list.list.currentItem():
            current_component = self.components_list.list.currentItem().data(1)
        else:
            pm.displayError("Select a component to export pose for.")
            return
        if not isinstance(current_component, luna_rig.components.CorrectiveComponent):
            pm.displayError("Invalid component selection, must be of type: {0}".format(luna_rig.components.CorrectiveComponent))
            return

        ctl_filter = [item.data(0) for item in self.controls_list.list.selectedItems()]
        pose_manager.export_pose(current_component, self.pose_name_field.text(), self.driver_field.text(), control_filter_list=ctl_filter)

    @ QtCore.Slot()
    def update_export_button(self):
        conditions = [self.driver_field.line_edit.text(),
                      self.pose_name_field.text(),
                      self.components_list.list.selectedItems()]
        self.export_button.setEnabled(all(conditions))


if __name__ == "__main__":
    SDKCorrectiveExporter.display()
