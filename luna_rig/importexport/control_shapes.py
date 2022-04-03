import pymel.core as pm
import os
from luna import Logger
from luna.utils import fileFn
import luna_rig
from luna_rig.importexport import manager
from luna_rig.core.shape_manager import ShapeManager
from luna_rig.functions import rigFn


class CtlShapeManager(manager.AbstractManager):

    DATA_TYPE = 'controls'
    EXTENSION = 'crvs'

    @property
    def path(self):
        return self.asset.controls

    def get_base_name(self):
        return "{0}_{1}".format(self.asset.name, self.DATA_TYPE)

    def get_new_file(self):
        return fileFn.get_new_versioned_file(self.get_base_name(), dir_path=self.path, extension=self.EXTENSION, full_path=True)

    def get_latest_file(self):
        return fileFn.get_latest_file(self.get_base_name(), self.path, extension=self.EXTENSION, full_path=True)

    @classmethod
    def save_selection_to_lib(cls):
        selection = pm.ls(sl=1)
        if not selection or not luna_rig.Control.is_control(selection[-1]):
            Logger.warning("No control selected to save")
            return

        selection = selection[-1]
        export_path = pm.fileDialog2(ff='JSON files (*.json)', cap='Save new shape', dir=ShapeManager.SHAPES_LIB)
        if not export_path:
            return

        export_path = export_path[0]
        shape_name = os.path.basename(export_path)
        ShapeManager.save_shape(selection, shape_name)
        Logger.info("Exported shape: {0}".format(export_path))

    @classmethod
    def load_shape_from_lib(cls):
        selection = pm.ls(sl=1)
        if not selection or not luna_rig.Control.is_control(selection[-1]):
            Logger.warning("No control selected to load shape for!")
            return

        shape_file = pm.fileDialog2(ff='JSON files (*.json)', cap='Select shape', dir=ShapeManager.SHAPES_LIB, fm=1)
        if not shape_file:
            return
        shape_name = os.path.basename(shape_file[0]).split(".")[0]
        for node in selection:
            ctl = luna_rig.Control(node)
            ctl.shape = shape_name
        Logger.info("Successfully loaded shape: " + shape_name)

    @classmethod
    def export_asset_shapes(cls):
        manager_instance = cls()
        data_dict = {}
        all_controls = rigFn.list_controls()
        if not all_controls:
            Logger.warning("No controls to save")
            return

        for ctl in all_controls:
            data_dict[ctl.transform.name()] = ctl.shape
        export_path = manager_instance.get_new_file()
        fileFn.write_json(export_path, data=data_dict)
        Logger.info("Exported control shapes: " + export_path)

    @classmethod
    def import_asset_shapes(cls):
        manager_instance = cls()
        latest_file = manager_instance.get_latest_file()
        if not latest_file:
            return
        data_dict = fileFn.load_json(latest_file)

        for transform, shape_data in data_dict.items():
            ShapeManager.apply_shape(transform, shape_list=shape_data)
        Logger.info("Imported control shapes: {0}".format(latest_file))
