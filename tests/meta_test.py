import pymel.core as pm
from Luna.rig.core import component
from Luna import Logger
reload(component)


def create_new():
    pm.newFile(f=1)
    new_component = component.Component.create(None, "core.component.Component", 1)
    return new_component


def get_existing():
    test_component = component.Component("network1")
    return test_component


if __name__ == "__main__":
    test = create_new()  # type: component.Component
    # test = get_existing()
    Logger.debug(test)
    test.do_smth()
