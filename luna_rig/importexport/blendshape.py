import pymel.core as pm
from luna import Logger
from luna import static
from luna.utils import fileFn
import luna_rig
from luna_rig.importexport import manager
import luna_rig.functions.deformerFn as deformerFn


class BlendShapeManager(manager.AbstractManager):

    DATA_TYPE = "blendShape"
    EXTENSION = "shape"

    @property
    def path(self):
        return self.asset.data.blendshapes

    def get_base_name(self, bs_node):
        return str(bs_node)

    def get_latest_file(self, bs_name, full_path=False):
        return fileFn.get_latest_file(self.get_base_name(bs_name), self.path, extension=self.EXTENSION, full_path=full_path)

    def get_new_file(self, bs_node):
        return fileFn.get_new_versioned_file(self.get_base_name(bs_node), self.path, extension=self.EXTENSION, full_path=True)

    def get_mapping(self):
        return fileFn.load_json(self.asset.mapping.blendshapes)

    def save_mapping(self, bs_node):
        mapping = self.get_mapping()
        mapping[bs_node.name()] = bs_node.getGeometry()[0]
        fileFn.write_json(self.asset.mapping.blendshapes, mapping)

    def get_mapped_geometry(self, bs_node):
        if not isinstance(bs_node, str):
            bs_node = str(bs_node)
        mapping = self.get_mapping()
        return mapping.get(bs_node)

    def export_single(self, node):
        node = pm.PyNode(node)  # type:  luna_rig.nt.BlendShape
        if not isinstance(node, luna_rig.nt.BlendShape):
            Logger.error("{0} is not a blendShape node.".format(node))
            return False
        export_path = self.get_new_file(node.name())
        try:
            node.export(export_path)
            self.save_mapping(node)
            Logger.info("{0}: Exported blendshape {1}".format(self, export_path))
            return export_path
        except RuntimeError:
            Logger.exception("{0}: Failed to export blendshape {1}".format(self, node))
            return False

    def import_single(self, bs_node):
        if not isinstance(bs_node, str):
            bs_node = str(bs_node)
        latest_path = self.get_latest_file(bs_node, full_path=True)
        if not latest_path:
            Logger.warning("{0}:No saved blendshape found {1}".format(self, bs_node))
            return False
        # Find existing geometry
        geometry = self.get_mapped_geometry(bs_node)
        if not geometry:
            Logger.error("{0}: Mapping missing for {1}".format(self, bs_node))
        if not pm.objExists(geometry):
            Logger.warning("{0}: Geometry {1} for shape {2} no longer exists, skipping...".format(self, geometry, bs_node))
            return False
        # Check if blendshape already exists and create one if not.
        geometry = pm.PyNode(geometry)  # type: luna_rig.nt.Shape
        if bs_node not in [str(node) for node in geometry.listHistory(type=self.DATA_TYPE)]:
            shape_node = pm.blendShape(geometry, n=bs_node, foc=1)  # type: luna_rig.nt.BlendShape
        else:
            shape_node = pm.PyNode(bs_node)  # type:  luna_rig.nt.BlendShape
        # Import data
        try:
            pm.blendShape(shape_node, e=1, ip=latest_path)
            Logger.info("{0}: Imported blendshape {1}".format(self, latest_path))
            return True
        except RuntimeError:
            Logger.exception("{0}: Failed to import blendshape {1}".format(self, latest_path))
            return False

    @classmethod
    def export_all(cls, under_group=static.CharacterMembers.geometry.value):
        bs_manager = cls()
        export_list = []
        export_list = deformerFn.list_deformers(cls.DATA_TYPE, under_group=under_group)
        for shape in export_list:
            bs_manager.export_single(shape)

    @classmethod
    def import_all(cls):
        bs_manager = cls()
        for bs_name in bs_manager.versioned_files.keys():
            bs_manager.import_single(bs_name)

    @classmethod
    def export_selected(cls):
        manager = cls()
        seleted = pm.selected(type=cls.DATA_TYPE)
        for bs_node in seleted:
            manager.export_single(bs_node)

    @classmethod
    def import_selected(cls):
        manager = cls()
        seleted = pm.selected(type=cls.DATA_TYPE)
        for bs_node in seleted:
            manager.import_single(bs_node)
