from logging import log
import pymel.core as pm
from Luna import Logger
from Luna.rig.core import meta
from Luna.rig.functions import nameFn


class _dataStruct:
    def __init__(self):
        self.side = None  # type: str
        self.name = None  # type: str
        self.fullname = None  # type: str


class Component(meta.MetaRigNode):
    def __new__(cls, node=None):
        return object.__new__(cls, node)

    def __init__(self, node):
        super(Component, self).__init__(node)
        self.data = _dataStruct()

    def __create__(self, side, name):
        # Store data in a struct
        self.data.side = side
        self.data.name = name

        self.pynode.rename(nameFn.generate_name(name, side, suffix="meta"))

    @ staticmethod
    def create(meta_parent, meta_type, version, side="c", name="component"):
        obj_instance = super(Component, Component).create(meta_parent, meta_type, version)  # type: Component
        obj_instance.__create__(side, name)

        return obj_instance

    def get_name(self):
        return nameFn.deconstruct_name(self.pynode)

    def get_meta_children(self, of_type=None):
        result = []
        if self.pynode.hasAttr("metaChildren"):
            connections = self.pynode.listConnections()
            if connections:
                children = [meta.MetaRigNode(connection_node) for connection_node in connections if pm.hasAttr(connection_node, "metaRigType")]
                if not of_type:
                    result = children
                else:
                    result = [child for child in children if isinstance(child, of_type)]

        return result

    def get_meta_parent(self):
        result = None
        connections = self.pynode.listConnections()
        if connections:
            result = Component(connections[0])
        return result

    def attach_to_component(self, parent):
        if not isinstance(parent, Component):
            parent = meta.MetaRigNode(parent)
        self.pynode.metaParent.connect(parent.pynode.metaChildren, na=1)


class AnimComponent(Component):
    class _groupStruct:
        def __init__(self):
            self.root = None
            self.ctls = None
            self.joints = None
            self.parts = None

    class _controlStruct:
        def __init__(self):
            pass

    def __init__(self, node):
        super(AnimComponent, self).__init__(node)
        self.group = self._groupStruct()
        self.controls = self._controlStruct()

    def __create__(self, side, name):
        super(AnimComponent, self).__create__(side, name)

        # Create hierarchy
        self.group.root = pm.group(n=nameFn.generate_name(self.data.name, self.data.side, suffix="grp"), em=1)
        self.group.ctls = pm.group(n=nameFn.generate_name(self.data.name, self.data.side, suffix="ctls"), em=1, p=self.group.root)
        self.group.joints = pm.group(n=nameFn.generate_name(self.data.name, self.data.side, suffix="jnts"), em=1, p=self.group.root)
        self.group.parts = pm.group(n=nameFn.generate_name(self.data.name, self.data.side, suffix="parts"), em=1, p=self.group.root)
        for node in [self.group.root, self.group.ctls, self.group.joints, self.group.parts]:
            node.addAttr("metaParent", at="message")

        # Add message attrs
        self.pynode.addAttr("rootGroup", at="message")
        self.pynode.addAttr("ctlsGroup", at="message")
        self.pynode.addAttr("jointsGroup", at="message")
        self.pynode.addAttr("partsGroup", at="message")

        # Connect hierarchy to meta
        self.group.root.metaParent.connect(self.pynode.rootGroup)
        self.group.ctls.metaParent.connect(self.pynode.ctlsGroup)
        self.group.joints.metaParent.connect(self.pynode.jointsGroup)
        self.group.parts.metaParent.connect(self.pynode.partsGroup)

    @ staticmethod
    def create(meta_parent, meta_type, version, side="c", name="animComponent"):
        obj_instance = super(AnimComponent, AnimComponent).create(meta_parent, meta_type, version, side, name)

        return obj_instance

    def populate_structs(self):
        # Populate structs from message connections
        self.group.root = self.pynode.rootGroup.get()

    def get_controls(self):
        pass

    def get_bind_joints(self):
        pass

    def select_controls(self):
        pass

    def key_controls(self):
        pass

    def attach_to_skeleton(self):
        pass

    def remove(self):
        pass

    def bake_to_skeleton(self):
        pass

    def bake_to_rig(self):
        pass

    def bake_and_detach(self):
        pass

    def to_default_pose(self):
        pass
