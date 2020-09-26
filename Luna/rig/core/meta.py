"""Based on 2015 GDC talk by David Hunt & Forrest Sderlind https://www.youtube.com/watch?v=U_4u0kbf-JE"""

import pymel.core as pm
from pymel.core.nodetypes import Network
from Luna import Logger


class MetaRigNode(object):
    def __new__(cls, node=None):
        """Initialize class stored in metaRigType attribute and return a intance of it.

        :param node: Network node, defaults to None
        :type node: str or PyNode, optional
        :return: Evaluated meta class
        :rtype: Meta rig node class instance
        """
        import Luna.rig  # noqa: F401
        result = None
        if node:
            node = pm.PyNode(node)
            class_string = node.metaRigType.get()
            eval_class = eval("Luna.rig." + class_string, globals(), locals())
            result = eval_class.__new__(eval_class, node)
        else:
            result = super(MetaRigNode, cls)

        return result

    def __init__(self, node):
        """Stores created network node as instance field

        :param node: Network node
        :type node: str or PyNode
        :raises TypeError: If node has no metaRigType attribute
        """
        node = pm.PyNode(node)
        if not node.hasAttr("metaRigType"):
            raise TypeError("{0} is not a valid meta rig node".format(str(node)))
        self.pynode = node  # type: pm.PyNode

    @staticmethod
    def create(meta_parent, meta_type, version):
        """Creates meta node and calls constructor for MetaRigNode using meta_type.

        :param meta_parent: Meta parent node to connect to
        :type meta_parent: str or PyNode
        :param meta_type: Meta class name
        :type meta_type: str
        :param version: meta version
        :type version: int
        :return: Instance of meta_type class
        :rtype: MetaRigNode
        """
        if meta_parent:
            meta_parent = MetaRigNode(meta_parent)

        # Create node

        node = pm.createNode("network")  # type: Network

        # Add attributes
        node.addAttr("version", at="long")
        node.addAttr("metaRigType", dt="string")
        node.addAttr("metaChildren", at="message", multi=1, im=0)
        node.addAttr("metaParent", at="message")
        node.version.set(version)
        node.metaRigType.set(meta_type)
        node = MetaRigNode(node)
        if meta_parent:
            node.set_meta_parent(meta_parent)

        return node

    def set_meta_parent(self, parent):
        self.pynode.metaParent.connect(parent.pynode.metaChildren, na=1)
