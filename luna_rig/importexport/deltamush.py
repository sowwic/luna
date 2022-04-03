import pymel.core as pm

import luna_rig
from luna import Logger
import luna.utils.fileFn as fileFn
import luna_rig.functions.deformerFn as deformerFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.rigFn as rigFn
from luna_rig.importexport import manager as manager_base


class DeltaMushManager(manager_base.AbstractManager):

    DATA_TYPE = 'deltaMush'
    EXTENSION = 'json'
    EXTRA_ATTRIBS = ["smoothingIterations",
                     "smoothingStep",
                     "pinBorderVertices",
                     "inwardConstraint",
                     "outwardConstraint",
                     "distanceWeight",
                     "displacement"]

    @property
    def path(self):
        return self.asset.weights.delta_mush

    def get_base_name(self, node):
        return str(node)

    def get_new_file(self, node, full=True):
        return fileFn.get_new_versioned_file(self.get_base_name(node), dir_path=self.path, extension=self.EXTENSION, full_path=full)

    def get_latest_file(self, node, full=True):
        return fileFn.get_latest_file(self.get_base_name(node), self.path, extension=self.EXTENSION, full_path=full)

    def export_single(self, node):
        deformer = deformerFn.get_deformer(node, self.DATA_TYPE)
        if not deformer:
            Logger.warning('No deltaMush deformer in the history of {0}'.format(node))
            return
        new_file_name = self.get_new_file(node, full=False)
        deformerFn.init_painted(deformer)
        try:
            pm.deformerWeights(new_file_name, fm='JSON', path=self.path, deformer=deformer, attribute=self.EXTRA_ATTRIBS, ex=1, wp=5, wt=0.00001)
        except Exception:
            Logger.exception('Failed to export deltaMush weights for {0}'.format(node))

    def import_single(self, node_name, character):
        if not isinstance(node_name, str):
            node_name = str(node_name)
        latest_file = self.get_latest_file(node_name)
        deformer_attribs = deformerFn.get_attributes_from_json(latest_file)
        deformer = deformerFn.get_deformer(node_name, self.DATA_TYPE)
        # Create new deltamush if not found
        if not deformer:
            try:
                geo_name_parts = nameFn.deconstruct_name(node_name)
                deformer_name = "{0}_{1}_dms".format(geo_name_parts.side, geo_name_parts.indexed_name)
            except Exception:
                deformer_name = node_name + "_dms"
            deformer = pm.deltaMush(node_name, n=deformer_name)

        # Set deformer attributes a nd import weights
        for attr_name, attr_value in deformer_attribs.items():
            pm.setAttr('{0}.{1}'.format(deformer, attr_name), attr_value)
        pm.deformerWeights(self.get_latest_file(node_name, full=False), path=self.path, deformer=deformer, im=1, wp=5, wt=0.00001)
        # Connect to character scale
        for axis in 'XYZ':
            if not pm.isConnected(character.root_control.transform.Scale, '{0}.scale{1}'.format(deformer, axis)):
                character.root_control.transform.Scale.connect('{0}.scale{1}'.format(deformer, axis))
        Logger.info('Imported {0} deltaMush weights: {1}'.format(node_name, latest_file))

    @classmethod
    def export_all(cls):
        manager = cls()
        for deformer in deformerFn.list_deformers(cls.DATA_TYPE, under_group=None):
            for geometry in deformer.getGeometry():
                manager.export_single(pm.PyNode(geometry).getTransform())

    @classmethod
    def import_all(cls, character=None):
        manager = cls()
        character = character if character else rigFn.get_build_character()
        for geo in manager.versioned_files.keys():
            if pm.objExists(geo):
                manager.import_single(geo, character)

    @classmethod
    def export_selected(cls):
        manager = cls()
        for obj in pm.selected():
            manager.export_single(obj)

    @classmethod
    def import_selected(cls, character=None):
        manager = cls()
        character = character if character else rigFn.get_build_character()
        for obj in pm.selected():
            manager.import_single(obj, character)


if __name__ == "__main__":
    pass
    # DeltaMushManager.export_all()
    # DeltaMushManager.import_all()
