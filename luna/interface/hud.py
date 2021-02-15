import pymel.core as pm
from luna import Logger
from luna import Config
from luna import HudVars
from luna.utils import environFn


class LunaHUD:
    HUD_NAME = "LunaHUD"
    UPDATE_EVENT = "SceneOpened"
    SECTION = Config.get(HudVars.section, default=7)  # type: int
    BLOCK = Config.get(HudVars.block, default=5)  # type: int
    BLOCK_SIZE = "medium"
    FONT_SIZE = "large"

    @classmethod
    def create(cls):
        hud_instance = None
        Logger.info("Building HUD...")
        cls.SECTION = Config.get(HudVars.section, default=7)
        cls.BLOCK = Config.get(HudVars.block, default=5)

        # Delete old
        cls.remove()
        try:
            hud_instance = pm.headsUpDisplay(cls.HUD_NAME,
                                             allowOverlap=True,
                                             section=cls.SECTION,
                                             block=cls.BLOCK,
                                             blockSize=cls.BLOCK_SIZE,
                                             labelFontSize=cls.FONT_SIZE,
                                             command=cls.get_hud_text,
                                             event=cls.UPDATE_EVENT)
            Logger.info("Successfully created HUD: {0}".format(cls.HUD_NAME))
        except RuntimeError:
            Logger.error("HUD position ({0}:{1}) is occupied by another HUD. Use configer to select other block/section.".format(cls.SECTION, cls.BLOCK))

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
    def get_hud_text():
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
