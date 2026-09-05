"""Based on 2015 GDC talk by David Hunt & Forrest Sderlind https://www.youtube.com/watch?v=U_4u0kbf-JE"""

from maya import cmds

from luna import Logger
from ..functions import nameFn


class MetaNode:
    IS_ANIMATABLE = False
    META_TYPE_ATTR = "metaType"
    META_PARENT_ATTR = "metaParent"
    META_CHILDREN_ATTR = "metaChildren"
    TAG_ATTR = "tag"

    @classmethod
    def as_str(cls, name_only=False) -> str:
        """Get a string representation of class path.

        Args:
            name_only (bool, optional): class name only as result. Defaults to False.

        Returns:
            str: string representation
        """
        meta_name = cls.__name__
        if name_only:
            return meta_name

        meta_module = cls.__module__
        meta_type_str = ".".join([meta_module, meta_name])
        return meta_type_str

    def __repr__(self) -> str:
        return f"{self.as_str(name_only=True)} ({self.pynode_short_name})"

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.pynode == other.pynode

    def __new__(cls, node=None) -> "MetaNode":
        """Initialize class stored in metaType attribute and return a instance of it.

        Args:
            node (str | None): node path

        Returns:
            MetaNode: initialized class from metaType string
        """
        import luna_rig  # noqa: F401

        result = None
        if node:
            class_string: str = cmds.getAttr(node, cls.META_TYPE_ATTR)
            try:
                eval_class = eval(class_string, globals(), locals())
                result = eval_class.__new__(eval_class, node)
            except Exception:
                Logger.exception(
                    f"{cls}: Failed to evaluate class string: {class_string}"
                )
                raise
        else:
            result = super()

        return result

    def __init__(self, node: str):
        """Store given network node as instance.

        Args:
            node (str): meta network node path.

        Raises:
            TypeError: provided node is not a valid metanode
        """
        if not self.is_metanode(node):
            raise TypeError(f"{str(node)} is not a valid meta rig node")
        self.pynode: str = node

    @property
    def pynode_short_name(self) -> str:
        return self.pynode.split("|")[-1]

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
    def meta_parent_attr(self) -> str:
        return f"{self.pynode}.{self.META_PARENT_ATTR}"

    @property
    def meta_children_attr(self) -> str:
        return f"{self.pynode}.{self.META_CHILDREN_ATTR}"

    @property
    def tag_attr(self) -> str:
        return f"{self.pynode}.{self.TAG_ATTR}"

    @property
    def has_tag_attr(self) -> bool:
        return cmds.objExists(self.tag_attr)

    @property
    def meta_type(self):
        return cmds.getAttr(self.META_TYPE_ATTR)

    @property
    def tag(self):
        if self.has_tag_attr:
            return cmds.getAttr(self.tag_attr)
        else:
            Logger.warning(f"{self}: Missing tag attribute")
            return ""

    @property
    def meta_parent(self) -> "MetaNode":
        """Get instance of meta parent

        :return: Meta parent node instance.
        :rtype: MetaNode
        """
        result = None
        connections = cmds.listConnections(self.meta_parent_attr) or []
        if connections:
            result = MetaNode(connections[0])
        return result

    @property
    def meta_children(self):
        return self.get_meta_children()

    # ========== Getter methods ============ #
    def get_namespace_list(self):
        return self.namespace_list

    def get_name(self) -> str:
        return self.name

    def get_side(self) -> str:
        return self.side

    def get_index(self) -> str:
        return self.index

    def get_indexed_name(self) -> str:
        return self.indexed_name

    def get_suffix(self) -> str:
        return self.suffix

    def get_meta_type(self) -> str:
        return self.meta_type

    def get_tag(self):
        return self.tag

    def get_meta_parent(self):
        return self.meta_parent

    # ========= Other Methods ==========#

    @staticmethod
    def is_metanode(node: str):
        return cmds.objExists(f"{node}.{MetaNode.META_TYPE_ATTR}")

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
        node: str = cmds.createNode("network")

        # Add attributes
        cmds.addAttr(node, longName=cls.META_TYPE_ATTR, dataType="string")
        cmds.addAttr(node, longName="tag", dataType="string")
        cmds.addAttr(
            node,
            longName="metaChildren",
            attributeType="message",
            multi=True,
            indexMatters=False,
        )
        cmds.addAttr(
            node, longName="metaParent", attributeType="message", indexMatters=False
        )
        cmds.setAttr(node, cls.META_TYPE_ATTR, cls.as_str(), type="string")
        meta_node = MetaNode(node)
        if meta_parent:
            meta_node.set_meta_parent(meta_parent)
        return meta_node

    def set_meta_parent(self, parent: "MetaNode"):
        cmds.connectAttr(
            self.meta_parent_attr, parent.meta_children_attr, nextAvailable=True
        )

    def get_meta_children(self, of_type=None, by_tag=""):
        # type: (type[MetaNode], str) -> list[MetaNode]
        """Get list of connected meta children

        :param of_type: Only list children of specific type, defaults to None
        :type of_type: class, optional
        :param by_tag: List child nodes that have specified tag, defaults to ""
        :type by_tag: str, optional
        :return: List of meta children instances
        :rtype: list[MetaNode]
        """
        connections = cmds.listConnections(self.meta_children_attr)
        if not connections:
            return []

        result = [
            MetaNode(connection_node)
            for connection_node in connections
            if self.is_metanode(connection_node)
        ]
        # Type filter
        if of_type:
            if isinstance(of_type, str):
                result = [child for child in result if of_type in child.as_str()]

            elif isinstance(of_type, MetaNode):
                of_type = type(of_type)
                result = [child for child in result if isinstance(child, of_type)]

        # Tag filter
        if by_tag:
            result = [child for child in result if child.tag == by_tag]
        return result

    def set_tag(self, tag_str):
        cmds.setAttr(self.tag_attr, tag_str)

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
        all_nodes = [
            MetaNode(node)
            for node in cmds.ls(type="network", long=True)
            if MetaNode.is_metanode(node)
        ]
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
        all_nodes = [
            MetaNode(network)
            for network in cmds.listConnections(node, type="network", fullNodeName=True)
            if MetaNode.is_metanode(node)
        ]
        if of_type:
            result = [
                meta_node for meta_node in all_nodes if isinstance(meta_node, of_type)
            ]
        else:
            result = all_nodes
        return result
