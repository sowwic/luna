import pymel.core as pm
from luna import Logger
from luna import Config
from luna import LunaVars
import luna.utils.enumFn as enumFn
import luna.utils.fileFn as fileFn
import luna_rig
import luna_rig.functions.curveFn as curveFn
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.importexport as importexport
import luna_rig.core.shape_manager as shape_manager


class MarkingMenu(object):

    NAME = "luna_marking_menu"

    class Modes(enumFn.Enum):
        ANIMATOR = 0
        RIGGER = 1

    @staticmethod
    def __null_cmd():
        pass

    @classmethod
    def create(cls):
        Logger.info("Building marking menu...")
        cls.__delete_old()
        pm.popupMenu(cls.NAME, mm=1, aob=1, button=2, ctl=1, alt=1, sh=0, p="viewPanes", pmo=0, pmc=cls.__populate)
        Logger.info("Successfully added marking menu: (CTL+ALT+MMB)")

    @classmethod
    def __delete_old(cls):
        if pm.popupMenu(cls.NAME, ex=1):
            pm.deleteUI(cls.NAME)

    @classmethod
    def __populate(cls, root_menu, parent):
        # Delete old items
        pm.popupMenu(cls.NAME, mm=1, e=1, dai=1)
        # Populate menu based on selection
        selection = pm.selected()
        if not selection:
            return
        is_rigging_mode = Config.get(LunaVars.marking_menu_mode, default=1, stored=True)
        if is_rigging_mode:
            if luna_rig.Control.is_control(selection[-1]):
                cls.__add_rigger_control_actions(root_menu, selection)
            elif isinstance(selection[-1], luna_rig.nt.Joint):
                cls.__add_joint_actions(root_menu, selection)
        else:
            if luna_rig.Control.is_control(selection[-1]):
                cls.__add_animator_control_actions(root_menu, selection)

    @classmethod
    def __add_animator_control_actions(cls, root_menu, selection):
        selected_control = luna_rig.Control(selection[-1])
        bind_pose_menu = pm.subMenuItem(p=root_menu, l="Bind pose", rp="N")
        pm.menuItem(p=bind_pose_menu, l="Asset bind pose", rp="N", c=lambda *args: selected_control.character.to_bind_pose(), i=fileFn.get_icon_path("bindpose.png"))
        pm.menuItem(p=bind_pose_menu, l="Component bind pose", rp="E", c=lambda *args: selected_control.connected_component.to_bind_pose(), i=fileFn.get_icon_path("bodyPart.png"))
        pm.menuItem(p=bind_pose_menu, l="Control bind pose", rp="W", c=lambda *args: selected_control.to_bind_pose(), i=fileFn.get_icon_path("control.png"))
        pm.menuItem(p=root_menu, l="Select component controls", rp="E", c=lambda *args: selected_control.connected_component.select_controls())

    @classmethod
    def __add_rigger_control_actions(cls, root_menu, selection):
        selected_control = luna_rig.Control(selection[-1])
        pm.menuItem(p=root_menu, l="Load shape", rp="E", c=lambda *args: importexport.CtlShapeManager.load_shape_from_lib(), i=fileFn.get_icon_path("library.png"))
        pm.menuItem(p=root_menu, l="Copy shape", rp="N", c=shape_manager.ShapeManager.copy_shape, i=fileFn.get_icon_path("copyCurve.png"))
        pm.menuItem(p=root_menu, l="Paste shape", rp="NE", c=lambda *args: shape_manager.ShapeManager.paste_shape(selection), i=fileFn.get_icon_path("pasteCurve.png"))
        pm.menuItem(p=root_menu, l="Copy color", rp="S", c=lambda *args: shape_manager.ShapeManager.copy_color(), i=fileFn.get_icon_path("copyColor.png"))
        pm.menuItem(p=root_menu, l="Paste color", rp="SE", c=lambda *args: shape_manager.ShapeManager.paste_color(), i=fileFn.get_icon_path("pasteColor.png"))
        pm.menuItem(p=root_menu, l="Select CVs", rp="W", c=lambda *args: curveFn.select_cvs(), i=fileFn.get_icon_path("cvs.png"))
        adjust_shape_menu = pm.subMenuItem(p=root_menu, l="Adjust shape", rp="NW")
        pm.menuItem(p=adjust_shape_menu, l="Mirror shape YZ", rp="N", c=lambda *args: selected_control.mirror_shape())
        pm.menuItem(p=adjust_shape_menu, l="Flip shape YZ", rp="NE", c=lambda *args: curveFn.flip_shape(selected_control.transform))
        pm.menuItem(p=adjust_shape_menu, l="Mirror shape to opposite control", rp="NW", c=lambda *args: selected_control.mirror_shape_to_opposite())
        bind_pose_menu = pm.subMenuItem(p=root_menu, l="Bind pose", rp="SW")
        pm.menuItem(p=bind_pose_menu, l="Asset bind pose", rp="N", c=lambda *args: selected_control.character.to_bind_pose(), i=fileFn.get_icon_path("bindpose.png"))
        pm.menuItem(p=bind_pose_menu, l="Component bind pose", rp="E", c=lambda *args: selected_control.connected_component.to_bind_pose(), i=fileFn.get_icon_path("bodyPart.png"))
        pm.menuItem(p=bind_pose_menu, l="Control bind pose", rp="W", c=lambda *args: selected_control.to_bind_pose(), i=fileFn.get_icon_path("control.png"))
        pm.menuItem(p=root_menu, l="Select component controls", rp="E", c=lambda *args: selected_control.connected_component.select_controls())

        if selected_control.connected_component:
            pm.menuItem(p=root_menu, l=str(selected_control.connected_component), en=0)
            for label, data_dict in selected_control.connected_component.actions_dict.items():
                pm.menuItem(p=root_menu, l=label, c=lambda *args: data_dict.get("callback", cls.__null_cmd)(), i=fileFn.get_icon_path(data_dict.get("icon")))

    @classmethod
    def __add_joint_actions(cls, root_menu, selection):
        pm.menuItem(p=root_menu, l="Joint chain from selection", rp="E", c=lambda *args: jointFn.create_chain(joint_list=selection), i="kinJoint.png")
        pm.menuItem(p=root_menu, l="Mirror joints", rp="W", c=lambda *args: jointFn.mirror_chain(chains=selection), i="mirrorJoint.png")


if __name__ == "__main__":
    MarkingMenu.create()
