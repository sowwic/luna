from Luna import Logger

try:
    from Luna.interface.menu.functions import main_menu
except Exception as e:
    Logger.exception("Failed to import modules", exc_info=e)

try:
    reload(main_menu)
except Exception as e:
    Logger.exception("Failed to reload modules", exc_info=e)
