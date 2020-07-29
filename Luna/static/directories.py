import logging
import os
import pymel.core as pm


logging.getLogger(__name__)


class Directories:
    MAYA_APP_PATH = str(pm.internalVar(uad=1))  # type: str
    TMP_PATH = pm.internalVar(utd=1)  # type: str
    USER_PREFS_PATH = pm.internalVar(upd=1)  # type: str
    LUNA_ROOT_PATH = pm.moduleInfo(moduleName="Luna", p=1)  # type: str # type: str
    LOG_FILE = os.path.join(LUNA_ROOT_PATH, "Luna.log")  # type: str
    LOG_CONFIG = os.path.join(LUNA_ROOT_PATH, "configs", "logging_config.ini")  # type: str
    SHAPES_LIB_PATH = os.path.join(LUNA_ROOT_PATH, "Luna/static/control_shapes")  # type: str
    ICONS_PATH = os.path.join(LUNA_ROOT_PATH, "icons")  # type: str
    COMET_ORIENT_PATH = MAYA_APP_PATH + "scripts/comet/cometJointOrient.mel"  # type: str


def getIcon(name):
    return os.path.join(Directories.ICONS_PATH, name)


if __name__ == "__main__":
    print Directories.LOG_FILE[1:]
