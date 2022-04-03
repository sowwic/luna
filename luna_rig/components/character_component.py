import pymel.core as pm
from luna import Logger
from luna import static
import luna_rig
import luna_rig.functions.animFn as animFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.outlinerFn as outlinerFn
import luna_rig.functions.rigFn as rigFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.jointFn as jointFn


class Character(luna_rig.Component):
    @property
    def root_control(self):
        return luna_rig.Control(self.pynode.rootCtl.listConnections()[0])

    @property
    def control_rig(self):
        node = self.pynode.controlRig.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def deformation_rig(self):
        node = self.pynode.deformationRig.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def geometry_grp(self):
        node = self.pynode.geometryGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def locators_grp(self):
        node = self.pynode.locatorsGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def world_locator(self):
        node = self.pynode.worldLocator.listConnections()[0]  # type:luna_rig.nt.Locator
        return node

    @property
    def util_grp(self):
        node = self.pynode.utilGrp.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def controls(self):
        return self.list_controls()

    @property
    def bind_joints(self):
        return self.list_bind_joints()

    @property
    def root_motion(self):
        connections = self.pynode.rootMotionJoint.listConnections(d=1)
        joint = connections[0] if connections else None  # type: luna_rig.nt.Joint
        return joint

    @property
    def clamped_size(self):
        size = max(self.get_size(axis="y") * 0.1, self.get_size(axis="x") * 0.1)
        return size

    @ property
    def actions_dict(self):
        actions = {}
        return actions

    # ======== Getter methods ========== #
    def get_root_control(self):
        return self.root_control

    def get_control_rig(self):
        return self.control_rig

    def get_deformation_rig(self):
        return self.deformation_rig

    def get_geometry_grp(self):
        return self.geometry_grp

    def get_locators_grp(self):
        return self.locators_grp

    def get_world_locator(self):
        return self.world_locator

    def get_util_grp(self):
        return self.util_grp

    def get_root_motion(self):
        return self.root_motion

    def get_clamped_size(self):
        return self.clamped_size

    @ classmethod
    def find(cls, name):
        result = []
        for character_node in cls.list_nodes(of_type=cls):
            if character_node.pynode.characterName.get() == name:
                result.append(character_node)
        if len(result) == 1:
            result = result[0]  # type: Character
        return result

    @classmethod
    def create(cls, meta_parent=None, name="character", tag="character"):
        """Creation method.

        :param meta_parent: Not used, defaults to None
        :type meta_parent: Component, optional
        :param name: Character name, defaults to "character"
        :type name: str, optional
        :return: New character instance.
        :rtype: Character
        """
        # Add message attrs to meta node
        instance = super(Character, cls).create(meta_parent, name=name, side="char", tag=tag)  # type: Character
        instance.pynode.addAttr("characterName", dt="string")
        instance.pynode.addAttr("rootCtl", at="message")
        instance.pynode.addAttr("controlRig", at="message")
        instance.pynode.addAttr("deformationRig", at="message")
        instance.pynode.addAttr("geometryGroup", at="message")
        instance.pynode.addAttr("locatorsGroup", at="message")
        instance.pynode.addAttr("worldLocator", at="message")
        instance.pynode.addAttr("utilGrp", at="message")
        instance.pynode.addAttr("rootMotionJoint", at="message")

        # Create main members
        root_control = luna_rig.Control.create(name="character_node",
                                               side="c",
                                               offset_grp=False,
                                               attributes="trs",
                                               shape="character_node",
                                               tag="root",
                                               orient_axis="y")
        root_control.rename(index="")
        control_rig = pm.createNode('transform', n=static.CharacterMembers.control_rig.value, p=root_control.transform)  # type: luna_rig.nt.Transform
        deformation_rig = pm.createNode('transform', n=static.CharacterMembers.deformation_rig.value, p=root_control.transform)  # type: luna_rig.nt.Transform
        locators_grp = pm.createNode('transform', n=static.CharacterMembers.locators.value, p=root_control.transform)  # type: luna_rig.nt.Transform
        world_locator = pm.spaceLocator(n=static.CharacterMembers.world_space.value)  # type: luna_rig.nt.Locator
        util_grp = pm.createNode('transform', n=static.CharacterMembers.util_group.value, p=root_control.transform)  # type: luna_rig.nt.Transform
        pm.parent(world_locator, locators_grp)

        # Handle geometry group
        if not pm.objExists(static.CharacterMembers.geometry.value):
            geometry_grp = pm.createNode('transform', n=static.CharacterMembers.geometry.value, p=root_control.transform)
        else:
            geometry_grp = pm.PyNode(static.CharacterMembers.geometry.value)
            pm.parent(geometry_grp, root_control.transform)
            geometry_grp.inheritsTransform.set(0)

        # Add meta parent attrs to nodes
        attrFn.add_meta_attr([control_rig,
                              deformation_rig,
                              geometry_grp,
                              locators_grp,
                              world_locator,
                              util_grp])

        # Connect to meta node
        instance.pynode.characterName.set(name)
        root_control.transform.metaParent.connect(instance.pynode.rootCtl)
        control_rig.metaParent.connect(instance.pynode.controlRig)
        deformation_rig.metaParent.connect(instance.pynode.deformationRig)
        geometry_grp.metaParent.connect(instance.pynode.geometryGroup)
        locators_grp.metaParent.connect(instance.pynode.locatorsGroup)
        world_locator.metaParent.connect(instance.pynode.worldLocator)
        util_grp.metaParent.connect(instance.pynode.utilGrp)

        # Edit attributes
        # Merge scale to make uniform
        root_control.transform.addAttr("Scale", defaultValue=1.0, shortName="us", at="float", keyable=1)
        root_control.transform.Scale.connect(root_control.transform.scaleX)
        root_control.transform.Scale.connect(root_control.transform.scaleY)
        root_control.transform.Scale.connect(root_control.transform.scaleZ)

        # Fit root control size
        instance.root_control.scale(instance.clamped_size, factor=1.0)

        # Visibility
        locators_grp.visibility.set(0)
        # Lock
        attrFn.lock(root_control.transform, ["sx", "sy", "sz"])
        instance.set_outliner_color(18)
        return instance

    def list_geometry(self):
        """List geometry nodes under geometry group.

        :return: List of nodes.
        :rtype: list[PyNode]
        """
        result = []
        for child in self.geometry_grp.listRelatives(ad=1):
            if isinstance(child, luna_rig.nt.Mesh):
                result.append(child)

        return result

    def list_controls(self, tag=None):
        ctls = []
        comp_list = self.get_meta_children()
        for comp in comp_list:
            if isinstance(comp, luna_rig.AnimComponent):
                ctls += comp.list_controls(tag)
        return ctls

    def list_bind_joints(self, by_tag=""):
        joint_list = []
        comp_list = self.get_meta_children(by_tag=by_tag)
        for comp in comp_list:
            if isinstance(comp, luna_rig.AnimComponent):
                joint_list += comp.bind_joints
        return joint_list

    def set_outliner_color(self, color):
        outlinerFn.set_color(self.root_control.group, color)

    def get_size(self, axis="y"):
        bounding_box = pm.exactWorldBoundingBox(self.geometry_grp, ii=True)
        if axis == "x":
            return bounding_box[3] - bounding_box[0]
        elif axis == "y":
            return bounding_box[4] - bounding_box[1]
        elif axis == "z":
            return bounding_box[5] - bounding_box[2]

    def save_bind_pose(self):
        Logger.info("Writing controls bind poses...")
        counter = 0
        ctls = rigFn.list_controls()
        for each in ctls:
            each.write_bind_pose()
            counter += 1
        Logger.info("Written {0} bind poses.".format(counter))

    def to_bind_pose(self):
        for ctl in self.list_controls():
            ctl.to_bind_pose()

    def get_nucleus(self):
        node = None
        nucleus_name = "{0}_nucl".format(self.name)
        nucleus_name = ":".join(self.namespace_list + [nucleus_name])
        if pm.objExists(nucleus_name):
            node = pm.PyNode(nucleus_name)  # type: luna_rig.nt.Nucleus
        return node

    def bake_to_skeleton(self, time_range=None):
        if not time_range:
            time_range = animFn.get_playback_range()
        Logger.info("{0}: Baking to skeleton {1}...".format(self, time_range))
        pm.bakeResults(self.bind_joints, time=time_range, simulation=True)

    def bake_and_detach(self, time_range=None):
        self.bake_to_skeleton(time_range=time_range)
        for anim_comp in self.get_meta_children(of_type=luna_rig.AnimComponent):
            anim_comp.detach_from_sekelton()

    def remove(self, time_range=None):
        # Bake root
        if self.root_motion:
            Logger.info("{0}: Baking root motion...".format(self))
            pm.bakeResults(self.root_motion, time=time_range, simulation=True)
        # Bake components
        self.bake_and_detach(time_range)
        # Remove rig
        for child in self.geometry_grp.getChildren():
            child.setParent(None)
        for child in self.deformation_rig.getChildren():
            child.setParent(None)
        pm.delete(self.root_control.group)
        self._delete_util_nodes()
        pm.delete(self.pynode)

    def set_interesting(self, value):
        for ctl in self.list_controls():
            for connected_node in ctl.transform.listConnections():
                connected_node.ihi.set(value)

    def add_root_motion(self, follow_object, root_joint=None, children=[]):
        # Process arguments
        if isinstance(follow_object, luna_rig.Control):
            follow_object = follow_object.transform
        if not root_joint:
            root_joint = jointFn.create_root_joint(parent=self.deformation_rig, children=children)
        elif not isinstance(root_joint, pm.PyNode):
            root_joint = pm.PyNode(root_joint)  # type: luna_rig.nt.Joint
            root_joint.setParent(self.deformation_rig)
        pm.pointConstraint(follow_object, root_joint, mo=1, skip="y")
        attrFn.add_meta_attr(root_joint)
        root_joint.metaParent.connect(self.pynode.rootMotionJoint)
        return root_joint

    def attach_to_skeleton(self):
        for comp in self.meta_children:
            comp.attach_to_skeleton()

    def create_controls_set(self, name="controls_set", tag=None):
        name = nameFn.add_namespaces(name, self.namespace_list)
        result = None
        if not pm.objExists(name):
            result = pm.sets([ctl.transform for ctl in self.list_controls(tag)], n=name)  # type: luna_rig.nt.ObjectSet
        else:
            result = pm.PyNode(name)
        return result

    def create_bind_joints_set(self, name="bind_joints_set"):
        name = nameFn.add_namespaces(name, self.namespace_list)
        result = None
        if not pm.objExists(name):
            result = pm.sets(self.list_bind_joints(), n=name)  # type: luna_rig.nt.ObjectSet
        else:
            result = pm.PyNode(name)
        return result

    def create_skeleton_set(self, name="skeleton_set"):
        name = nameFn.add_namespaces(name, self.namespace_list)
        result = None
        skel_joints = self.deformation_rig.listRelatives(type="joint", ad=True)
        if not pm.objExists(name):
            result = pm.sets(skel_joints, n=name)  # type: luna_rig.nt.ObjectSet
        else:
            result = pm.PyNode(name)
        return result

    def create_geometry_set(self, name="geometry_set"):
        name = nameFn.add_namespaces(name, self.namespace_list)
        result = None
        polygon_objects = [node for node in self.geometry_grp.listRelatives() if isinstance(node.getShape(), luna_rig.nt.Mesh)]
        if not pm.objExists(name):
            result = pm.sets(polygon_objects, n=name)  # type: luna_rig.nt.ObjectSet
        else:
            result = pm.PyNode(name)
        return result

    def create_selection_sets(self):
        ctl_set = self.create_controls_set()
        skel_set = self.create_skeleton_set()
        bind_jnt_set = self.create_bind_joints_set()
        geo_set = self.create_geometry_set()
        if not pm.objExists("rig_set"):
            rig_set = pm.sets([ctl_set, skel_set, bind_jnt_set, geo_set], n="rig_set")
        else:
            rig_set = pm.PyNode("rig_set")
        return rig_set

    def set_publish_mode(self, value):
        self.set_interesting(not value)
        rigFn.set_node_selectable(self.geometry_grp, not value)
        rigFn.set_node_selectable(self.deformation_rig, not value)
        self.deformation_rig.visibility.set(not value)
        self.util_grp.visibility.set(not value)
        self.create_selection_sets()

    def copy_keyframes(self, time_range, target_component, time_offset=0.0):
        for source_ctl in self.controls:
            for target_ctl in target_component.controls:
                if target_ctl.transform.stripNamespace() == source_ctl.transform.stripNamespace():
                    source_ctl.copy_keyframes(time_range, target_ctl, time_offset=time_offset)
