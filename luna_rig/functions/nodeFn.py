import pymel.core as pm
import luna
import luna_rig
import luna_rig.functions.nameFn as nameFn


def create_locator(at_object=None):
    locator = pm.spaceLocator(n=nameFn.generate_name("space", "temp", "loc"))
    match_object = pm.selected()[-1] if pm.selected() else at_object
    if match_object:
        match_rot = luna.Config.get(luna.ToolVars.locator_match_orient, default=False)
        match_pos = luna.Config.get(luna.ToolVars.locator_match_position, default=True)
        pm.matchTransform(locator, match_object, pos=match_pos, rot=match_rot)


def create(node_type, name, side, suffix=None, override_index=None, *args, **kwargs):
    if not suffix:
        pass
    node = pm.createNode(node_type,
                         n=nameFn.generate_name(name, side, suffix, override_index=override_index),
                         *args,
                         **kwargs)  # type: luna_rig.nt.DependNode
    return node
