import os
import pymel.core as pm


class Directories:
    MAYA_APP_PATH = str(pm.internalVar(uad=1))  # type: str
    TMP_PATH = pm.internalVar(utd=1)  # type: str
    USER_PREFS_PATH = pm.internalVar(upd=1)  # type: str
    LUNA_ROOT_PATH = pm.moduleInfo(moduleName="Luna", p=1)  # type: str # type: str
    LOG_FILE = os.path.join(LUNA_ROOT_PATH, "Luna.log")  # type: str
    SHAPES_LIB_PATH = os.path.join(LUNA_ROOT_PATH, "res", "shapes")  # type: str
    TEMPLATES_PATH = os.path.join(LUNA_ROOT_PATH, "res", "templates")  # type: str
    EMPTY_SCENES_PATH = os.path.join(TEMPLATES_PATH, "emptyScenes")  # type: str
    ICONS_PATH = os.path.join(LUNA_ROOT_PATH, "res", "images", "icons")  # type: str
    FALLBACK_IMG_PATH = os.path.join(LUNA_ROOT_PATH, "res", "images", "fallbacks")  # type: str
    COMET_ORIENT_PATH = MAYA_APP_PATH + "scripts/comet/cometJointOrient.mel"  # type: str
    DEFAULT_CONFIG_PATH = os.path.join(LUNA_ROOT_PATH, "configs", "default_config.json")  # type:str
    CONFIG_PATH = os.path.join(LUNA_ROOT_PATH, "configs", "config.json")  # type:str
    EXTERNAL_TOOLS_REGISTER = os.path.join(LUNA_ROOT_PATH, "configs", "external_tools.json")  # type:str
    TEST_DIR_PATH = os.path.join(LUNA_ROOT_PATH, "tests")  # type:str
