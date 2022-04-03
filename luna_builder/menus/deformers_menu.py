import pymel.core as pm
from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn
import luna_rig.importexport as importexport


class DeformersMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(DeformersMenu, self).__init__("Deformers", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        self.create_blendshapes_menu()
        self.create_psd_menu()
        self.create_deltamush_menu()

    def create_actions(self):
        self.shape_editor_action = QtWidgets.QAction(pysideFn.get_QIcon("blendShapeEditor.png", maya_icon=True), "Shape editor", self)
        self.export_all_blendshapes_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export asset blendshapes", self)
        self.import_all_blendshapes_action = QtWidgets.QAction("Import asset blendshapes", self)
        self.export_selected_blendshapes_action = QtWidgets.QAction("Exported selected blendshapes", self)
        self.import_selected_blendshapes_action = QtWidgets.QAction("Import selected blendshapes", self)

        self.pose_manager_action = QtWidgets.QAction(pysideFn.get_QIcon("poseEditor.png", maya_icon=True), "Pose manager", self)
        self.export_pose_interpolators_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export interpolators", self)
        self.import_pose_interpolators_action = QtWidgets.QAction("Import interpolators", self)

        self.export_all_deltamush_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), 'Export asset deltaMush', self)
        self.import_all_deltamush_action = QtWidgets.QAction('Import asset deltaMush', self)
        self.export_selected_deltamush_action = QtWidgets.QAction('Export selected deltaMush', self)
        self.import_selected_deltamush_action = QtWidgets.QAction('Import selected deltaMush', self)

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        # Blendshapes
        self.shape_editor_action.triggered.connect(lambda: pm.mel.eval("ShapeEditor;"))
        self.import_all_blendshapes_action.triggered.connect(importexport.BlendShapeManager.import_all)
        self.export_all_blendshapes_action.triggered.connect(importexport.BlendShapeManager.export_all)
        self.import_selected_blendshapes_action.triggered.connect(importexport.BlendShapeManager.import_selected)
        self.export_selected_blendshapes_action.triggered.connect(importexport.BlendShapeManager.export_selected)

        self.pose_manager_action.triggered.connect(lambda: pm.mel.eval("PoseEditor;"))
        self.import_pose_interpolators_action.triggered.connect(importexport.PsdManager.import_all)
        self.export_pose_interpolators_action.triggered.connect(importexport.PsdManager.export_all)

        self.import_all_deltamush_action.triggered.connect(importexport.DeltaMushManager.import_all)
        self.export_all_deltamush_action.triggered.connect(importexport.DeltaMushManager.export_all)
        self.import_selected_deltamush_action.triggered.connect(importexport.DeltaMushManager.import_selected)
        self.export_selected_deltamush_action.triggered.connect(importexport.DeltaMushManager.export_selected)

    def create_blendshapes_menu(self):
        self.blendshapes_menu = QtWidgets.QMenu('Blendshapes')
        self.blendshapes_menu.addAction(self.shape_editor_action)
        self.blendshapes_menu.addSection("Asset")
        self.blendshapes_menu.addAction(self.import_all_blendshapes_action)
        self.blendshapes_menu.addAction(self.export_all_blendshapes_action)
        self.blendshapes_menu.addSection("Selection")
        self.blendshapes_menu.addAction(self.import_selected_blendshapes_action)
        self.blendshapes_menu.addAction(self.export_selected_blendshapes_action)

    def create_psd_menu(self):
        self.psd_menu = QtWidgets.QMenu('Pose Space Deformation')
        self.psd_menu.addAction(self.pose_manager_action)
        self.psd_menu.addAction(self.import_pose_interpolators_action)
        self.psd_menu.addAction(self.export_pose_interpolators_action)

    def create_deltamush_menu(self):
        self.deltamush_menu = QtWidgets.QMenu('DeltaMush')
        self.deltamush_menu.addSection('Asset')
        self.deltamush_menu.addAction(self.import_all_deltamush_action)
        self.deltamush_menu.addAction(self.export_all_deltamush_action)
        self.deltamush_menu.addSection('Selection')
        self.deltamush_menu.addAction(self.import_selected_deltamush_action)
        self.deltamush_menu.addAction(self.export_selected_deltamush_action)

    def populate(self):
        self.addMenu(self.blendshapes_menu)
        self.addMenu(self.psd_menu)
        self.addMenu(self.deltamush_menu)

    def update_actions_state(self):
        is_asset_set = True if luna.workspace.Asset.get() else False
        for menu in (self.blendshapes_menu, self.psd_menu, self.deltamush_menu):
            menu.setEnabled(is_asset_set)
