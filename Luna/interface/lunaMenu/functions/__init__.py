from Luna import Logger

try:
    from Luna.interface.lunaMenu.functions import mainMenu
except Exception as e:
    Logger.exception("Failed to import modules", exc_info=e)

try:
    reload(mainMenu)
except Exception as e:
    Logger.exception("Failed to reload modules", exc_info=e)
