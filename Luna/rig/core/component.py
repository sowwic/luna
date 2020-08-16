import pymel.core as pm
from Luna import Logger
from Luna.rig.core import meta
from Luna.rig.functions import nameFn


class Component(meta.MetaRigNode):
    def __new__(cls, node=None):
        return object.__new__(cls, node)

    def __init__(self, node):
        super(Component, self).__init__(node)
        Logger.debug("Construnctor call")

    def __create__(self):
        Logger.debug("Custom create")
        pm.createNode("transform", n="Custom_create")

    def do_smth(self):
        Logger.debug("Instance function call")

    @staticmethod
    def create(meta_parent, meta_type, version):
        obj_instance = super(Component, Component).create(meta_parent, meta_type, version)  # type: Component
        obj_instance.__create__()

        return obj_instance
