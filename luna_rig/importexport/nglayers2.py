import pymel.core as pm
try:
    from ngSkinTools2 import api as ngst_api
except ImportError:
    pass

import luna_rig
from luna import Logger
import luna.utils.fileFn as fileFn
from luna_rig.importexport import manager as manager_base


class NgLayers2Manager(manager_base.AbstractManager):

    DATA_TYPE = 'ng_layers2'
    EXTENSION = 'layers'

    @property
    def path(self):
        return self.asset.weights.ng_layers2

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
        export_path = self.get_new_file(node)

        # Export
        try:
            ngst_api.export_json(node.name(), export_path)
            Logger.info("{0}: Exported layers {1}".format(self, export_path))
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
        import_config = ngst_api.InfluenceMappingConfig()
        import_config.use_distance_matching = True
        import_config.use_name_matching = False
        try:
            ngst_api.import_json(node_name, file=latest_file, influences_mapping_config=import_config)
            Logger.info("{0}: Imported layers for {1}".format(self, node_name))
        except Exception:
            Logger.exception("Failed to apply ngLayers to {0}".format(node_name))

    @classmethod
    def get_initialized_skin(cls):
        skin_clusters = []
        for skin in pm.ls(type="skinCluster"):
            if skin.listConnections(type="ngst2SkinLayerData"):
                skin_clusters.append(skin)
        return skin_clusters

    @classmethod
    def export_all(cls):
        ng_manager = cls()
        for skin in cls.get_initialized_skin():
            ng_manager.export_single(skin)

    @classmethod
    def import_all(cls):
        ng_manager = cls()
        for node_name in ng_manager.versioned_files.keys():
            ng_manager.import_single(node_name)

    @classmethod
    def export_selected(cls):
        ng_manager = cls()
        for obj in pm.selected():
            ng_manager.export_single(obj)

    @classmethod
    def import_selected(cls):
        ng_manager = cls()
        for obj in pm.selected():
            ng_manager.import_single(obj)


if __name__ == "__main__":
    manager = NgLayers2Manager()
    manager.export_all()
