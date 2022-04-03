
import json
import pymel.core as pm
from luna import Logger
from luna import Config
from luna import RigVars
from luna import static
import luna_rig
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.attrFn as attrFn
import luna_rig.functions.curveFn as curveFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.functions.transformFn as transformFn
import luna_rig.functions.outlinerFn as outlinerFn
import luna_rig.functions.animFn as animFn
from luna_rig.core.shape_manager import ShapeManager


class Control(object):

    def __repr__(self):
        return "Control({0})".format(self.transform)

    def __init__(self, node):
        # Type casting
        if isinstance(node, Control):
            node = node.transform
        if not isinstance(node, pm.PyNode):
            node = pm.PyNode(node)

        # Find transform
        if isinstance(node, luna_rig.nt.Controller):
            self.transform = node.controllerObject.listConnections()[0]  # type: luna_rig.nt.Transform
        elif isinstance(node, luna_rig.nt.Transform):
            self.transform = pm.PyNode(node)  # type: luna_rig.nt.Transform
        elif isinstance(node, luna_rig.nt.Shape):
            self.transform = node.getTransform()  # type: luna_rig.nt.Transform
        else:
            raise TypeError("Control requires node with transform to initialize.")

        if not self.is_control(self.transform):
            Logger.error("Invalid control transform - {0}".format(self))
            raise TypeError

    @classmethod
    def create(cls,
               name="control_obj",
               side="c",
               guide=None,
               parent=None,
               attributes="tr",
               delete_guide=False,
               match_pos=True,
               match_orient=True,
               match_pivot=True,
               color=None,
               offset_grp=True,
               joint=False,
               shape="cube",
               tag="",
               component=None,
               orient_axis="x",
               scale=1.0):
        """Control creation method

        :param name: Control name, defaults to "control_obj"
        :type name: str, optional
        :param side: Control side, defaults to "c"
        :type side: str, optional
        :param guide: Transform object to match, defaults to None
        :type guide: pm.luna_rig.nt.Transform, optional
        :param parent: Object to parent to, defaults to None
        :type parent: pm.luna_rig.nt.Transform, optional
        :param attributes: Attributes to leave unlocked and visible, defaults to "tr"
        :type attributes: str, optional
        :param delete_guide: If guide object should be deleted after matched, defaults to False
        :type delete_guide: bool, optional
        :param match_pos: If Control position should be matched to guide object, defaults to True
        :type match_pos: bool, optional
        :param match_orient: If Control rotation values should be matched to guide object, defaults to True
        :type match_orient: bool, optional
        :param match_pivot: If Control pivot should match guide object, defaults to True
        :type match_pivot: bool, optional
        :param color: Control color, if not set will use color based on side, defaults to None
        :type color: int, enumFn.Enum, optional
        :param offset_grp: If offset group should be created, defaults to True
        :type offset_grp: bool, optional
        :param joint: If control joint should be created, defaults to False
        :type joint: bool, optional
        :param shape: Desired control shape from shape lib, defaults to "cube"
        :type shape: str, optional
        :param tag: Additional tag to set on tag node, defaults to ""
        :type tag: str, optional
        :param component: Connect to component.pynode.controls on creation, defaults to None
        :type component: AnimComponent
        :param: orient_axis: Control orientation. Valid values: ("x", "y", "z"), defaults to "x"
        :type orient_axis: str
        :param scale: Control scale, defaults to 1.0
        :type scale: float, optional
        :return: Control instance
        :rtype: Control
        """
        # Group
        offset_node = None
        ctl_joint = None
        if isinstance(parent, Control):
            temp_parent = parent.transform
        elif isinstance(parent, str) and parent:
            parent = pm.PyNode(parent)
            temp_parent = parent
        else:
            temp_parent = parent

        group_node = pm.createNode('transform', n=nameFn.generate_name(name, side, suffix="grp"), p=temp_parent)
        temp_parent = group_node
        if guide:
            pm.matchTransform(group_node, guide, pos=match_pos, rot=match_orient, piv=match_pivot)
            if delete_guide:
                pm.delete(guide)
        # Offset
        if offset_grp:
            offset_node = pm.createNode('transform', n=nameFn.generate_name(name, side, suffix="ofs"), p=temp_parent)
            temp_parent = offset_node

        # Transform
        transform_node = pm.createNode('transform', n=nameFn.generate_name(name, side, suffix="ctl"), p=temp_parent)
        temp_parent = transform_node

        # Joint
        if joint:
            ctl_joint = pm.createNode('joint', n=nameFn.generate_name(name, side, suffix="cjnt"), p=temp_parent)
            ctl_joint.visibility.set(0)

        # Tag node
        pm.controller(transform_node)
        tag_node = transform_node.listConnections(t="controller")[0]  # type: luna_rig.nt.Controller
        tag_node.addAttr("group", at="message")
        tag_node.addAttr("offset", at="message", multi=1, im=0)
        tag_node.addAttr("joint", at="message")
        tag_node.addAttr("tag", dt="string")
        tag_node.addAttr("bindPose", dt="string", keyable=False)
        tag_node.bindPose.set(json.dumps({}))
        tag_node.bindPose.lock()
        tag_node.tag.set(tag)
        # Add meta parent attribs
        for node in [group_node, offset_node, transform_node, ctl_joint]:
            if node:
                node.addAttr("metaParent", at="message")

        # Connect to tag node
        group_node.metaParent.connect(tag_node.group)
        if offset_node:
            offset_node.metaParent.connect(tag_node.offset, na=1)
        if ctl_joint:
            ctl_joint.metaParent.connect(tag_node.joint)
        if isinstance(parent, Control):
            child_index = len(parent.tag_node.children.listConnections())
            tag_node.parent.connect(parent.tag_node.children[child_index])

        # Create instance
        instance = Control(transform_node)
        instance.shape = shape
        instance.color = color
        instance.set_outliner_color(27)
        ShapeManager.set_line_width(instance.transform, Config.get(RigVars.line_width, default=2.0, cached=True))
        # Attributes
        instance.lock_attrib(exclude_attr=attributes, channel_box=False)

        # Adjust shape
        instance.scale(scale, factor=0.8)
        instance.orient_shape(direction=orient_axis)
        # Connect to component
        if component:
            component._store_controls((instance))

        return instance

    @property
    def namespace_list(self):
        return nameFn.deconstruct_name(self.transform).namespaces

    @property
    def name(self):
        """Name part of control's name

        :return: Name
        :rtype: str
        """
        return nameFn.deconstruct_name(self.transform).name

    @property
    def indexed_name(self):
        return nameFn.deconstruct_name(self.transform).indexed_name

    @property
    def side(self):
        """Control side as string.

        :return: Side
        :rtype: str
        """
        return nameFn.deconstruct_name(self.transform).side

    @property
    def index(self):
        """Index value of control as string

        :return: Index
        :rtype: str
        """
        return nameFn.deconstruct_name(self.transform).index

    @property
    def tag(self):
        """Value of tag_node.tag attribute

        :return: Tag text
        :rtype: str
        """
        value = self.tag_node.tag.get()  # type: str
        return value

    @property
    def tag_node(self):
        """Controller node

        :return: Control tag node as instance.
        :rtype: luna_rig.nt.Controller
        """
        node = self.transform.listConnections(t="controller")[0]  # type: luna_rig.nt.Controller
        return node

    @property
    def group(self):
        """Control's root group

        :return: Group
        :rtype: luna_rig.nt.Transform
        """
        node = self.tag_node.group.listConnections()[0]  # type: luna_rig.nt.Transform
        return node

    @property
    def joint(self):
        """Joint parented under Control.transform

        :return: Joint
        :rtype: luna_rig.nt.Joint
        """
        result = None  # type: luna_rig.nt.Joint
        child_joints = self.tag_node.joint.listConnections()
        if child_joints:
            result = child_joints[0]  # type: luna_rig.nt.Joint
        return result

    @property
    def offset(self):
        """Get offset above transform node

        :return: Offset node
        :rtype: luna_rig.nt.Transform
        """
        all_offsets = self.offset_list
        result = None  # type: luna_rig.nt.Transform
        if all_offsets:
            result = all_offsets[-1]  # type: luna_rig.nt.Transform
        else:
            result = None  # type: luna_rig.nt.Transform
        return result

    @property
    def offset_list(self):
        """List of controls offsets. Newly inserted offsets are appended at the end of the list.

        :return: List of transform nodes
        :rtype: list, luna_rig.nt.Transform
        """
        offsets = self.tag_node.offset.listConnections()  # type: list
        return offsets

    @property
    def color(self):
        """Control color as color index

        :return: Control color.
        :rtype: int
        """
        return ShapeManager.get_color(self.transform)

    @color.setter
    def color(self, value):
        """Set control color by passing color index

        :param value: Color index
        :type value: int
        """
        if not value:
            value = static.SideColor[self.side].value
        ShapeManager.set_color(self.transform, value)

    @property
    def shape(self):
        """Control shape as dictionary

        :return: Control shape.
        :rtype: dict
        """
        return ShapeManager.get_shapes(self.transform)

    @shape.setter
    def shape(self, name):
        """Set control shape by passing shape name.

        :param name: Shape name
        :type name: str
        """
        ShapeManager.set_shape_from_lib(self.transform, name)

    @property
    def bind_pose(self):
        """Control bind pose as dictionary

        :return: Bind pose.
        :rtype: dict
        """
        pose_dict = {}
        if pm.hasAttr(self.tag_node, "bindPose"):
            pose_dict = json.loads(self.tag_node.bindPose.get())
        else:
            Logger.warning("{0}: missing bind pose!".format(self))
        return pose_dict

    @property
    def pose(self):
        pose_dict = {}
        attributes = pm.listAttr(self.transform, k=1, u=1) + pm.listAttr(self.transform, cb=1, u=1)
        for attr in attributes:
            if not pm.listConnections("{0}.{1}".format(self.transform, attr), s=1, d=0):
                pose_dict[attr] = pm.getAttr("{0}.{1}".format(self.transform, attr))
        return pose_dict

    @property
    def spaces(self):
        result = []
        if self.transform.hasAttr("space"):
            result = attrFn.get_enums(self.transform.space)
        return result

    @property
    def spaces_dict(self):
        result = {}
        if self.transform.hasAttr("space"):
            for space_name, space_index in attrFn.get_enums(self.transform.space):
                result[space_name] = space_index
        return result

    @property
    def space_index(self):
        result = None
        if self.transform.hasAttr("space"):
            result = self.transform.space.get()  # type: int
        return result

    @property
    def space_name(self):
        result = None
        if self.transform.hasAttr("space"):
            index = self.transform.space.get()  # type: int
            result = self.spaces[index][0]
        return result

    @property
    def connected_component(self):
        """Get component this control is connected to via metaParent attribute of Control.transform

        :return: [description]
        :rtype: [type]
        """
        result = None
        connections = self.transform.metaParent.listConnections()
        for node in connections:
            if not luna_rig.MetaNode.is_metanode(node):
                Logger.warning("Strange connection on {0}.metaParent: {1}".format(self, node))
                continue
            result = luna_rig.MetaNode(node)  # type: luna_rig.AnimComponent
        return result

    @property
    def character(self):
        comp = self.connected_component
        if not comp:
            Logger.warning("{0}: Failed to find connected component!".format(self))
            return None
        char = comp if isinstance(comp, luna_rig.components.Character) else comp.character  # type: luna_rig.components.Character
        return char

    # ======== Getter methods ============ #
    def get_tag(self):
        return self.tag

    def get_joint(self):
        return self.joint

    def get_connected_component(self):
        return self.connected_component

    def get_character(self):
        return self.character

    def get_transform(self):
        return self.transform

    @classmethod
    def is_control(cls, node):
        """Test if specified node is a controller

        :param node: Node to test
        :type node: str or luna_rig.nt.Transform
        :return: Test result
        :rtype: bool
        """
        if not isinstance(node, pm.PyNode):
            node = pm.PyNode(node)
        result = all([pm.controller(node, q=1, ic=1), node.hasAttr("metaParent")])
        return result

    def print_debug(self):
        """Print control debug information"""
        Logger.debug("""========Control instance========
                tree:
                -group: {0}
                -offset_list: {1}
                -offset: {2}
                -transform: {3}
                -joint: {4}
                -tag_node: {5}
                -shape: {6}
                -bind pose {7}

                data:
                -side: {8}
                -name: {9}
                        """.format(self.group, self.offset_list, self.offset, self.transform, self.joint, self.tag_node, self.shape, self.bind_pose,
                                   self.side, self.name))

    def set_tag(self, value_str):
        self.tag_node.tag.set(value_str)

    def set_outliner_color(self, color):
        outlinerFn.set_color(self.transform, color)

    def scale(self, scale, factor=0.8):
        if scale == 1.0 and factor == 1.0:
            return
        for each in self.transform.getShapes():
            pm.scale(each + ".cv[0:1000]", [factor * scale, factor * scale, factor * scale], objectSpace=True)

    def move_shape(self, vector):
        for each in self.transform.getShapes():
            pm.move(each + ".cv[0:1000]", vector, r=1)

    def set_parent(self, parent):
        """Set control parent

        :param parent: Parent to set, if None - will be parented to world.
        :type parent: pm.PyNode
        """
        if isinstance(parent, Control):
            connect_index = len(parent.tag_node.children.listConnections(d=1))
            self.tag_node.parent.connect(parent.tag_node.children[connect_index])
            parent = parent.transform
        else:
            parent.message.connect(self.tag_node.parent, f=1)

        if not isinstance(parent, pm.PyNode):
            parent = pm.PyNode(parent)
        pm.parent(self.group, parent)

    def get_parent(self, generations=1):
        """Get current parent

        :return: Parent node
        :rtype: pm.PyNode
        """
        return self.group.getParent(generations=generations)

    def lock_attrib(self, exclude_attr, channel_box=False):
        """Lock attributes on transform node

        :param exclude_attr: Attributes to leave unlocked
        :type exclude_attr: list
        :param channel_box: If locked attributes should be present in channel box, defaults to False
        :type channel_box: bool, optional
        """
        to_lock = ['tx', 'ty', 'tz',
                   'rx', 'ry', 'rz',
                   'sx', 'sy', 'sz',
                   'v']
        exclude_attr = list(exclude_attr)

        for attr in exclude_attr:
            if attr in list("trs"):
                for axis in "xyz":
                    to_lock.remove(attr + axis)
            else:
                to_lock.remove(attr)

        attrFn.lock(self.transform, to_lock, channel_box)

    def insert_offset(self, extra_name="extra"):
        """Inserts extra ofset node and inbetween transform and last offset node present.

        :param extra_name: name to add to new offset node, defaults to "extra"
        :type extra_name: str, optional
        :return: Created node
        :rtype: pm.PyNode
        """
        Logger.debug("{0} - Inserting offset with extra name: {1}".format(self, extra_name))
        if self.offset_list:
            parent = self.offset
        else:
            parent = self.group
        if extra_name:
            new_name = "_".join([self.indexed_name, extra_name])
        new_offset = pm.createNode("transform", n=nameFn.generate_name(new_name, side=self.side, suffix="ofs"), p=parent)  # type: luna_rig.nt.Transform
        pm.parent(self.transform, new_offset)
        new_offset.addAttr("metaParent", at="message")
        new_offset.metaParent.connect(self.tag_node.offset, na=1)
        return new_offset

    def find_offset(self, extra_name):
        result = None
        for offset_node in self.offset_list:
            if extra_name in nameFn.deconstruct_name(offset_node).name:
                result = offset_node  # type: luna_rig.nt.Transform
                break
        return result

    def mirror_shape(self, behaviour=True, flip=False, flip_across="yz"):
        """Mirrors control's shape
        """
        curveFn.mirror_shape(self.transform, behaviour=behaviour, flip=flip, flip_across="yz")

    def mirror_shape_to_opposite(self, behaviour=True, across="yz", flip=False, flip_across="yz"):
        opposite_ctl = self.find_opposite()
        if not opposite_ctl:
            Logger.warning("{0}: No opposite control was found.".format(self))
            return
        old_color = opposite_ctl.color
        ShapeManager.apply_shape(opposite_ctl.transform, self.shape)
        opposite_ctl.mirror_shape(behaviour=behaviour, flip=flip, flip_across=flip_across)
        opposite_ctl.color = old_color

    def add_space(self, target, name, via_matrix=True):
        # Process inputs
        if pm.about(api=1) < 20200100 and via_matrix:
            Logger.warning("Matrix space method requires Maya 2020+. Using constraint method instead.")
            via_matrix = False

        # Add divider if matrix
        if via_matrix and not self.transform.hasAttr("SPACE_SWITCHING"):
            attrFn.add_divider(self.transform, "SPACE_SWITCHING")

        if isinstance(target, Control):
            target = target.transform
        else:
            target = pm.PyNode(target)
        if not isinstance(target, luna_rig.nt.Transform):
            Logger.error("{0}: Can't add space to not transform {1}".format(self, target))
            raise ValueError

        # Add space attribute
        if not self.transform.hasAttr("space"):
            self.transform.addAttr("space", at="enum", keyable=True, en=["NONE"])

        # Check if enum name already exists
        existing_enums = attrFn.get_enums(self.transform.space)
        enum_names = [enum[0] for enum in existing_enums]
        if name in enum_names:
            Logger.exception("{0}: space with name {1} already exists.".format(self, name))
            return
        if "NONE" in enum_names:
            enum_names.remove("NONE")

        # Add enum value
        enum_names.append(name)
        pm.setEnums(self.transform.attr("space"), enum_names)

        # Create switch logic
        if via_matrix:
            self.__add_matrix_space(target, name)
        else:
            self.__add_constr_space(target, name)
        # Store as component setting
        if self.connected_component:
            self.connected_component._store_settings(self.transform.space)
            if via_matrix:
                self.connected_component._store_settings(self.transform.spaceUseTranslate)
                self.connected_component._store_settings(self.transform.spaceUseRotate)
                self.connected_component._store_settings(self.transform.spaceUseScale)
        Logger.info("{0}: added space {1}".format(self, target))

    def __add_matrix_space(self, target, name):
        """Add space using matrix method\n
        Based on https://www.chadvernon.com/blog/space-switching-offset-parent-matrix/
        :param target: target space
        :type target: PyNode
        :param name: Space name
        :type name: str
        """
        # Add ctl attrs
        if not self.transform.hasAttr("spaceUseTranslate"):
            self.transform.addAttr("spaceUseTranslate", at="bool", dv=True, k=1)
        if not self.transform.hasAttr("spaceUseRotate"):
            self.transform.addAttr("spaceUseRotate", at="bool", dv=True, k=1)
        if not self.transform.hasAttr("spaceUseScale"):
            self.transform.addAttr("spaceUseScale", at="bool", dv=True, k=1)

        # Get offset matrix
        mult_mtx = pm.createNode("multMatrix", n=nameFn.generate_name([self.indexed_name, name.lower()], side=self.side, suffix="mmtx"))
        offset_mtx = transformFn.matrix_to_list(self.transform.worldMatrix.get() * self.transform.matrix.get().inverse() * target.worldInverseMatrix.get())
        mult_mtx.matrixIn[0].set(offset_mtx)
        target.worldMatrix.connect(mult_mtx.matrixIn[1])
        self.transform.getParent().worldInverseMatrix.connect(mult_mtx.matrixIn[2])
        index = len(self.spaces) - 1
        # Condition
        condition = pm.createNode("condition", n=nameFn.generate_name([self.indexed_name, name.lower()], side=self.side, suffix="cond"))
        condition.secondTerm.set(index)
        condition.colorIfTrueR.set(1)
        condition.colorIfFalseR.set(0)
        self.transform.space.connect(condition.firstTerm)
        # Blend matrix
        blend_name = "{0}_{1}_space_00_blend".format(self.side, self.indexed_name)
        if not pm.objExists(blend_name):
            blend_mtx = pm.createNode("blendMatrix", n=blend_name)
        else:
            blend_mtx = pm.PyNode(blend_name)

        condition.outColorR.connect(blend_mtx.target[index].weight)
        mult_mtx.matrixSum.connect(blend_mtx.target[index].targetMatrix)
        if not self.transform.offsetParentMatrix.isConnected():
            blend_mtx.outputMatrix.connect(self.transform.offsetParentMatrix)
        self.transform.spaceUseTranslate.connect(blend_mtx.target[index].useTranslate)
        self.transform.spaceUseRotate.connect(blend_mtx.target[index].useRotate)
        self.transform.spaceUseScale.connect(blend_mtx.target[index].useScale)

    def __add_constr_space(self, target, name):
        # Space offset
        space_offset = self.find_offset("space")
        if not space_offset:
            space_offset = self.insert_offset(extra_name="space")
        # Create space transforms
        space_node = pm.createNode("transform", n=nameFn.generate_name([self.indexed_name, name.lower()], side=self.side, suffix="space"), p=self.transform)
        pm.parent(space_node, world=True)
        parent_constr = pm.parentConstraint(space_node, space_offset)
        # Condition node
        condition = pm.createNode("condition", n=nameFn.generate_name([self.indexed_name, name.lower()], side=self.side, suffix="cond"))
        self.transform.space.connect(condition.firstTerm)
        condition.secondTerm.set(len(parent_constr.getTargetList()) - 1)
        condition.colorIfTrueR.set(1)
        condition.colorIfFalseR.set(0)
        condition.outColorR.connect(parent_constr.getWeightAliasList()[-1])
        pm.parent(space_node, target)

    def add_world_space(self, via_matrix=True):
        """Uses add space method to add space to hidden world locator
        """
        self.add_space(self.character.world_locator, "World", via_matrix)

    def switch_space(self, index, matching=True):
        if not self.transform.hasAttr("space"):
            return
        if index > len(self.spaces) - 1:
            Logger.warning("{0} - Space index {1} out of bounds.".format(self, index))
            return
        mtx = self.transform.getMatrix(worldSpace=True)
        self.transform.space.set(index)
        if matching:
            self.transform.setMatrix(mtx, worldSpace=True)

    def add_wire(self, source):
        """Adds staight line curve connecting source object and controls' transform

        :param source: Wire source object
        :type source: str or luna_rig.nt.Transform
        """
        # Curve
        curve_points = [source.getTranslation(space="world"), self.transform.getTranslation(space="world")]
        wire_curve = curveFn.curve_from_points(name=nameFn.generate_name([self.indexed_name, "wire"], side=self.side, suffix="crv"), degree=1, points=curve_points)
        wire_curve.inheritsTransform.set(0)
        # Clusters
        src_cluster = pm.cluster(wire_curve.getShape().controlPoints[0], n=nameFn.generate_name([self.indexed_name, "wire", "src"], side=self.side, suffix="clst"))
        dest_cluster = pm.cluster(wire_curve.getShape().controlPoints[1], n=nameFn.generate_name([self.indexed_name, "wire", "dest"], side=self.side, suffix="clst"))
        pm.pointConstraint(source, src_cluster, n=nameFn.generate_name([self.indexed_name, "wire", "src"], side=self.side, suffix="ptcon"))
        pm.pointConstraint(self.transform, dest_cluster, n=nameFn.generate_name([self.indexed_name, "wire", "dest"], side=self.side, suffix="ptcon"))
        # Grouping
        wire_grp = pm.group(src_cluster, dest_cluster, n=nameFn.generate_name([self.indexed_name, "wire"], side=self.side, suffix="grp"))
        pm.parent(wire_curve, wire_grp)
        pm.parent(wire_grp, self.group)
        # Housekeeping
        src_cluster[1].visibility.set(0)
        dest_cluster[1].visibility.set(0)
        wire_curve.getShape().overrideEnabled.set(1)
        wire_curve.getShape().overrideDisplayType.set(2)

    def rename(self, side=None, name=None, index=None, suffix=None):
        """Rename control member nodes

        :param side: New side, defaults to None
        :type side: str, optional
        :param name: New name, defaults to None
        :type name: str, optional
        :param index: New index, defaults to None
        :type index: int, optional
        :param suffix: New suffix, defaults to None
        :type suffix: str, optional
        """
        old_name = self.name
        for node in [self.group, self.transform, self.joint]:
            nameFn.rename(node, side, name, index, suffix)
        for node in self.offset_list:
            if name:
                name_parts = nameFn.deconstruct_name(node).name.split("_")
                extra_parts = [substr for substr in name_parts if substr not in old_name.split("_")]
                name = "_".join([name] + extra_parts)
            nameFn.rename(node, side, name, index, suffix)

    def write_bind_pose(self):
        """Writes current control pose to bindPose attribute on Control.transform"""
        if not pm.hasAttr(self.tag_node, "bindPose"):
            self.tag_node.addAttr("bindPose", dt="string", keyable=False)
            self.tag_node.bindPose.set(json.dumps(self.pose))
            self.tag_node.bindPose.lock()
        else:
            self.tag_node.bindPose.unlock()
            self.tag_node.bindPose.set(json.dumps(self.pose))
            self.tag_node.bindPose.lock()

    def to_bind_pose(self):
        """Reset control to pose stored in bindPose attribute"""
        self.set_pose(self.bind_pose)

    def set_pose(self, attr_dict):
        """Set attributes from dict

        :param attr_dict: Dictionary of pairs attr:value
        :type attr_dict: dict
        """
        for attr, value in attr_dict.items():
            if self.transform.hasAttr(attr):
                pm.setAttr("{0}.{1}".format(self.transform, attr), value)
            else:
                Logger.warning("Missing attribute {0}.{1}".format(self.transform, attr))

    def find_opposite(self):
        """Finds opposite control in the scene

        :return: [description]
        :rtype: [type]
        """
        template = nameFn.get_template()
        if self.side not in ["l", "r"]:
            return None
        opposite_transform = template.format(side=static.OppositeSide[self.side].value, name=self.indexed_name, suffix="ctl")
        # Handle namespaces
        opposite_transform = ":".join(self.transform.namespaceList() + [opposite_transform])
        if pm.objExists(opposite_transform):
            return Control(opposite_transform)
        else:
            Logger.info("{0}: No opposite control found.".format(self))
            return None

    def mirror_pose(self, behavior=True, direction="source", skip_translate=[False, False, False], skip_rotate=[False, False, False]):
        """Mirror control pose to opposite side

        :param across: Mirror plane, defaults to "yz"
        :type across: str, optional
        :param space: Mirror space, any transform or str values: ("world", "character"), defaults to "character"
        :type space: str or luna_rig.nt.Transform, optional
        :param behavior: Mirror transform behaviour, defaults to True
        :type behavior: bool, optional
        :param direction: Mirror direction, valid values ("source", "destination"), defaults to "source"
        :type direction: str, optional
        """
        opposite_ctl = self.find_opposite()
        if not opposite_ctl:
            opposite_ctl = self
        # Define direction
        if direction == "source":
            source_transform = self.transform
            destination_transform = opposite_ctl.transform
        else:
            source_transform = opposite_ctl.transform
            destination_transform = self.transform
        # Store old values
        old_translate = destination_transform.translate.get()
        old_rotate = destination_transform.rotate.get()
        # Apply matrix
        if behavior:
            destination_transform.setMatrix(source_transform.getMatrix(os=1).inverse(), os=1)
        else:
            destination_transform.setMatrix(source_transform.getMatrix(os=1), os=1)
        # Apply skipped values
        if any(skip_translate):
            for is_skipped, attr_name, old_value in zip(skip_translate, ["tx", "ty", "tz"], old_translate):
                if is_skipped:
                    destination_transform.attr(attr_name).set(old_value)
        if any(skip_rotate):
            for is_skipped, attr_name, old_value in zip(skip_rotate, ["rx", "ry", "rz"], old_rotate):
                if is_skipped:
                    destination_transform.attr(attr_name).set(old_value)

    def orient_shape(self, direction="x"):
        if direction.lower() not in "xyz" and direction.lower() not in ["-x", "-y", "-z"]:
            Logger.exception("Invalid orient direction: {0}".format(direction))
            return
        if direction == "y":
            return

        # Create temp transform and parent shapes to it
        temp_transform = pm.createNode("transform", n="temp_transform", p=self.transform)  # type: luna_rig.nt.Transform
        for each in self.transform.getShapes():
            pm.parent(each, temp_transform, s=1, r=1)

        # Apply rotation
        if direction == "x":
            temp_transform.rotateX.set(-90)
            temp_transform.rotateY.set(-90)
        elif direction == "-x":
            temp_transform.rotateX.set(90)
            temp_transform.rotateY.set(-90)
        elif direction == "-y":
            temp_transform.rotateZ.set(180)
        elif direction == "z":
            temp_transform.rotateX.set(90)
        elif direction == "-z":
            temp_transform.rotateX.set(-90)

        # Reparent shapes and delete temp transform
        pm.makeIdentity(temp_transform, rotate=True, apply=True)
        for each in temp_transform.getShapes():
            pm.parent(each, self.transform, s=1, r=1)
        pm.delete(temp_transform)

    def add_orient_switch(self, space_target, local_parent=None, default_state=1.0):
        if isinstance(local_parent, Control):
            local_parent = local_parent.transform
        if not local_parent and self.connected_component:
            local_parent = self.connected_component.in_hook.transform
        # Crete orient transforms
        space_group = pm.createNode("transform", n=nameFn.generate_name([self.name, "orient_space"], side=self.side, suffix="grp"), p=self.group)  # type: luna_rig.nt.Transform
        local_group = pm.createNode("transform", n=nameFn.generate_name([self.name, "orient_local"], side=self.side, suffix="grp"), p=self.group)  # type: luna_rig.nt.Transform
        space_group.setParent(None)
        local_group.setParent(None)
        # Add orient offset
        offset = self.insert_offset(extra_name="orient")
        orient_contstr = pm.orientConstraint(local_group, space_group, offset)  # type: luna_rig.nt.OrientConstraint
        # pm.pointConstraint(local_group, self.group)
        local_group.setParent(local_parent)
        space_group.setParent(space_target)
        # Connections
        self.transform.addAttr("localOrient", at="float", k=True, dv=default_state, min=0.0, max=1.0)
        reverse_node = pm.createNode("reverse", n=nameFn.generate_name([self.name, "orient"], side=self.side, suffix="rev"))
        self.transform.localOrient.connect(orient_contstr.getWeightAliasList()[0])
        self.transform.localOrient.connect(reverse_node.inputX)
        reverse_node.outputX.connect(orient_contstr.getWeightAliasList()[1])
        # Store util nodes
        if self.connected_component:
            self.connected_component._store_util_nodes([local_group, space_group])

    def add_driven_pose(self, driven_dict, driver_attr, driver_value):
        sdk_offset = self.find_offset("sdk")
        if not sdk_offset:
            sdk_offset = self.insert_offset(extra_name="sdk")
        for attr_name, value in driven_dict.items():
            pm.setDrivenKeyframe(sdk_offset.attr(attr_name), cd=driver_attr, v=sdk_offset.attr(attr_name).get(), dv=0)
            pm.setDrivenKeyframe(sdk_offset.attr(attr_name), cd=driver_attr, v=value, dv=driver_value)
        return sdk_offset

    def copy_keyframes(self, time_range, target_control, time_offset=0.0):
        copiedKeys = pm.copyKey(self.transform, time=time_range)
        if copiedKeys:
            pm.pasteKey(target_control.transform, time=time_range, option="fitReplace", timeOffset=time_offset)

    def constrain_geometry(self, geometry, scale=True, inherit_transforms=True):
        if not isinstance(geometry, pm.PyNode):
            geometry = pm.PyNode(geometry)  # type: luna_rig.nt.DependNode

        pm.parentConstraint(self.transform, geometry, mo=1)
        if scale:
            pm.scaleConstraint(self.transform, geometry, mo=1)

        if inherit_transforms and geometry.listRelatives(ad=1, typ="transform"):
            for child in geometry.listRelatives(ad=1, typ="transform"):
                child.it.set(True)

    def bake_space(self,
                   space_index=None,
                   space_name=None,
                   time_range=None,
                   step=1.0):
        if not self.spaces:
            Logger.warning("{0}: no spaces to bake".format(self))
            return

        # Get target space
        if isinstance(space_index, int):
            try:
                new_space_tuple = self.spaces[space_index]
            except IndexError:
                Logger.error("{0}: Invalid space index {1}".format(self, space_index))
                return
        elif space_name:
            filtered_spaces = [tpl for tpl in self.spaces if space_name == tpl[0]]
            try:
                new_space_tuple = filtered_spaces[0]
            except IndexError:
                Logger.error("{0}: Invalid space name '{1}'".format(self, space_name))
        else:
            Logger.error("{0}Bake space requires space index int or space name str, got index: {1}, name{2}".format(self, space_index, space_name))
            raise ValueError
        # Check against current
        if new_space_tuple[0] == self.space_name or new_space_tuple[1] == self.space_index:
            pm.warning("{0}: Can't bake space {1} to identical {2}".format(self, (self.space_name, self.space_index), new_space_tuple))
            return

        # Time range
        if not time_range:
            time_range = animFn.get_playback_range()

        # Baking
        src_space_index = self.space_index
        Logger.info("{0}: Baking space {1} ->> {2} {3}".format(self, self.space_name, new_space_tuple[0], time_range))
        # Bake to locator
        Logger.info("Baking to locator...")
        self.switch_space(src_space_index)
        bake_locator = pm.spaceLocator(n="bake_locator")  # type: luna_rig.nt.Transform
        pm.matchTransform(bake_locator, self.transform)
        parent_constr = pm.parentConstraint(self.transform, bake_locator)
        pm.bakeResults(bake_locator, t=time_range, sampleBy=step)
        pm.delete(parent_constr)

        # Bake new space for switch attrib
        Logger.info("Baking switch attr...")
        for frame in range(time_range[0], time_range[1] + 1, int(step)):
            pm.setCurrentTime(frame)
            self.switch_space(new_space_tuple[1], matching=False)
            self.transform.space.setKey()

        # Unparent
        Logger.info("Baking to control...")
        pm.setCurrentTime(time_range[0])
        bake_locator.setParent(None)
        pm.parentConstraint(bake_locator, self.transform, mo=True)
        pm.bakeResults(self.transform, t=time_range, sampleBy=step)
        # Cleanup
        pm.delete(bake_locator)
        Logger.info("Done.")

    def bake_custom_space(self,
                          space_object,
                          time_range=None,
                          step=1.0):
        # Find locked attrs to skip
        locked_attrs = self.transform.listAttr(locked=True)
        skip_rotate = []
        skip_translate = []
        for attr in locked_attrs:
            if attr.attrName() in ["tx", "ty", "tz"]:
                skip_translate.append(attr.attrName()[-1])
            elif attr.attrName() in ["rx", "ry", "rz"]:
                skip_rotate.append(attr.attrName()[-1])

        # Create locator and constraint to control to it
        space_locator = pm.spaceLocator(n="space_locator")
        pm.matchTransform(space_locator, space_object)
        pm.parent(space_locator, space_object)
        pm.parentConstraint(space_locator, self.transform, mo=1, sr=skip_rotate, st=skip_translate)
        # Time range
        if not time_range:
            time_range = animFn.get_playback_range()
        # Baking
        Logger.info("{0}: Baking to space {1} {2}".format(self, space_object, time_range))
        pm.bakeResults(self.transform, t=time_range, sampleBy=step)
        # Cleanup
        pm.delete(space_locator)

    def connect_via_remap(self,
                          source_plug,
                          dest_plug,
                          remap_name="remap",
                          input_min=0.0,
                          input_max=10.0,
                          output_min=0.0,
                          output_max=1.0):
        if isinstance(source_plug, str):
            source_plug = self.transform.attr(source_plug)  # type: pm.Attribute
        if isinstance(dest_plug, str):
            dest_plug = pm.PyNode(dest_plug)  # type: pm.Attribute
        remap_node = nodeFn.create("remapValue", [self.indexed_name, remap_name], self.side, suffix="rmv")
        remap_node.inputMin.set(input_min)
        remap_node.inputMax.set(input_max)
        remap_node.outputMin.set(output_min)
        remap_node.outputMax.set(output_max)
        source_plug.connect(remap_node.inputValue)
        remap_node.outValue.connect(dest_plug)
