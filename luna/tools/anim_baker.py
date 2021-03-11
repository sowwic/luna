import pymel.core as pm
from PySide2 import QtWidgets


import luna_rig
from luna import Logger
import luna.utils.pysideFn as pysisdeFn
import luna.interface.shared_widgets as shared_widgets
reload(shared_widgets)


class AnimBakerDialog(QtWidgets.QDialog):

    INSTANCE = None  # type: AnimBakerDialog
    GEOMETRY = None

    def closeEvent(self, event):
        AnimBakerDialog.GEOMETRY = self.saveGeometry()
        super(AnimBakerDialog, self).closeEvent(event)

    def __init__(self, parent=pysisdeFn.maya_main_window()):
        super(AnimBakerDialog, self).__init__(parent)
        self.setWindowTitle("Animation baker")
        self.setProperty("saveWindowPref", True)
        self.resize(400, 500)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

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

    def create_actions(self):
        pass

    def create_widgets(self):
        self.mode_combobox = QtWidgets.QComboBox()
        self.mode_combobox.addItems(("Skeleton", "FKIK", "Space"))
        self.skel_baker = SkeletonBakerWidget()
        self.fkik_baker = FKIKBakerWidget()
        self.space_baker = SpaceBakerWidget()
        self.stack = QtWidgets.QStackedWidget()
        # self.stack.layout().setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.skel_baker)
        self.stack.addWidget(self.fkik_baker)
        self.stack.addWidget(self.space_baker)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.mode_combobox)
        self.main_layout.addWidget(self.stack)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.mode_combobox.currentIndexChanged.connect(self.stack.setCurrentIndex)


class SkeletonBakerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SkeletonBakerWidget, self).__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.range_widget = shared_widgets.TimeRangeWidget()
        self.components_grp = QtWidgets.QGroupBox("Components")
        self.components_wgt = shared_widgets.ComponentsListing()
        # Bake buttons
        self.bake_to_skel_btn = QtWidgets.QPushButton("Bake to skeleton")
        self.bake_to_rig_btn = QtWidgets.QPushButton("Bake to rig")
        self.bake_and_detach_btn = QtWidgets.QPushButton("Bake and detach")
        self.remove_rig_button = QtWidgets.QPushButton("Remove rig")
        self.remove_rig_button.setStyleSheet("background-color: rgb(144,0,0);")

    def create_layouts(self):
        components_layout = QtWidgets.QVBoxLayout()
        components_layout.addWidget(self.components_wgt)
        self.components_grp.setLayout(components_layout)

        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.addWidget(self.bake_to_skel_btn)
        buttons_layout.addWidget(self.bake_and_detach_btn)
        buttons_layout.addWidget(self.bake_to_rig_btn)
        buttons_layout.addWidget(self.remove_rig_button)

        self.main_layout = QtWidgets.QVBoxLayout()
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.range_widget)
        self.main_layout.addWidget(self.components_wgt)
        self.main_layout.addStretch()
        self.main_layout.addLayout(buttons_layout)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.bake_to_skel_btn.clicked.connect(self.bake_to_skel)
        self.bake_and_detach_btn.clicked.connect(self.bake_and_detach)
        self.bake_to_rig_btn.clicked.connect(self.bake_to_rig)
        self.remove_rig_button.clicked.connect(self.remove_rig)

    def get_bake_components(self):
        components = []
        if self.components_wgt.list.selectedItems():
            for item in self.components_wgt.list.selectedItems():
                if not item.data(1).is_animatable():
                    Logger.warning("Non bakeable component selected {0}, skipping...".format(item.data(1)))
                else:
                    components.append(item.data(1))
        else:
            components = [item.data(1) for item in pysisdeFn.qlist_all_items(self.components_wgt.list) if item.data(1).is_animatable()]
        return components

    def bake_to_skel(self):
        components = self.get_bake_components()
        time_range = self.range_widget.get_range()
        for each in components:
            each.bake_to_skeleton(time_range=time_range)
        Logger.info("Bake to skeleton complete.")

    def bake_and_detach(self):
        components = self.get_bake_components()
        time_range = self.range_widget.get_range()
        for each in components:
            each.bake_and_detach(time_range=time_range)
        Logger.info("Bake and detach complete.")

    def bake_to_rig(self):
        components = self.get_bake_components()
        time_range = self.range_widget.get_range()
        for each in components:
            each.bake_to_rig(time_range=time_range)
        Logger.info("Bake to rig complete.")

    def remove_rig(self):
        selected = self.components_wgt.get_selected_components()
        if not selected or not isinstance(selected[-1], luna_rig.components.Character):
            pm.warning("Select Character component to remove rig.")
            return
        character = selected[-1]  # type: luna_rig.components.Character
        char_name = character.name
        time_range = self.range_widget.get_range()
        character.remove(time_range=time_range)
        Logger.info("{0} rig successfully removed.".format(char_name))


class FKIKBakerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(FKIKBakerWidget, self).__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.range_widget = shared_widgets.TimeRangeWidget()
        self.options_group = QtWidgets.QGroupBox("Options")
        self.fk_source_radio = QtWidgets.QRadioButton("FK")
        self.fk_source_radio.setChecked(True)
        self.ik_source_radio = QtWidgets.QRadioButton("IK")
        self.checkbox_pv_bake = QtWidgets.QCheckBox("Pole vector")
        self.checkbox_pv_bake.setChecked(True)
        self.checkbox_pv_bake.setEnabled(self.fk_source_radio.isChecked())
        self.step_field = shared_widgets.NumericFieldWidget("Step:", data_type="int", default_value=1)
        self.components_wgt = shared_widgets.ComponentsListing(base_type=luna_rig.components.FKIKComponent, general_types_enabled=False)
        self.bake_button = QtWidgets.QPushButton("Bake")

    def create_layouts(self):
        self.range_widget.main_layout.addWidget(self.step_field)

        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(QtWidgets.QLabel("Source:"))
        options_layout.addWidget(self.fk_source_radio)
        options_layout.addWidget(self.ik_source_radio)
        options_layout.addWidget(self.checkbox_pv_bake)
        options_layout.addStretch()
        self.options_group.setLayout(options_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.range_widget)
        self.main_layout.addWidget(self.options_group)
        self.main_layout.addWidget(self.components_wgt)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.bake_button)
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.fk_source_radio.toggled.connect(self.checkbox_pv_bake.setEnabled)
        self.bake_button.clicked.connect(self.do_baking)

    def do_baking(self):
        for fkik_component in self.components_wgt.get_selected_components():
            source = "fk" if self.fk_source_radio.isChecked() else "ik"
            fkik_component.bake_fkik(source=source,
                                     time_range=self.range_widget.get_range(),
                                     bake_pv=self.checkbox_pv_bake.isChecked(),
                                     step=self.step_field.value())


class SpaceBakerWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SpaceBakerWidget, self).__init__(parent)
        self.custom_space_item_text = "Custom..."
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.range_widget = shared_widgets.TimeRangeWidget()
        self.control_field = shared_widgets.StringFieldWidget(label_text="Control:", button=True, button_text="Set")
        self.spaces_combobox = QtWidgets.QComboBox()
        self.custom_space_object_field = shared_widgets.StringFieldWidget(label_text="Custom object", button=True, button_text="Set")
        self.step_field = shared_widgets.NumericFieldWidget("Step:", data_type="int", default_value=1)
        self.bake_button = QtWidgets.QPushButton("Bake")

    def create_layouts(self):
        self.range_widget.main_layout.addWidget(self.step_field)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Target space:", self.spaces_combobox)
        form_layout.addRow(self.control_field)
        form_layout.addRow(self.custom_space_object_field)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.range_widget)
        self.main_layout.addLayout(form_layout)

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.bake_button)
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

    def create_connections(self):
        self.control_field.button.clicked.connect(self.set_control)
        self.spaces_combobox.currentTextChanged.connect(lambda text: self.custom_space_object_field.setEnabled(text == self.custom_space_item_text))
        self.custom_space_object_field.button.clicked.connect(self.set_custom_space)
        self.bake_button.clicked.connect(self.do_baking)

    def set_control(self):
        selection = pm.selected()
        if not selection:
            pm.warning("Select control to bake space for")
            return
        ctl_transform = selection[-1]
        if not luna_rig.Control.is_control(ctl_transform):
            pm.warning("Object {0} is not a control".format(ctl_transform))
            return
        self.control_field.line_edit.setText(str(ctl_transform))
        self.update_spaces_box()

    def update_spaces_box(self):
        self.spaces_combobox.clear()
        try:
            control_instance = luna_rig.Control(self.control_field.text())
        except Exception:
            Logger.exception("Failed to update {0} spaces".format(self.control_field.text()))
            return
        for space_name, space_index in control_instance.spaces:
            self.spaces_combobox.addItem(space_name, space_index)
        self.spaces_combobox.addItem(self.custom_space_item_text, None)

    def set_custom_space(self):
        selection = pm.selected()
        if not selection:
            pm.warning("Select custom space object")
            return
        space_transform = selection[-1]
        if not isinstance(space_transform, luna_rig.nt.Transform):
            pm.displayError("Space object must be of type Transform")
            return
        self.custom_space_object_field.line_edit.setText(space_transform.name())

    def do_baking(self):
        try:
            ctl_instance = luna_rig.Control(self.control_field.text())
        except Exception:
            Logger.exception("Failed to create control instance from {0}".format(self.control_field.text()))
            raise RuntimeError("Invalid control object")

        step = self.step_field.value()
        if self.spaces_combobox.currentText() == self.custom_space_item_text:
            custom_object = self.custom_space_object_field.text()
            if not custom_object or not pm.objExists(custom_object):
                pm.displayError("Invalid custom space object: {0}".format(custom_object))
                return
            ctl_instance.bake_custom_space(custom_object, time_range=self.range_widget.get_range(), step=step)
        else:
            ctl_instance.bake_space(space_name=self.spaces_combobox.currentText(),
                                    time_range=self.range_widget.get_range(),
                                    step=step)


if __name__ == "__main__":
    AnimBakerDialog.display()
