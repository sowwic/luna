import logging
import logging.config
import pymel.core as pm
from Luna.static import Directories

# Logging
logging.config.fileConfig(fname=Directories.LOG_CONFIG,
                          defaults={"logfilename": Directories.LOG_FILE},
                          disable_existing_loggers=0)
LOGGER = logging.getLogger(__name__)


def open_port(port=7221, lang="python"):
    if not pm.commandPort("127.0.0.1:{0}".format(port), n=1, q=1):
        try:
            pm.commandPort(name="127.0.0.1:{0}".format(port), stp=lang, echoOutput=True)
            LOGGER.info("Command port opened: Python - 7221")
        except Exception as e:
            LOGGER.error("Failed to open command port", exc_info=e)


def run():
    LOGGER.info("Logging to file: {0}".format(Directories.LOG_FILE))
    open_port()
