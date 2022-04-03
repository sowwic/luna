import sys
import pymel.core as pm
from PySide2 import QtWidgets
import luna
import luna.utils.pysideFn as pysideFn
import luna_rig.importexport as importexport


class SkinMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(SkinMenu, self).__init__("Skin", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        pass

    def create_actions(self):
        self.bind_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("smoothSkin.png", maya_icon=True), "Bind skin", self)
        self.detach_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("detachSkin.png", maya_icon=True), "Detach skin", self)
        self.mirror_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorSkinWeight.png", maya_icon=True), "Mirror weights", self)
        self.copy_skin_action = QtWidgets.QAction(pysideFn.get_QIcon("copySkinWeight.png", maya_icon=True), "Copy weights", self)
        self.export_all_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export asset weights", self)
        self.import_all_action = QtWidgets.QAction("Import asset weights", self)
        self.export_selected_action = QtWidgets.QAction("Export selection weights", self)
        self.import_selected_action = QtWidgets.QAction("Import selection weights", self)
        self.ngtools_export_all_action = QtWidgets.QAction("Export asset layers", self)
        self.ngtools_import_all_action = QtWidgets.QAction("Import asset layers", self)
        self.ngtools_export_selected_action = QtWidgets.QAction("Export selection layers", self)
        self.ngtools_import_selected_action = QtWidgets.QAction("Import selection layers", self)
        self.ngtools2_export_all_action = QtWidgets.QAction("Export asset layers", self)
        self.ngtools2_import_all_action = QtWidgets.QAction("Import asset layers", self)
        self.ngtools2_export_selected_action = QtWidgets.QAction("Export selection layers", self)
        self.ngtools2_import_selected_action = QtWidgets.QAction("Import selection layers", self)

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        # Actions
        self.bind_skin_action.triggered.connect(lambda: pm.mel.eval("SmoothBindSkinOptions;"))
        self.detach_skin_action.triggered.connect(lambda: pm.mel.eval("DetachSkinOptions;"))
        self.mirror_skin_action.triggered.connect(lambda: pm.mel.eval("MirrorSkinWeightsOptions;"))
        self.copy_skin_action.triggered.connect(lambda: pm.mel.eval("CopySkinWeightsOptions;"))
        self.export_all_action.triggered.connect(lambda *_: importexport.SkinManager.export_all())
        self.import_all_action.triggered.connect(importexport.SkinManager.import_all)
        self.export_selected_action.triggered.connect(importexport.SkinManager.export_selected)
        self.import_selected_action.triggered.connect(importexport.SkinManager.import_selected)
        # Ng layers
        if sys.version_info[0] < 3:
            self.ngtools_export_all_action.triggered.connect(importexport.NgLayersManager.export_all)
            self.ngtools_import_all_action.triggered.connect(importexport.NgLayersManager.import_all)
            self.ngtools_export_selected_action.triggered.connect(importexport.NgLayersManager.export_selected)
            self.ngtools_import_selected_action.triggered.connect(importexport.NgLayersManager.import_selected)
        # Ng layers2
        self.ngtools2_export_all_action.triggered.connect(importexport.NgLayers2Manager.export_all)
        self.ngtools2_import_all_action.triggered.connect(importexport.NgLayers2Manager.import_all)
        self.ngtools2_export_selected_action.triggered.connect(importexport.NgLayers2Manager.export_selected)
        self.ngtools2_import_selected_action.triggered.connect(importexport.NgLayers2Manager.import_selected)

    def populate(self):
        self.addAction(self.bind_skin_action)
        self.addAction(self.detach_skin_action)
        self.addSection("Weight maps")
        self.addAction(self.mirror_skin_action)
        self.addAction(self.copy_skin_action)
        self.addSection("Asset")
        self.addAction(self.export_all_action)
        self.addAction(self.import_all_action)
        self.addAction(self.export_selected_action)
        self.addAction(self.import_selected_action)
        if "ngSkinTools" in pm.moduleInfo(lm=1) and sys.version_info[0] < 3:
            self.addSection("ngSkinTools")
            ng_asset_menu = self.addMenu("Asset")  # type: QtWidgets.QMenu
            ng_asset_menu.setTearOffEnabled(True)
            ng_asset_menu.addAction(self.ngtools_export_all_action)
            ng_asset_menu.addAction(self.ngtools_import_all_action)
            ng_selection_menu = self.addMenu("Selection")  # type: QtWidgets.QMenu
            ng_selection_menu.setTearOffEnabled(True)
            ng_selection_menu.addAction(self.ngtools_export_selected_action)
            ng_selection_menu.addAction(self.ngtools_import_selected_action)
        if "ngskintools2" in pm.moduleInfo(lm=1):
            self.addSection("ngSkinTools2")
            ng2_asset_menu = self.addMenu("Asset")  # type: QtWidgets.QMenu
            ng2_asset_menu.setTearOffEnabled(True)
            ng2_asset_menu.addAction(self.ngtools2_export_all_action)
            ng2_asset_menu.addAction(self.ngtools2_import_all_action)
            ng2_selection_menu = self.addMenu("Selection")  # type: QtWidgets.QMenu
            ng2_selection_menu.setTearOffEnabled(True)
            ng2_selection_menu.addAction(self.ngtools2_export_selected_action)
            ng2_selection_menu.addAction(self.ngtools2_import_selected_action)

    def update_actions_state(self):
        is_asset_set = True if luna.workspace.Asset.get() else False
        self.export_all_action.setEnabled(is_asset_set)
        self.import_all_action.setEnabled(is_asset_set)
        self.import_selected_action.setEnabled(is_asset_set)
        self.export_selected_action.setEnabled(is_asset_set)
        self.ngtools_export_all_action.setEnabled(is_asset_set)
        self.ngtools_import_all_action.setEnabled(is_asset_set)
        self.ngtools_import_selected_action.setEnabled(is_asset_set)
        self.ngtools_export_selected_action.setEnabled(is_asset_set)
        self.ngtools2_export_all_action.setEnabled(is_asset_set)
        self.ngtools2_import_all_action.setEnabled(is_asset_set)
        self.ngtools2_import_selected_action.setEnabled(is_asset_set)
        self.ngtools2_export_selected_action.setEnabled(is_asset_set)
