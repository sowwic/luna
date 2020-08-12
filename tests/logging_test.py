from Luna import Logger


Logger.info("Test info")
Logger.debug("Test debug")
Logger.error("Test error")
Logger.warning("Test warning")
Logger.critical("Test critical")
Logger.log(5, "Log message")


# Logger.signal_handler().emitter.message_logged.connect()


try:
    a = []
    b = a[0]
except BaseException:
    Logger.exception("Exception message")
