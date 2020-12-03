import sys

from Luna import Logger
from Luna.test import maya_unit_test


def run_unit_tests(*args):
    maya_unit_test.run_all_tests()


def reload_rig_components(*args):
    """Reloads all modules located in in Luna_rig.components package"""
    avoid_reload = set("Luna_rig.core.meta, Luna_rig.core.component")
    to_reload = set()
    for mod_name in sys.modules.keys():
        if "Luna_rig.components" in mod_name and "pymel" not in mod_name:
            to_reload.add(mod_name)

    for mod_name in to_reload.difference(avoid_reload):
        mod = sys.modules.get(mod_name)
        if mod:
            reload(mod)
            Logger.info("Reloaded {0}".format(mod_name))
