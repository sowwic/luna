import pymel.core as pm
from Luna import Logger
from Luna.rig.components import fk_component


def create_new():
    pm.newFile(f=1)
    new_component = fk_component.FKComponent.create(None, "components.fk_component.FKComponent", 1)
    return new_component


def get_existing():
    test_component = fk_component.FKComponent("network1")
    return test_component


if __name__ == "__main__":
    test = create_new()  # type: fk_component.FKComponent
    test = get_existing()
    Logger.debug(test)
    # test.do_smth()
