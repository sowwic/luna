import pymel.core as pm
import luna_rig
from luna import Logger
import luna.utils.fileFn as fileFn
from luna_rig.importexport import manager as manager_base
from luna_rig.importexport import BlendShapeManager


class PsdManager(manager_base.AbstractManager):

    DATA_TYPE = 'psd'
    EXTENSION = 'pose'

    @property
    def path(self):
        return self.asset.data.psd

    def get_base_name(self):
        return self.asset.name

    def get_latest_file(self):
        return fileFn.get_latest_file(self.get_base_name(), self.path, extension=self.EXTENSION, full_path=True)

    def get_new_file(self):
        return fileFn.get_new_versioned_file(self.get_base_name(), self.path, extension=self.EXTENSION, full_path=True)

    @classmethod
    def export_all(cls):
        psd_manager = cls()
        interpolators = pm.ls(typ="poseInterpolator")
        if not interpolators:
            pm.warning("{0}: No pose interpolators found in the scene.".format(psd_manager))
            return False
        # Export pose blendshapes
        pose_blendshapes = []
        for pose_node in interpolators:
            connected_bs_nodes = pose_node.output.listConnections(s=1, type="blendShape")
            for bs_node in connected_bs_nodes:
                if bs_node not in pose_blendshapes:
                    pose_blendshapes.append()
        bs_manager = BlendShapeManager()
        for bs_node in pose_blendshapes:
            bs_manager.export_single(bs_node)
        # Export interpolators
        export_path = psd_manager.get_new_file()
        pm.poseInterpolator(interpolators, e=1, ex=export_path)
        Logger.info("{0}: Exported pose interpolators: {1}".format(psd_manager, export_path))
        return export_path

    @classmethod
    def import_all(cls):
        psd_manager = cls()
        interpolator_file = psd_manager.get_latest_file()
        if not interpolator_file:
            pm.warning("No interpolators to import", noContext=True)
            return False
        pm.poseInterpolator(im=interpolator_file)
        for interpolator_shape in pm.ls(typ="poseInterpolator"):
            driver = interpolator_shape.getTransform().driver.listConnections()[0]
            driver_parent_component = luna_rig.MetaNode.get_connected_metanode(driver)
            if driver_parent_component:
                pm.parent(interpolator_shape.getTransform(), driver_parent_component.character.util_grp)
        Logger.info("{0}: Imported pose interpolators: {1}".format(psd_manager, interpolator_file))
