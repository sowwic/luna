import pymel.core as pm
from PySide2 import QtWidgets


import luna_rig
from luna import Logger
import luna.utils.pysideFn as pysisdeFn
import luna.interface.shared_widgets as shared_widgets


class AnimBakerDialog(QtWidgets.QDialog):

    INSTANCE = None  # type: AnimBakerDialog
    GEOMETRY = None

    def __init__(self, parent=pysisdeFn.maya_main_window()):
        super(AnimBakerDialog, self).__init__(parent)
        self.setWindowTitle("Animation baker")
        self.setProperty("saveWindowPref", True)
        self.resize(400, 500)
        # Init ui
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        # Post init
        self.restoreGeometry(AnimBakerDialog.GEOMETRY)

    @classmethod
    def display(cls):
        if not cls.INSTANCE:
            cls.INSTANCE = cls()
        if cls.INSTANCE.isHidden():
            cls.INSTANCE.show()
        else:
            cls.INSTANCE.raise_()
            cls.INSTANCE.activateWindow()

    def create_actions(self):
        pass

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
                components.append(item.data(1))
        else:
            components = [item.data(1) for item in pysisdeFn.qlist_all_items(self.components_wgt.list)]
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


if __name__ == "__main__":
    AnimBakerDialog.display()
