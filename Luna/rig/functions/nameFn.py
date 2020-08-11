import pymel.core as pm
from Luna import Logger


def deconstruct_name(full_name):
    name_parts = full_name.split("_")

    class _nameStruct:
        def __init__(self):
            self.side = name_parts[0]
            self.name = name_parts[1]
            self.type = name_parts[2]
            self.index = name_parts[-2]
            self.suffix = name_parts[-1]

    return _nameStruct()


def generate_name(name, side="", sub_type="", suffix=""):
    if side:
        side += "_"
    if sub_type:
        sub_type = "_{0}_".format(sub_type)
    if suffix:
        suffix = "_" + suffix

    index = 1
    version = '{0:02}'.format(index)
    full_name = side + name + sub_type + version + suffix
    while pm.objExists(full_name):
        index += 1
        version = '{0:02}'.format(index)
        full_name = side + name + sub_type + version + suffix

    return full_name
