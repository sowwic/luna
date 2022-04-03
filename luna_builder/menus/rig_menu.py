from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn


class RigMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(RigMenu, self).__init__("Rig", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        self.driven_pose_exporter = QtWidgets.QAction("Export driven pose", self)
        self.sdk_corrective_exporter = QtWidgets.QAction("SDK corrective exporter", self)

    def create_connections(self):
        self.driven_pose_exporter.triggered.connect(lambda: luna.tools.DrivenPoseExporter.display())
        self.sdk_corrective_exporter.triggered.connect(lambda: luna.tools.SDKCorrectiveExporter.display())

    def populate(self):
        self.addAction(self.driven_pose_exporter)
        self.addAction(self.sdk_corrective_exporter)

    def update_actions_state(self):
        is_asset_set = True if luna.workspace.Asset.get() else False
        self.driven_pose_exporter.setEnabled(is_asset_set)
        self.sdk_corrective_exporter.setEnabled(is_asset_set)
