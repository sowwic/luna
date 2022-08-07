import pymel.core as pm

import luna_rig
from luna import Logger
import luna.utils.enumFn as enumFn
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.outlinerFn as outlinerFn
import luna_rig.functions.animFn as animFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.rigFn as rigFn


class Component(luna_rig.MetaNode):

    required_plugins = []

    def __new__(cls, node=None):
        return object.__new__(cls)

    def __init__(self, node):
        super(Component, self).__init__(node)

    @property
    def settings(self):
        """Component controls attrs to export/import

        :return: Dictionary of {attr: value}
        :rtype: dict
        """
        attr_dict = {}
        for connected_attr in self.pynode.settings.listConnections(d=1, plugs=1):
            attr_dict[str(connected_attr)] = connected_attr.get()
        return attr_dict

    @property
    def util_nodes(self):
        nodes = self.pynode.utilNodes.listConnections(d=1)  # type: list
        return nodes

    @ classmethod
    def create(cls, meta_parent, side="c", name="component", tag=""):
        """Creates instance of component

        :param meta_parent: Other Component to parent to.
        :type meta_parent: Component
        :param side: Component side, defaults to "c"
        :type side: str, optional
        :param name: Component name, defaults to "component"
        :type name: str, optional
        :return: New component instance.
        :rtype: Component
        """
        Logger.info("Building {0}({1}_{2})...".format(cls.as_str(name_only=True), side, name))
        Logger.info("Meta parent: {0}".format(meta_parent))
        cls.load_required_plugins()
        # Create instance, add attribs
        instance = super(Component, cls).create(meta_parent)  # type: Component
        instance.pynode.rename(nameFn.generate_name(name, side, suffix="meta"))
        instance.pynode.addAttr("settings", at="message", multi=1, im=0)
        instance.pynode.addAttr("utilNodes", at="message", multi=1, im=0)
        instance.set_tag(tag)

        return instance

    @classmethod
    def verify_parent_type(cls, parent, valid_types):
        if not isinstance(parent, valid_types):
            Logger.exception(
                "{0}: Invalid meta parent type - {1}. Valid types: {2}".format(cls.as_str(name_only=True), parent, valid_types))
            raise TypeError

    @classmethod
    def load_required_plugins(cls):
        for plugin_name in cls.required_plugins:
            if not pm.pluginInfo(plugin_name, q=True, loaded=True):
                try:
                    Logger.info('Loading plugin {0} required by {1}'.format(
                        plugin_name, cls.as_str(name_only=True)))
                    pm.loadPlugin(plugin_name, quiet=True)
                except Exception:
                    Logger.exception(
                        'Failed to load plugin {0} required by {1}'.format(plugin_name, cls))
                    raise

    def remove(self):
        pass

    def set_outliner_color(self, color):
        raise NotImplementedError

    def attach_to_component(self, other_comp):
        """Attach to other component

        :param other_comp: Other component
        :type other_comp: Component
        """
        if not isinstance(other_comp, Component):
            other_comp = luna_rig.MetaNode(other_comp)
        if other_comp.pynode not in self.pynode.metaParent.listConnections():
            self.set_meta_parent(other_comp)
            Logger.info("Meta parent set: {0} ->> {1}".format(self, other_comp))

    def _store_settings(self, attr):
        """Store given attribute as component setting

        :param attr: Node attribute
        :type attr: pymel.core.Attribute
        """
        # if not attr.isConnectedTo(self.pynode.settings, checkLocalArray=True, checkOtherArray=True):
        if not isinstance(attr, pm.PyNode):
            attr = pm.PyNode(attr)
        if attr not in self.pynode.settings.listConnections(d=1, plugs=1):
            attr.connect(self.pynode.settings, na=1)

    def _store_util_nodes(self, nodes):
        if not isinstance(nodes, list):
            nodes = [nodes]
        for each in nodes:
            if each not in self.util_nodes:
                each.message.connect(self.pynode.utilNodes, na=1)

    def _delete_settings_attrs(self):
        for source_attr in self.settings.keys():
            if pm.objExists(source_attr):
                pm.deleteAttr(source_attr)
                Logger.info("{0}: Deleted settings attribute - {1}".format(self, source_attr))
            else:
                Logger.error("{0}: Settings attr doesn't exist - {1}".format(self, source_attr))

    def _delete_util_nodes(self):
        for util_node in self.util_nodes:
            if isinstance(util_node, luna_rig.nt.DagNode):
                if util_node.numChildren():
                    try:
                        util_node.childAtIndex(0).setParent(util_node.getParent())
                    except RuntimeError:
                        Logger.warning("Failed to parent {0} children ({1}) to {2}".format(
                            util_node, util_node.getChildren(), util_node.getParent()))
            pm.delete(util_node)
            Logger.debug("{0}: Deleted util node {1}".format(self, util_node))

    def copy_keyframes(self, time_range, target_component, time_offset=0.0):
        pass


class AnimComponent(Component):

    @ classmethod
    def create(cls,
               meta_parent=None,
               side="c",
               name="anim_component",
               hook=None,
               character=None,
               tag=""):  # noqa:F821
        """Create AnimComponent hierarchy in the scene and instance.

        :param meta_parent: Other Rig element to connect to, defaults to None
        :type meta_parent: AnimComponent, optional
        :param side: Component side, used for naming, defaults to "c"
        :type side: str, optional
        :param name: Component name. If list - items will be connected by underscore, defaults to "anim_component"
        :type name: str, list[str], optional
        :param hook: Point index on parent component to attach to, defaults to 0
        :type hook: int, optional
        :return: New instance of AnimComponent.
        :rtype: AnimComponent
        """
        if not side:
            side = meta_parent.side
        instance = super(AnimComponent, cls).create(
            meta_parent, side, name, tag=tag)  # type: AnimComponent
        # Create hierarchy
        root_grp = pm.group(n=nameFn.generate_name(
            instance.name, instance.side, suffix="comp"), em=1)
        ctls_grp = pm.group(n=nameFn.generate_name(
            instance.name, instance.side, suffix="ctls"), em=1, p=root_grp)
        joints_grp = pm.group(n=nameFn.generate_name(
            instance.name, instance.side, suffix="jnts"), em=1, p=root_grp)
        parts_grp = pm.group(n=nameFn.generate_name(
            instance.name, instance.side, suffix="parts"), em=1, p=root_grp)
        noscale_grp = pm.group(n=nameFn.generate_name(
            instance.name, instance.side, suffix="noscale"), em=1, p=parts_grp)
        noscale_grp.inheritsTransform.set(0)
        out_grp = pm.group(n=nameFn.generate_name(
            instance.name, instance.side, suffix="out"), em=1, p=root_grp)
        out_grp.visibility.set(0)
        for node in [root_grp, ctls_grp, joints_grp, parts_grp, noscale_grp, out_grp]:
            node.addAttr("metaParent", at="message")

        # Add message attrs
        instance.pynode.addAttr("character", at="message")
        instance.pynode.addAttr("rootGroup", at="message")
        instance.pynode.addAttr("ctlsGroup", at="message")
        instance.pynode.addAttr("jointsGroup", at="message")
        instance.pynode.addAttr("partsGroup", at="message")
        instance.pynode.addAttr("noScaleGroup", at="message")
        instance.pynode.addAttr("outGroup", at="message")
        instance.pynode.addAttr("bindJoints", at="message", multi=1, im=0)
        instance.pynode.addAttr("ctlChain", at="message", multi=1, im=0)
        instance.pynode.addAttr("controls", at="message", multi=1, im=0)
        instance.pynode.addAttr("outHooks", at="message", multi=1, im=0)
        instance.pynode.addAttr("inHook", at="message")

        # Connect hierarchy to meta
        root_grp.metaParent.connect(instance.pynode.rootGroup)
        ctls_grp.metaParent.connect(instance.pynode.ctlsGroup)
        joints_grp.metaParent.connect(instance.pynode.jointsGroup)
        parts_grp.metaParent.connect(instance.pynode.partsGroup)
        noscale_grp.metaParent.connect(instance.pynode.noScaleGroup)
        out_grp.metaParent.connect(instance.pynode.outGroup)
        instance.set_outliner_color(17)
        # Connect to character
        instance.connect_to_character(character_component=character, parent=False)

        return instance

    @ property
    def root(self):
        node = self.pynode.rootGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @ property
    def group_ctls(self):
        node = self.pynode.ctlsGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @ property
    def group_joints(self):
        node = self.pynode.jointsGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @ property
    def group_parts(self):
        node = self.pynode.partsGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @ property
    def group_noscale(self):
        node = self.pynode.noScaleGroup.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @ property
    def group_out(self):
        node = self.pynode.outGroup.listConnections(d=1)[0]  # type: luna_rig.nt.Transform
        return node

    @ property
    def controls(self):
        # type: (list[luna_rig.nt.Transform]) -> list[luna_rig.Control]
        connected_nodes = self.pynode.controls.listConnections()
        all_ctls = [luna_rig.Control(node) for node in connected_nodes]
        return all_ctls

    @ property
    def bind_joints(self):
        joint_list = self.pynode.bindJoints.listConnections()  # type: list[luna_rig.nt.Joint]
        return joint_list

    @ property
    def ctl_chain(self):
        ctl_chain = self.pynode.ctlChain.listConnections()  # type: list[luna_rig.nt.Joint]
        return ctl_chain

    @ property
    def character(self):
        # type: () -> luna_rig.components.Character
        connections = self.pynode.character.listConnections()
        result = luna_rig.MetaNode(connections[0]) if connections else None
        return result

    @ property
    def out_hooks(self):
        hooks = [Hook(node) for node in self.pynode.outHooks.listConnections()]
        return hooks

    @ property
    def in_hook(self):
        connections = self.pynode.inHook.listConnections()
        result = Hook(connections[0]) if connections else None  # type: Hook
        return result

    @property
    def in_hook_index(self):
        hook = self.in_hook
        if hook:
            return hook.index
        return None

    @ property
    def actions_dict(self):
        actions = {}
        return actions

    # ========= Getter methods ========== #
    def get_root(self):
        return self.root

    def get_group_ctls(self):
        return self.group_ctls

    def get_group_joints(self):
        return self.group_joints

    def get_group_parts(self):
        return self.group_parts

    def get_group_noscale(self):
        return self.group_noscale

    def get_group_out(self):
        return self.group_out

    def get_controls(self):
        return self.controls

    def get_bind_joints(self):
        return self.bind_joints

    def get_ctl_chain(self):
        return self.ctl_chain

    def get_character(self):
        return self.character

    def get_in_hook(self):
        return self.in_hook

    def get_in_hook_index(self):
        return self.in_hook_index

    def get_hook_transform(self, hook_index):
        return self.get_hook(hook_index).transform

    def get_actions_dict(self):
        return self.actions_dict

    # ========= Other methods ========== #

    def set_outliner_color(self, color):
        # type: (list[float] | int | str) -> None
        outlinerFn.set_color(self.root, color)

    def _store_bind_joints(self, joint_chain):
        for jnt in joint_chain:
            if not isinstance(jnt, pm.PyNode):
                jnt = pm.PyNode(jnt)
            attrFn.add_meta_attr(jnt)
            if jnt not in self.pynode.bindJoints.listConnections(d=1):
                jnt.metaParent.connect(self.pynode.bindJoints, na=1)

    def _store_ctl_chain(self, joint_chain):
        for jnt in joint_chain:
            attrFn.add_meta_attr(jnt)
            if jnt not in self.pynode.ctlChain.listConnections(d=1):
                jnt.metaParent.connect(self.pynode.ctlChain, na=1)

    def _store_controls(self, ctl_list):
        for ctl in ctl_list:
            if ctl.transform not in self.pynode.controls.listConnections(d=1):
                ctl.transform.metaParent.connect(self.pynode.controls, na=1)

    def list_controls(self, tag=None):
        """Get list of component controls. Extra attr for tag sorting.

        :return: List of all component controls.
        :rtype: list[luna_rig.Control]
        """
        connected_nodes = self.pynode.controls.listConnections()
        all_ctls = [luna_rig.Control(node) for node in connected_nodes]
        if tag:
            tagged_list = [ctl for ctl in all_ctls if ctl.tag == tag]
            return tagged_list
        return all_ctls

    def select_controls(self, tag=None):
        # type: (str | None) -> None
        """Select all component controls"""
        for ctl in self.list_controls(tag):
            ctl.transform.select(add=1)

    def key_controls(self, tag=None):
        # type: (str | None) -> None
        """Override: key all components controls"""
        ctls = self.list_controls(tag)
        for each in ctls:
            pm.setKeyframe(each.transform)

    def attach_to_skeleton(self):
        """Override: attach to skeleton"""
        Logger.info("{0}: Attaching to skeleton...".format(self))
        for ctl_jnt, bind_jnt in zip(self.ctl_chain, self.bind_joints):
            if not self.character.IGNORE_EXISTING_CONSTRAINTS_ON_SKELETON_ATTACHMENT and bind_jnt.listConnections(type="parentConstraint"):
                Logger.info("Replacing {0} attachment to {1}".format(bind_jnt, ctl_jnt))
                pm.delete(bind_jnt.listConnections(type="parentConstraint"))
            pm.parentConstraint(ctl_jnt, bind_jnt, mo=1)

    def detach_from_skeleton(self):
        bind_joints_parent_constraints = set()
        ctl_joints_parent_constraints = set()

        for skel_jnt in self.bind_joints:
            bind_joints_parent_constraints.update(skel_jnt.listConnections(
                type="parentConstraint", destination=True))

        for ctl_joint in self.ctl_chain:
            ctl_joints_parent_constraints.update(
                ctl_joint.listConnections(type="parentConstraint", source=True))

        common_constraints = bind_joints_parent_constraints.intersection(
            ctl_joints_parent_constraints)
        Logger.debug("Deleting constraints: {}".format(common_constraints))
        for constr_node in common_constraints:
            pm.delete(constr_node)

        Logger.info("{0}: Detached from skeleton.".format(self))

    def bake_to_skeleton(self, time_range=None):
        # type: (tuple[int, int]) -> None
        """Override: bake animation to skeleton"""
        if not self.bind_joints:
            return
        if not time_range:
            time_range = animFn.get_playback_range()
        pm.bakeResults(self.bind_joints, time=time_range, simulation=True)
        Logger.info("{0}: Baked to skeleton.".format(self))

    def bake_and_detach(self, time_range=None):
        self.bake_to_skeleton(time_range)
        self.detach_from_skeleton()

    def bake_to_rig(self, time_range):
        """Override: reverse bake to rig"""
        pass

    def to_bind_pose(self):
        """Override: revert all controls to default values"""
        for ctl in self.controls:
            ctl.to_bind_pose()

    def remove(self):
        """Delete component from scene"""
        self.detach_from_skeleton()
        for child in self.meta_children:
            child.remove()
        pm.delete(self.root)
        self._delete_util_nodes()
        pm.delete(self.pynode)
        Logger.info("Removed {0}".format(self))

    def add_hook(self, node, name):
        # type: (pm.PyNode | str, str) -> Hook
        """Set given node as attach point

        :param node: Dag node
        :type node: str or pm.PyNode
        """
        hook = Hook.create(self, node, name)
        return hook

    def get_hook(self, index):
        # type: (int) -> Hook
        """Get component attach point from index

        :param index: Index for attach point, defaults to 0
        :type index: int or enumFn.Enum, optional
        :return: Attach point object.
        :rtype: pm.PyNode
        """
        if isinstance(index, enumFn.Enum):
            index = index.value
        elif isinstance(index, float):
            index = int(index)
        try:
            hook = self.out_hooks[index]
        except IndexError:
            raise
        return hook

    def copy_keyframes(self, time_range, target_component, time_offset=0.0):
        # type: (tuple[int, int], AnimComponent, float) -> None
        for source_ctl in self.controls:
            for target_ctl in target_component.controls:
                if target_ctl.transform.stripNamespace() == source_ctl.transform.stripNamespace():
                    source_ctl.copy_keyframes(time_range, target_ctl, time_offset=time_offset)

    def attach_to_component(self, other_comp, hook_index=None):
        # type: (AnimComponent, int) -> None
        """Attach to other AnimComponent

        :param other_comp: Component to attach to.
        :type other_comp: AnimComponent
        :param hook: Attach point index, defaults to 0
        :type hook: int, enumFn.Enum, optional
        :return: Attach object to use in derived method.
        :rtype: pm.PyNode
        """
        if not other_comp:
            return
        super(AnimComponent, self).attach_to_component(other_comp)
        if isinstance(hook_index, float):
            hook_index = int(hook_index)

        if hook_index is None:
            pass
        else:
            try:
                hook = other_comp.get_hook(index=hook_index)  # type: Hook
                hook.add_output(self)
            except Exception:
                Logger.error("Failed to connect {0} to {1} at point {2}".format(
                    self, other_comp, hook_index))
                raise

    def connect_to_character(self, character_component=None, character_name=None, parent=False):
        # type: (luna_rig.components.Character, str, bool) -> None
        """Connect component to character

        :param character_name: Specific character to connect to, defaults to ""
        :type character_name: str, optional
        """
        if not character_component:
            if character_name:
                all_characters = luna_rig.MetaNode.list_nodes(of_type=luna_rig.components.Character)
                if not all_characters:
                    raise RuntimeError("No characters found in the scene!")
                for char_node in all_characters:
                    if char_node.pynode.characterName.get() == character_name:
                        character_component = char_node
                        break
            else:
                character_component = rigFn.get_build_character()  # type: luna_rig.components.Character
        if not isinstance(character_component, luna_rig.components.Character):
            raise RuntimeError("{0} is not a valid Character".format(character_component))

        # Connect
        if self.pynode not in character_component.pynode.metaChildren.listConnections(d=1):
            self.pynode.character.connect(character_component.pynode.metaChildren, na=1)
        if parent:
            self.root.setParent(character_component.control_rig)

    def scale_controls(self, scale_dict):
        # type: (dict) -> None
        if self.character and self.character.clamped_size > 1.0:
            clamped_size = self.character.clamped_size
            Logger.debug(self.character.clamped_size)
        else:
            clamped_size = 1.0

        for ctl, factor in scale_dict.items():
            ctl.scale(clamped_size, factor=factor)


class Hook(object):

    def __repr__(self):
        return "Hook({0})".format(self.transform)

    def __eq__(self, other):
        if not isinstance(other, Hook):
            raise TypeError("Can't compare Hook and {0}".format(type(other)))
        return self.transform == other.transform

    def __init__(self, node):
        self.transform = node  # type: luna_rig.nt.Transform

    def add_output(self, anim_component):
        self.transform.children.connect(anim_component.pynode.inHook)
        Logger.info("{0} ->> {1}".format(self, anim_component))

    @classmethod
    def create(cls, anim_component, object_node, name):
        hook_transform = nodeFn.create("transform",
                                       [anim_component.indexed_name, name],
                                       anim_component.side,
                                       suffix="hook",
                                       p=anim_component.group_out)
        if not isinstance(object_node, pm.PyNode):
            object_node = pm.PyNode(object_node)

        pm.pointConstraint(object_node, hook_transform)
        pm.orientConstraint(object_node, hook_transform)

        # Attributes
        attrFn.add_meta_attr(hook_transform)
        hook_transform.addAttr("object", at="message")
        hook_transform.addAttr("children", at="message")
        object_node.message.connect(hook_transform.object)
        hook_transform.metaParent.connect(anim_component.pynode.outHooks, na=1)
        instance = cls(hook_transform)
        return instance

    @property
    def as_object(self):
        node = self.transform.object.listConnections(d=1)[0]  # type: luna_rig.nt.DependNode
        return node

    @property
    def component(self):
        comp_node = luna_rig.MetaNode(self.transform.metaParent.listConnections(s=1)[
                                      0])  # type: luna_rig.AnimComponent
        return comp_node

    @property
    def children(self):
        connections = self.transform.outputs.listConnections(s=1)
        return [luna_rig.MetaNode(conn) for conn in connections]

    @property
    def index(self):
        return self.component.out_hooks.index(self)
