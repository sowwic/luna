import os
import pymel.core as pm

MAYA_APP_PATH = str(pm.internalVar(uad=1))  # type: str
TMP_PATH = pm.internalVar(utd=1)  # type: str
USER_PREFS_PATH = pm.internalVar(upd=1)  # type: str
LUNA_ROOT_PATH = pm.moduleInfo(moduleName="luna", p=1)  # type: str # type: str
LOG_FILE = os.path.join(LUNA_ROOT_PATH, "luna.log")  # type: str
SHAPES_LIB_PATH = os.path.join(LUNA_ROOT_PATH, "resources", "shapes")  # type: str
TEMPLATES_PATH = os.path.join(LUNA_ROOT_PATH, "resources", "templates")  # type: str
EMPTY_SCENES_PATH = os.path.join(TEMPLATES_PATH, "emptyScenes")  # type: str
ICONS_PATH = os.path.join(LUNA_ROOT_PATH, "resources", "images", "icons")  # type: str
FALLBACK_IMG_PATH = os.path.join(LUNA_ROOT_PATH, "resources", "images", "fallbacks")  # type: str
COMET_ORIENT_PATH = MAYA_APP_PATH + "scripts/comet/cometJointOrient.mel"  # type: str
DEFAULT_CONFIG_PATH = os.path.join(LUNA_ROOT_PATH, "configs", "default_config.json")  # type:str
CONFIG_PATH = os.path.join(LUNA_ROOT_PATH, "configs", "config.json")  # type:str
EXTERNAL_TOOLS_REGISTER = os.path.join(LUNA_ROOT_PATH, "configs", "external_tools.json")  # type:str
TEST_DIR_PATH = os.path.join(LUNA_ROOT_PATH, "tests")  # type:str
PLUGINS_DIR_PATH = os.path.join(LUNA_ROOT_PATH, "plugins")  # type:str
EDITOR_PLUGINS_PATH = os.path.join(LUNA_ROOT_PATH, "luna_builder", "rig_nodes")


def get_icon_path(*path_parts):
    return os.path.join(ICONS_PATH, *path_parts)
