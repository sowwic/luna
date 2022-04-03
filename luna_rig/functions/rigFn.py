import pymel.core as pm
import pymel.api as pma
import luna
import luna_rig
from luna import Logger


def list_controls():
    """Get all controller nodes in the scene as Control instances

    :return: List of controls
    :rtype: list(Control)
    """
    transforms = pm.controller(ac=1, q=1)
    ctls = []
    for each in transforms:
        try:
            instance = luna_rig.Control(each)  # type :control.Control
        except Exception:
            Logger.exception("Failed to create control instance from {0}".format(each))
            continue
        ctls.append(instance)
    return ctls


def get_build_character():
    """Gets character component of current build.

    :return: Character meta node as Character instance.
    :rtype: Character
    """
    current_asset = luna.workspace.Asset.get()
    all_characters = luna_rig.MetaNode.list_nodes(of_type=luna_rig.components.Character)
    for char_node in all_characters:
        if char_node.pynode.characterName.get() == current_asset.name:
            return char_node
    Logger.error("Failed to find build character!")


def get_param_ctl_locator(side, anchor_transform, move_axis="x", mult=1):
    current_char = get_build_character()
    if not current_char:
        clamped_size = current_char.clamped_size
    else:
        clamped_size = 1.0

    locator = pm.spaceLocator(n="param_loc")  # type: luna_rig.nt.Transform
    end_jnt_vec = anchor_transform.getTranslation(space="world")  # type:pma.MVector
    side_mult = -1 if side == "r" else 1
    # if move_axis == "x":
    if "x" in move_axis:
        end_jnt_vec.x += clamped_size * 20 * side_mult * mult
    # elif move_axis == "y":
    if "y" in move_axis:
        end_jnt_vec.y += clamped_size * 20 * side_mult * mult
    # elif move_axis == "z":
    if "z" in move_axis:
        end_jnt_vec.z += clamped_size * 20 * side_mult * mult
    locator.translate.set(end_jnt_vec)
    return locator


def delete_all_meta_nodes():
    for node in luna_rig.MetaNode.list_nodes():
        if pm.objExists(node.pynode):
            pm.delete(node.pynode)


def set_node_selectable(node, value):
    state_values = {True: 0,
                    False: 2}
    node.overrideEnabled.set(1)
    node.overrideDisplayType.set(state_values.get(value, 0))


def selected_control_bind_pose():
    selected = pm.selected()
    if not selected:
        return
    controls = []
    for item in selected:
        if luna_rig.Control.is_control(item):
            controls.append(luna_rig.Control(item))
    for ctl in controls:
        ctl.to_bind_pose()


def asset_bind_pose():
    selected = pm.selected()
    if not selected:
        return
    if not luna_rig.Control.is_control(selected[-1]):
        return
    character = luna_rig.Control(selected[-1]).character
    if not character:
        Logger.warning("{0}: connected character not found.")
        return
    character.to_bind_pose()
