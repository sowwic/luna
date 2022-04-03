"""Based on 2015 GDC talk by David Hunt & Forrest Sderlind https://www.youtube.com/watch?v=U_4u0kbf-JE"""

import pymel.core as pm
import luna_rig
from luna import Logger
from luna_rig.functions import nameFn


class MetaNode(object):

    @classmethod
    def as_str(cls, name_only=False):
        """Get a string representation of class path.

        :return: Class string e.g luna_rig.components.fk_component.FKComponent
        :rtype: str
        """
        meta_module = cls.__module__
        meta_name = cls.__name__
        if name_only:
            return meta_name
        meta_type_str = ".".join([meta_module, meta_name])
        return meta_type_str

    def __repr__(self):
        return "{0} ({1})".format(self.as_str(name_only=True), self.pynode.name())

    def __eq__(self, other):
        if not hasattr(other, 'pynode'):
            return False
        return self.pynode == other.pynode

    def __new__(cls, node=None):
        """Initialize class stored in metaType attribute and return a intance of it.

        :param node: Network node, defaults to None
        :type node: str or PyNode, optional
        :return: Evaluated meta class
        :rtype: Meta rig node class instance
        """
        import luna_rig  # noqa: F401
        result = None
        if node:
            node = pm.PyNode(node)
            class_string = node.metaType.get()
            try:
                eval_class = eval(class_string, globals(), locals())
                result = eval_class.__new__(eval_class, node)
            except Exception:
                Logger.exception("{0}: Failed to evaluate class string: {1}".format(cls, class_string))
                raise
        else:
            result = super(MetaNode, cls)

        return result

    def __init__(self, node):
        """Stores created network node as instance field

        :param node: Network node
        :type node: str or PyNode
        :raises TypeError: If node has no metaType attribute
        """
        node = pm.PyNode(node)
        if not self.is_metanode(node):
            raise TypeError("{0} is not a valid meta rig node".format(str(node)))
        self.pynode = node  # type: luna_rig.nt.Network

    @property
    def namespace_list(self):
        name_parts = nameFn.deconstruct_name(self.pynode)
        return name_parts.namespaces

    @property
    def name(self):
        name_parts = nameFn.deconstruct_name(self.pynode)
        return name_parts.name

    @property
    def side(self):
        return nameFn.deconstruct_name(self.pynode).side

    @property
    def index(self):
        return nameFn.deconstruct_name(self.pynode).index

    @property
    def indexed_name(self):
        name_parts = nameFn.deconstruct_name(self.pynode)
        return name_parts.indexed_name

    @property
    def suffix(self):
        return nameFn.deconstruct_name(self.pynode).suffix

    @property
    def meta_type(self):
        attr_val = self.pynode.metaType.get()  # type: str
        return attr_val

    @property
    def tag(self):
        if self.pynode.hasAttr("tag"):
            return self.pynode.tag.get()
        else:
            Logger.warning("{0}: Missing tag attribute".format(self))
            return ""

    @property
    def meta_parent(self):
        """Get instance of meta parent

        :return: Meta parent node instance.
        :rtype: MetaNode
        """
        result = None
        connections = self.pynode.metaParent.listConnections()
        if connections:
            result = MetaNode(connections[0])
        return result

    @property
    def meta_children(self):
        return self.get_meta_children()

    # ========== Getter methods ============ #
    def get_namespace_list(self):
        return self.namespace_list

    def get_name(self):
        return self.name

    def get_side(self):
        return self.side

    def get_index(self):
        return self.index

    def get_indexed_name(self):
        return self.indexed_name

    def get_suffix(self):
        return self.suffix

    def get_meta_type(self):
        return self.meta_type

    def get_tag(self):
        return self.tag

    def get_meta_parent(self):
        return self.meta_parent

    # ========= Other Methods ==========#

    @classmethod
    def is_metanode(cls, node):
        node = pm.PyNode(node)
        return node.hasAttr("metaType")

    @classmethod
    def create(cls, meta_parent):
        """Creates meta node and calls constructor for MetaNode using meta_type.

        :param meta_parent: Meta parent node to connect to
        :type meta_parent: str or PyNode
        :return: Instance of meta_type class
        :rtype: MetaNode
        """
        if meta_parent:
            if not isinstance(meta_parent, MetaNode):
                meta_parent = MetaNode(meta_parent)

        # Create node
        node = pm.createNode("network")  # type: luna_rig.nt.Network

        # Add attributes
        node.addAttr("metaType", dt="string")
        node.addAttr("tag", dt="string")
        node.addAttr("metaChildren", at="message", multi=1, im=0)
        node.addAttr("metaParent", at="message")
        node.metaType.set(cls.as_str())
        meta_node = MetaNode(node)
        if meta_parent:
            meta_node.set_meta_parent(meta_parent)
        return meta_node

    def set_meta_parent(self, parent):
        self.pynode.metaParent.connect(parent.pynode.metaChildren, na=1)

    def get_meta_children(self, of_type=None, by_tag=""):
        """Get list of connected meta children

        :param of_type: Only list children of specific type, defaults to None
        :type of_type: class, optional
        :param by_tag: List child nodes that have specified tag, defaults to ""
        :type by_tag: str, optional
        :return: List of meta children instances
        :rtype: list[MetaNode]
        """
        result = []
        if self.pynode.hasAttr("metaChildren"):
            connections = self.pynode.metaChildren.listConnections()
            if connections:
                children = [MetaNode(connection_node) for connection_node in connections if pm.hasAttr(connection_node, "metaType")]
                # Type filter
                if not of_type:
                    result = children
                else:
                    if not isinstance(of_type, type):
                        of_type = type(of_type)

                    if isinstance(of_type, str):
                        result = [child for child in children if of_type in child.as_str()]
                    else:
                        result = [child for child in children if isinstance(child, of_type)]
                # Tag filter
                if by_tag:
                    result = [child for child in result if child.tag == by_tag]
        else:
            Logger.warning("{0}: Missing metaChildren attribute.")
        return result

    def set_tag(self, tag_str):
        self.pynode.tag.set(tag_str)

    def is_animatable(self):
        return isinstance(self, (luna_rig.AnimComponent, luna_rig.components.Character))

    @staticmethod
    def list_nodes(of_type=None, by_tag=""):
        """List existing meta nodes

        :param of_type: List only specific type, defaults to None
        :type of_type: str, class, optional
        :param by_tag: List nodes that have specified tag, defaults to ""
        :type by_tag: str, optional
        :return: List of MetaNode instances.
        :rtype: list[MetaNode]
        """
        result = []
        all_nodes = [MetaNode(node) for node in pm.ls(typ="network") if node.hasAttr("metaType")]
        if of_type:
            if not isinstance(of_type, type):
                of_type = type(of_type)

            if isinstance(of_type, str):
                result = [node for node in all_nodes if of_type in node.as_str()]
            else:
                result = [node for node in all_nodes if isinstance(node, of_type)]
        else:
            result = all_nodes

        # Tag filter
        if by_tag:
            result = [node for node in result if node.tag == by_tag]
        return result

    @staticmethod
    def scene_types(of_type=None):
        types_dict = {}
        for meta_node in MetaNode.list_nodes(of_type=of_type):
            if meta_node.as_str(name_only=True) not in types_dict.keys():
                types_dict[meta_node.as_str(name_only=True)] = type(meta_node)
        return types_dict

    @staticmethod
    def get_connected_metanode(node, of_type=None):
        node = pm.PyNode(node)
        all_nodes = [MetaNode(network) for network in node.listConnections(type="network") if network.hasAttr("metaType")]
        if of_type:
            result = [meta_node for meta_node in all_nodes if isinstance(meta_node, of_type)]
        else:
            result = all_nodes
        return result
