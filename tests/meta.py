import pymel.core as pm
from Luna_rig.core import component
from Luna import Logger
reload(component)


def create_new():
    pm.newFile(f=1)
    new_component = component.AnimComponent.create(None, "core.component.AnimComponent", 1)
    return new_component


def get_existing(node):
    test_component = component.AnimComponent(node)
    return test_component


if __name__ == "__main__":
    test = create_new()  # type: component.Component
    # test = get_existing("c_animComponent_00_meta")
    test2 = component.AnimComponent.create(test.pynode, "core.component.AnimComponent", 1)

    test2.attach_to_component(test)
