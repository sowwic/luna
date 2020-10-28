import pymel.core as pm
from Luna import Logger
from Luna_rig import components


def create_new():
    pm.newFile(f=1)
    new_component = components.FKComponent.create(None, "components.FKComponent", 1)
    return new_component


def get_existing():
    test_component = components.FKComponent("network1")
    return test_component


if __name__ == "__main__":
    # test = create_new()  # type: components.FKComponent
    test = get_existing()
    Logger.debug(test)
    # test.do_smth()
