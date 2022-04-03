import pymel.core as pm
from PySide2 import QtWidgets
import luna.utils.pysideFn as pysideFn
import luna_rig.functions.jointFn as jointFn


class JointsMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(JointsMenu, self).__init__("Joints", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        # Joints
        self.mirror_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorJoint.png"), "Mirror", self)
        self.selection_to_chain_action = QtWidgets.QAction(pysideFn.get_QIcon("kinJoint.png", maya_icon=True), "Chain from selection", self)

    def create_connections(self):
        self.mirror_action.triggered.connect(lambda *args: jointFn.mirror_chain())
        self.selection_to_chain_action.triggered.connect(lambda *args: jointFn.create_chain(joint_list=pm.selected(type="joint")))

    def populate(self):
        self.addAction(self.mirror_action)
        self.addAction(self.selection_to_chain_action)

    def update_actions_state(self):
        pass
