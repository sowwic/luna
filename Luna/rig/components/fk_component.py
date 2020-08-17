import pymel.core as pm
from Luna import Logger
from Luna.rig.core import component


class FKComponent(component.Component):
    def __init__(self, node):
        super(FKComponent, self).__init__(node)

    def __create__(self):
        return super(FKComponent, self).__create__()

    def do_smth(self):
        Logger.debug("fk_component do_smth method")

    @staticmethod
    def create(meta_parent, meta_type, version):
        return super(FKComponent, FKComponent).create(meta_parent, meta_type, version)
