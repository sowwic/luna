"""Based on 2015 GDC talk by David Hunt & Forrest Sderlind https://www.youtube.com/watch?v=U_4u0kbf-JE"""

import pymel.core as pm
from pymel.core.nodetypes import Network
from Luna import Logger


class MetaRigNode(object):
    def __new__(cls, node=None):
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
        node = pm.PyNode(node)
        if not node.hasAttr("metaRigType"):
            raise TypeError("{0} is not a valid meta rig node".format(str(node)))
        self.pynode = node

    @staticmethod
    def create(meta_parent, meta_type, version):
        if meta_parent:
            meta_parent = MetaRigNode(meta_parent)

        # Create node
        node = pm.createNode("network")  # type: Network

        # Add attributes
        node.addAttr("version", at="long")
        node.addAttr("metaRigType", dt="string")
        node.addAttr("metaChildren", at="message", m=1)
        node.addAttr("metaParent", at="message")
        node.version.set(version)
        node.metaRigType.set(meta_type)
        node = MetaRigNode(node)
        if meta_parent:
            node.set_meta_parent(meta_parent)

        return node

    def set_meta_parent(self, parent):
        Logger.debug("{0} parent - {1}".format(str(self.pynode), str(parent)))
