import os
import pymel.core as pm
from luna import Logger
import luna_rig
import luna.utils.fileFn as fileFn
from luna_rig.importexport import manager


class DrivenPoseManager(manager.AbstractManager):

    DATA_TYPE = 'pose'
    EXTENSION = 'json'

    @property
    def path(self):
        return self.asset.data.driven_poses

    def get_base_name(self, component_name, pose_name):
        return "{0}-{1}".format(component_name, pose_name)

    def get_new_file(self, node_name, pose_name):
        return fileFn.get_new_versioned_file(self.get_base_name(node_name, pose_name), self.path, extension=self.EXTENSION, full_path=True)

    def get_latest_file(self, node_name, pose_name):
        return fileFn.get_latest_file(self.get_base_name(node_name, pose_name), self.path, extension=self.EXTENSION, full_path=True)

    def export_pose(self, component_node, controls_list, driver_ctl, pose_name, driver_value=10.0):
        pose_dict = {}
        for control in controls_list:
            pose_dict[control.transform.name()] = {}
            for attr_name in ["rotate", "translate"]:
                attr_value = control.transform.attr(attr_name).get()
                if attr_value == pm.dt.Vector(0.0, 0.0, 0.0):
                    continue
                pose_dict[control.transform.name()][attr_name] = list(attr_value)
        pose_dict["driver"] = driver_ctl
        pose_dict["driver_value"] = driver_value
        export_path = self.get_new_file(component_node.pynode.name(), pose_name)
        fileFn.write_json(export_path, data=pose_dict)
        Logger.info("{0}: Exported {1} pose: {2}".format(self, component_node, export_path))

        return pose_dict

    def import_pose(self, component, pose_name):
        if isinstance(component, luna_rig.AnimComponent):
            component_node = component.pynode.name()
        else:
            component_node = component
        # Import data
        latest_file = self.get_latest_file(component_node, pose_name)
        pose_dict = fileFn.load_json(latest_file)  # type:dict
        driver_ctl = pose_dict.pop("driver")
        driver_value = pose_dict.get("driver_value", 10.0)
        if not pm.objExists(driver_ctl):
            Logger.error("{0}: Pose {1} driver {2} doesnt exist, skipping...".format(self, pose_name, driver_ctl))
            return
        # Add pose name to driver
        driver_ctl = pm.PyNode(driver_ctl)
        if not driver_ctl.hasAttr(pose_name):
            driver_ctl.addAttr(pose_name, at="float", k=True, dv=0.0, min=0, max=driver_value)

        # Create driven keys
        for transform, attr_dict in pose_dict.items():
            if not pm.objExists(transform):
                continue
            if not attr_dict:
                continue
            control = luna_rig.Control(transform)
            for attr, value_list in attr_dict.items():
                axis_dict = {attr + "X": value_list[0],
                             attr + "Y": value_list[1],
                             attr + "Z": value_list[2]}
                control.add_driven_pose(axis_dict, driver_ctl.attr(pose_name), driver_value)
        Logger.info("{0}: Imported {1} pose: {2}".format(self, component, latest_file))

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
        for component in luna_rig.MetaNode.list_nodes(of_type=luna_rig.AnimComponent):
            pose_manager.import_component_poses(component)
