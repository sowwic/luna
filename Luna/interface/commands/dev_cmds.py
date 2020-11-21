import sys

from Luna import Logger
from Luna.test import maya_unit_test


def run_unit_tests(*args):
    maya_unit_test.run_all_tests()


def reload_luna_modules(*args):
    #!FIXME Reload causes inheritance issues in Luna_rig modules.
    avoid_reload = set("Luna_rig.core.meta, Luna_rig.core.component")
    to_reload = set()
    for mod_name in sys.modules.keys():
        if "Luna" in mod_name and "pymel" not in mod_name:
            to_reload.add(mod_name)
            # mod = sys.modules.get(mod_name)
            # if mod:
            #     reload(mod)
            #     Logger.info("Reloaded {0}".format(mod_name))

    for mod_name in to_reload.difference(avoid_reload):
        mod = sys.modules.get(mod_name)
        if mod:
            reload(mod)
            Logger.info("Reloaded {0}".format(mod_name))
