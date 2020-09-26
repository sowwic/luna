import pymel.core as pm
from Luna.rig.core import component
from Luna import Logger
reload(component)


def create_new():
    pm.newFile(f=1)
    new_component = component.Component.create(None, "core.component.Component", 1)
    return new_component


def get_existing(node):
    test_component = component.Component(node)
    return test_component


if __name__ == "__main__":
    test = create_new()  # type: component.Component
    # test = get_existing("c_component_00_meta")
    test2 = component.Component.create(None, "core.component.Component", 1)
    test3 = component.Component.create(None, "core.component.Component", 1)

    test.attach_to_component(test2)
    test3.attach_to_component(test2)
