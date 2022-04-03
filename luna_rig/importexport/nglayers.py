import pymel.core as pm
try:
    from ngSkinTools.utilities import removeLayerData
    from ngSkinTools.importExport import JsonExporter
    from ngSkinTools.importExport import JsonImporter
    from ngSkinTools.importExport import LayerData
except ImportError:
    pass

import luna
import luna_rig
from luna import Logger
import luna.utils.fileFn as fileFn
from luna_rig.importexport import manager as manager_base


class NgLayersManager(manager_base.AbstractManager):

    DATA_TYPE = 'ng_layers'
    EXTENSION = 'layers'

    def __init__(self):
        super(NgLayersManager, self).__init__()
        self.file_format = luna.Config.get(luna.RigVars.nglayers_export_format, default="pickle")  # type: str
        if self.file_format not in ["json", "pickle"]:
            Logger.error("{0}: Invalid file format: {1}".format(self, self.file_format))
            raise ValueError

    @property
    def path(self):
        return self.asset.weights.ng_layers

    def get_base_name(self, node):
        return str(node)

    def get_new_file(self, node):
        return fileFn.get_new_versioned_file(self.get_base_name(node), dir_path=self.path, extension=self.EXTENSION, full_path=True)

    def get_latest_file(self, node):
        return fileFn.get_latest_file(self.get_base_name(node), self.path, extension=self.EXTENSION, full_path=True)

    def export_single(self, node):
        # Get transform
        if isinstance(node, str):
            node = pm.Pynode(node)
        if isinstance(node, luna_rig.nt.SkinCluster):
            node = node.getGeometry()[0].getTransform()
        # Prepare to export
        new_file = self.get_new_file(node)
        layer_data = LayerData()
        layer_data.loadFrom(str(node))
        exporter = JsonExporter()
        json_data = exporter.process(layer_data)
        # Export
        try:
            if self.file_format == "pickle":
                fileFn.write_pickle(new_file, json_data)
            elif self.file_format == "json":
                fileFn.write_json(new_file, json_data, sort_keys=False)
            Logger.info("{0}: Exported layers {1}".format(self, new_file))
        except Exception:
            Logger.exception("{0}: Failed to export layers for {0}".format(node))

    def import_single(self, node_name):
        # Get node name
        if not pm.objExists(node_name):
            Logger.warning("{0}: Object {1} no longer exists, skipping...".format(self, node_name))
            return
        if isinstance(node_name, pm.PyNode):
            node_name = str(node_name)
        # Get latest file
        latest_file = self.get_latest_file(node_name)
        if not latest_file:
            Logger.warning("{0}: No exported layers found for {1}".format(self, node_name))
            return
        # Do import
        if self.file_format == "pickle":
            imported_data = fileFn.load_pickle(latest_file)
        elif self.file_format == "json":
            imported_data = fileFn.load_json(latest_file)
        ng_importer = JsonImporter()
        layer_data = ng_importer.process(imported_data)
        try:
            layer_data.saveTo(node_name)
            Logger.info("{0}: Imported layers for {1}".format(self, node_name))
        except Exception:
            Logger.exception("Failed to apply ngLayers to {0}".format(node_name))

    @classmethod
    def get_initialized_skin(cls):
        skin_clusters = []
        for skin in pm.ls(type="skinCluster"):
            if skin.listConnections(type="ngSkinLayerData"):
                skin_clusters.append(skin)
        return skin_clusters

    @classmethod
    def export_all(cls):
        ng_manager = NgLayersManager()
        for skin in cls.get_initialized_skin():
            ng_manager.export_single(skin)

    @classmethod
    def import_all(cls):
        ng_manager = NgLayersManager()
        for node_name in ng_manager.versioned_files.keys():
            ng_manager.import_single(node_name)

    @classmethod
    def export_selected(cls):
        ng_manager = NgLayersManager()
        for obj in pm.selected():
            ng_manager.export_single(obj)

    @classmethod
    def import_selected(cls):
        ng_manager = NgLayersManager()
        for obj in pm.selected():
            ng_manager.import_single(obj)

    @staticmethod
    def delete_custom_nodes(selection=False):
        if selection:
            removeLayerData.removeLayersFromSelection()
        else:
            removeLayerData.removeAllNodes()


if __name__ == "__main__":
    manager = NgLayersManager()
    manager.export_all()
