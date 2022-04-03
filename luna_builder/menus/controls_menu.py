from PySide2 import QtWidgets
import luna
import luna.static as static
import luna.utils.pysideFn as pysideFn
import luna_rig.core.shape_manager as shape_manager
import luna_rig.importexport as importexport


class ControlsMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super(ControlsMenu, self).__init__("Controls", parent)
        self.setTearOffEnabled(True)
        self.create_actions()
        self.create_sub_menus()
        self.populate()
        self.create_connections()

    def create_sub_menus(self):
        self.color_index_menu = QtWidgets.QMenu("Set color")
        self.color_index_menu.setTearOffEnabled(True)
        self.update_color_actions()

    def create_actions(self):
        self.export_all_action = QtWidgets.QAction(pysideFn.get_QIcon("save.png", maya_icon=True), "Export asset shapes", self)
        self.import_all_action = QtWidgets.QAction("Import asset shapes", self)
        self.load_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("library.png"), "Load shape from library", self)
        self.save_shape_action = QtWidgets.QAction("Save as new shape", self)
        self.copy_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("copyCurve.png"), "Copy shape", self)
        self.mirror_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorCurve.png"), "Mirror shape in place", self)
        self.mirror_shape_ops_action = QtWidgets.QAction(pysideFn.get_QIcon("mirrorCurve.png"), "Mirror shape to opposite", self)
        self.paste_shape_action = QtWidgets.QAction(pysideFn.get_QIcon("pasteCurve.png"), "Paste shape", self)
        self.copy_color_action = QtWidgets.QAction(pysideFn.get_QIcon("copyColor.png"), "Copy color", self)
        self.paste_color_action = QtWidgets.QAction(pysideFn.get_QIcon("pasteColor.png"), "Paste color", self)

    def create_connections(self):
        self.aboutToShow.connect(self.update_actions_state)
        self.export_all_action.triggered.connect(importexport.CtlShapeManager.export_asset_shapes)
        self.import_all_action.triggered.connect(importexport.CtlShapeManager.import_asset_shapes)
        self.save_shape_action.triggered.connect(importexport.CtlShapeManager.save_selection_to_lib)
        self.load_shape_action.triggered.connect(importexport.CtlShapeManager.load_shape_from_lib)
        self.copy_shape_action.triggered.connect(shape_manager.ShapeManager.copy_shape)
        self.paste_shape_action.triggered.connect(shape_manager.ShapeManager.paste_shape)
        self.copy_color_action.triggered.connect(shape_manager.ShapeManager.copy_color)
        self.paste_color_action.triggered.connect(shape_manager.ShapeManager.paste_color)

    def populate(self):
        self.addSection("Asset")
        self.addAction(self.import_all_action)
        self.addAction(self.export_all_action)
        self.addSection("Shape")
        self.addAction(self.save_shape_action)
        self.addAction(self.load_shape_action)
        self.addAction(self.copy_shape_action)
        self.addAction(self.paste_shape_action)
        self.addAction(self.mirror_shape_action)
        self.addAction(self.mirror_shape_ops_action)
        self.addSection("Color")
        self.addMenu(self.color_index_menu)
        self.addAction(self.copy_color_action)
        self.addAction(self.paste_color_action)

    def update_actions_state(self):
        asset_set = True if luna.workspace.Asset.get() else False
        self.export_all_action.setEnabled(asset_set)
        self.import_all_action.setEnabled(asset_set)

    def update_color_actions(self):
        self.color_index_menu.clear()
        for color_index in range(1, 32):
            icon_name = "colorIndex{}.png".format(static.ColorIndex(color_index).value)
            label = static.ColorIndex(color_index).name  # type: str
            label = label.title().replace("_", " ")
            action = QtWidgets.QAction(pysideFn.get_QIcon(icon_name), label, self)
            self.color_index_menu.addAction(action)
            action.triggered.connect(lambda nodes=None, index=color_index, *args: shape_manager.ShapeManager.set_color(nodes, index))
