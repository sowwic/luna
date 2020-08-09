import pymel.core as pm
from Luna import Logger
from Luna.core.config import Config
from Luna.core.config import HudVars
from Luna.utils import environFn


class LunaHud:
    HUD_NAME = "LunaHud"
    UPDATE_EVENT = "SceneOpened"
    SECTION = Config.get(HudVars.section, default=7)
    BLOCK = Config.get(HudVars.block, default=5)
    BLOCK_SIZE = "medium"
    FONT_SIZE = "large"

    @classmethod
    def create(cls):
        hud_instance = None
        Logger.info("Building {0}...".format(cls.HUD_NAME))

        # Delete old
        cls.remove()
        hud_instance = pm.headsUpDisplay(cls.HUD_NAME,
                                         section=cls.SECTION,
                                         block=cls.BLOCK,
                                         blockSize=cls.BLOCK_SIZE,
                                         labelFontSize=cls.FONT_SIZE,
                                         command=cls.getHudText,
                                         event=cls.UPDATE_EVENT)
        Logger.info("Successfully created HUD: {0}".format(cls.HUD_NAME))

        return hud_instance

    @classmethod
    def refresh(cls):
        try:
            pm.headsUpDisplay(cls.HUD_NAME, r=1)
        except BaseException:
            Logger.exception("Failed to refresh {0}".format(cls.HUD_NAME))

    @classmethod
    def remove(cls):
        if pm.headsUpDisplay(cls.HUD_NAME, ex=1):
            pm.headsUpDisplay(cls.HUD_NAME, rem=1)

    @staticmethod
    def getHudText():
        stringToDraw = ""
        current_project = environFn.get_project_var()
        current_asset = environFn.get_asset_var()
        if current_project:
            stringToDraw += current_project.name
            if current_asset:
                stringToDraw += " :: {0}".format(current_asset.name)
        else:
            stringToDraw = " "

        return stringToDraw
