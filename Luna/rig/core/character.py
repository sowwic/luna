import pymel.core as pm
from Luna import Logger
from Luna.rig.core import component


class Character(component.Component):
    def __init__(self, node):
        super(Character, self).__init__(node)

    def __create__(self):
        pass

    @staticmethod
    def create(meta_parent, meta_type, version):
        return super(Character, Character).create(meta_parent, meta_type, version)
