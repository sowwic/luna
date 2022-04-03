import os
import pymel.core as pm
from luna import Logger
import luna_rig
import luna.utils.fileFn as fileFn
from luna_rig.importexport import manager


class SDKCorrectiveManager(manager.AbstractManager):

    DATA_TYPE = 'corrective'
    EXTENSION = 'json'

    @property
    def path(self):
        return self.asset.data.sdk_correctives

    def get_base_name(self, component_name, pose_name):
        return "{0}-{1}".format(component_name, pose_name)

    def get_new_file(self, node_name, pose_name):
        return fileFn.get_new_versioned_file(self.get_base_name(node_name, pose_name), self.path, extension=self.EXTENSION, full_path=True)

    def get_latest_file(self, node_name, pose_name):
        return fileFn.get_latest_file(self.get_base_name(node_name, pose_name), self.path, extension=self.EXTENSION, full_path=True)

    def export_pose(self, corrective_component, pose_name, driver, control_filter_list=[]):
        pose_dict = corrective_component.get_pose_dict()  # type: dict
        export_path = self.get_new_file(corrective_component.pynode.name(), pose_name)
        for corr_control in pose_dict.keys():
            if control_filter_list and corr_control not in control_filter_list:
                pose_dict.pop(corr_control)
                continue
        pose_dict["driver"] = driver
        pose_dict["driver_value"] = pm.getAttr(driver)
        fileFn.write_json(export_path, data=pose_dict, sort_keys=False)
        Logger.info("{0}: Exported {1} pose {2}".format(self, corrective_component, export_path))

    def import_pose(self, corrective_component, pose_name):
        if isinstance(corrective_component, luna_rig.AnimComponent):
            corrective_component = corrective_component.pynode.name()
        latest_file = self.get_latest_file(corrective_component, pose_name)
        pose_dict = fileFn.load_json(latest_file)  # type: dict#
        driver_attr = pose_dict.pop("driver")
        driver_value = pose_dict.pop("driver_value", 0.0)
        if not pm.objExists(driver_attr):
            Logger.warning("{0}: Driver attr {1} no longer exists".format(self, driver_attr))
            return

        for corr_control_name in pose_dict.keys():
            if not pm.objExists(corr_control_name):
                Logger.warning("{0}: Control {1} no longer exists, skipping...".format(self, corr_control_name))
                continue
            control = luna_rig.Control(corr_control_name)
            for attr, value_list in pose_dict[corr_control_name].items():
                axis_dict = {attr + "X": value_list[0],
                             attr + "Y": value_list[1],
                             attr + "Z": value_list[2]}
                control.add_driven_pose(axis_dict, pm.PyNode(driver_attr), driver_value)
        Logger.info("{0}: Imported {1} pose: {2}".format(self, corrective_component, latest_file))

    def import_component_poses(self, component_node):
        if isinstance(component_node, luna_rig.AnimComponent):
            component_node = component_node.pynode.name()
        for pose_path in fileFn.get_latest_from_sub_name(component_node, self.path, extension=self.EXTENSION, sub_index=0, sub_split="-"):
            file_name = os.path.basename(pose_path)
            pose_name = file_name.split(".")[0].replace(component_node + "-", "")
            self.import_pose(component_node, pose_name)

    @classmethod
    def import_all(cls):
        pose_manager = cls()
        for component in luna_rig.MetaNode.list_nodes(of_type=luna_rig.components.CorrectiveComponent):
            pose_manager.import_component_poses(component)
