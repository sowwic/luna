import pymel.core as pm
from luna import Logger
from luna import Config
from luna import LunaVars
import luna.utils.enumFn as enumFn
import luna.utils.fileFn as fileFn
import luna_rig
import luna_rig.functions.curveFn as curveFn
import luna_rig.functions.jointFn as jointFn
import luna_rig.functions.transformFn as transformFn
import luna_rig.functions.nodeFn as nodeFn
import luna_rig.importexport as importexport
import luna_rig.core.shape_manager as shape_manager


class MarkingMenu(object):
    class Modes(enumFn.Enum):
        ANIMATOR = 0
        RIGGER = 1

    NAME = "luna_marking_menu"
    MODE = Config.get(LunaVars.marking_menu_mode, default=Modes.RIGGER.value)

    @staticmethod
    def __null_cmd():
        pass

    @classmethod
    def create(cls):
        Logger.info("Building marking menu...")
        cls._delete_old()
        pm.popupMenu(cls.NAME, mm=1, aob=1, button=2, ctl=1, alt=1, sh=0, p="viewPanes", pmo=0, pmc=cls.__populate)
        Logger.info("Successfully added marking menu: (CTL+ALT+MMB)")

    @classmethod
    def _delete_old(cls):
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

        if cls.MODE == cls.Modes.RIGGER.value:
            if luna_rig.Control.is_control(selection[-1]):
                cls.__add_rigger_control_actions(root_menu, selection)
            elif isinstance(selection[-1], luna_rig.nt.Joint):
                cls.__add_joint_actions(root_menu, selection)
            elif isinstance(selection[-1], luna_rig.nt.Transform):
                cls.__add_transform_actions(root_menu, selection)
        else:
            if luna_rig.Control.is_control(selection[-1]):
                cls.__add_animator_control_actions(root_menu, selection)

    @classmethod
    def __add_animator_control_actions(cls, root_menu, selection):
        selected_control = luna_rig.Control(selection[-1])
        pm.menuItem(p=root_menu, l="Select component controls", rp="E", c=lambda *args: selected_control.connected_component.select_controls())
        pm.menuItem(p=root_menu, l="Key component controls", rp="W", c=lambda *args: selected_control.connected_component.key_controls())
        # Bind pose sub menu
        pose_menu = pm.subMenuItem(p=root_menu, l="Pose", rp="N")
        cls.__add_pose_actions(pose_menu, selection)
        # Component actions
        cls.__add_component_actions(root_menu, selected_control)

    @ classmethod
    def __add_rigger_control_actions(cls, root_menu, selection):
        selected_control = luna_rig.Control(selection[-1])

        pm.menuItem(p=root_menu, l="Select CVs", rp="W", c=lambda *args: curveFn.select_cvs(), i=fileFn.get_icon_path("cvs.png"))
        # Adjust shape sub menu
        adjust_shape_menu = pm.subMenuItem(p=root_menu, l="Shape", rp="N")
        cls.__add_shape_actions(adjust_shape_menu, selection)
        pose_menu = pm.subMenuItem(p=root_menu, l="Pose", rp="E")
        cls.__add_pose_actions(pose_menu, selection)
        # Component menu
        cls.__add_component_actions(root_menu, selected_control)

    @classmethod
    def __add_component_actions(cls, root_menu, selected_control):
        if not selected_control.connected_component:
            return
        pm.menuItem(p=root_menu, l=str(selected_control.connected_component), en=0)
        # Space switching
        if selected_control.spaces:
            spaces_menu = pm.subMenuItem(p=root_menu, l="Spaces")
            for space_name in selected_control.spaces_dict.keys():
                pm.menuItem(p=spaces_menu, l=space_name, c=lambda triggered=True, name=space_name, *args: selected_control.switch_space(selected_control.spaces_dict.get(name)))
        # Actions callbacks
        if hasattr(selected_control.connected_component, "actions_dict"):
            for label, data_dict in selected_control.connected_component.actions_dict.items():
                pm.menuItem(p=root_menu, l=label, c=lambda *args: data_dict.get("callback", cls.__null_cmd)(), i=fileFn.get_icon_path(data_dict.get("icon")))

    @classmethod
    def __add_pose_actions(cls, root_menu, selection):
        selected_control = luna_rig.Control(selection[-1])
        pm.menuItem(p=root_menu,
                    l="Mirror pose (Behaviour)",
                    rp="SW",
                    c=lambda *args: [luna_rig.Control(trs).mirror_pose(behavior=True, direction="source") for trs in selection if luna_rig.Control.is_control(trs)])
        pm.menuItem(p=root_menu,
                    l="Mirror pose (No behaviour)",
                    rp="S",
                    c=lambda *args: [luna_rig.Control(trs).mirror_pose(behavior=False, direction="source") for trs in selection if luna_rig.Control.is_control(trs)])
        pm.menuItem(p=root_menu, l="Asset bind pose", rp="N", c=lambda *args: selected_control.character.to_bind_pose(), i=fileFn.get_icon_path("bindpose.png"))
        pm.menuItem(p=root_menu, l="Component bind pose", rp="NE", c=lambda *args: selected_control.connected_component.to_bind_pose(), i=fileFn.get_icon_path("bodyPart.png"))
        pm.menuItem(p=root_menu,
                    l="Control bind pose",
                    rp="E",
                    c=lambda *args: [luna_rig.Control(trs).to_bind_pose() for trs in selection if luna_rig.Control.is_control(trs)],
                    i=fileFn.get_icon_path("control.png"))

    @classmethod
    def __add_shape_actions(cls, root_menu, selection):
        selected_control = luna_rig.Control(selection[-1])
        pm.menuItem(p=root_menu, l="Load shape", rp="E", c=lambda *args: importexport.CtlShapeManager.load_shape_from_lib(), i=fileFn.get_icon_path("library.png"))
        pm.menuItem(p=root_menu, l="Copy shape", rp="N", c=shape_manager.ShapeManager.copy_shape, i=fileFn.get_icon_path("copyCurve.png"))
        pm.menuItem(p=root_menu, l="Paste shape", rp="NE", c=lambda *args: shape_manager.ShapeManager.paste_shape(selection), i=fileFn.get_icon_path("pasteCurve.png"))
        pm.menuItem(p=root_menu, l="Copy color", rp="S", c=lambda *args: shape_manager.ShapeManager.copy_color(), i=fileFn.get_icon_path("copyColor.png"))
        pm.menuItem(p=root_menu, l="Paste color", rp="SE", c=lambda *args: shape_manager.ShapeManager.paste_color(), i=fileFn.get_icon_path("pasteColor.png"))
        pm.menuItem(p=root_menu, l="Mirror shape YZ", rp="W", c=lambda *args: selected_control.mirror_shape())
        pm.menuItem(p=root_menu, l="Flip shape YZ", rp="SW", c=lambda *args: curveFn.flip_shape(selected_control.transform))
        pm.menuItem(p=root_menu, l="Mirror shape to opposite control", rp="NW", c=lambda *args: selected_control.mirror_shape_to_opposite())
        # Bind pose sub menu
        bind_pose_menu = pm.subMenuItem(p=root_menu, l="Bind pose", rp="SW")
        pm.menuItem(p=bind_pose_menu, l="Asset bind pose", rp="N", c=lambda *args: selected_control.character.to_bind_pose(), i=fileFn.get_icon_path("bindpose.png"))
        pm.menuItem(p=bind_pose_menu, l="Component bind pose", rp="E", c=lambda *args: selected_control.connected_component.to_bind_pose(), i=fileFn.get_icon_path("bodyPart.png"))
        pm.menuItem(p=bind_pose_menu, l="Control bind pose", rp="W", c=lambda *args: selected_control.to_bind_pose(), i=fileFn.get_icon_path("control.png"))
        pm.menuItem(p=root_menu, l="Select component controls", rp="E", c=lambda *args: selected_control.connected_component.select_controls())

    @ classmethod
    def __add_joint_actions(cls, root_menu, selection):
        pm.menuItem(p=root_menu, l="Joint chain from selection", rp="E", c=lambda *args: jointFn.create_chain(joint_list=pm.selected(type="joint")), i="kinJoint.png")
        pm.menuItem(p=root_menu, l="Mirror joints", rp="W", c=lambda *args: jointFn.mirror_chain(chains=selection), i=fileFn.get_icon_path("mirrorJoint.png"))
        # Transform menu
        transform_menu = pm.subMenuItem(p=root_menu, l="Transform", rp="N")
        cls.__add_transform_actions(transform_menu, selection)

    @ classmethod
    def __add_transform_actions(cls, root_menu, selection):
        pm.menuItem(p=root_menu, l="Create locator", rp="E", c=lambda *args: nodeFn.create_locator(at_object=selection[-1]), i="locator.png")
        # Match position sub menu
        match_position_menu = pm.subMenuItem(p=root_menu, l="Match", rp="N")
        pm.menuItem(p=match_position_menu, l="Position", rp="S", c=lambda *args: pm.matchTransform(selection[-1], selection[0], pos=True))
        pm.menuItem(p=match_position_menu, l="Rotation", rp="SW", c=lambda *args: pm.matchTransform(selection[-1], selection[0], rot=True))
        pm.menuItem(p=match_position_menu, l="Object center", rp="N", c=lambda *args: transformFn.snap_to_object_center(selection[0], selection[1:]))
        pm.menuItem(p=match_position_menu, l="Components center", rp="W", c=lambda *args: transformFn.snap_to_components_center(selection[:-1], selection[-1]))


if __name__ == "__main__":
    MarkingMenu.create()
