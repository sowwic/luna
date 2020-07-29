import logging
import pymel.core as pm
from Luna.utils.enumFn import Enum

LOGGER = logging.getLogger(__name__)


class OptionVars(Enum):
    prevWorkspace = "LunaPrevWorkspace"
    locatorToolOptions = "LunaLocatorToolOptions"
