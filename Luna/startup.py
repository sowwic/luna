import logging
import logging.config
from Luna.static import Directories

logging.config.fileConfig(fname=Directories.LOG_CONFIG, defaults={"logfilename": Directories.LOG_FILE}, disable_existing_loggers=0)
LOGGER = logging.getLogger(__name__)


def open_port(port=7221):
    LOGGER.info("Opened Python command port: {0}".format(port))


def run():
    LOGGER.info("Logging to file: {0}".format(Directories.LOG_FILE))
    open_port()
