import pymel.core as pm


def make_cmuscle(polygon_geo):
    if not isinstance(polygon_geo, pm.PyNode):
        polygon_geo = pm.PyNode(polygon_geo)

    pm.select(polygon_geo, r=True)
    pm.mel.eval('cMuscle_makeMuscle(0);')
    muscle_object_node = polygon_geo.getShapes()[-1]
    return muscle_object_node


def rig_keepout(transforms):
    pm.select(transforms, r=True)
    pm.mel.eval('cMuscle_rigKeepOutSel();')
    keep_out_nodes = []
    for trs in transforms:
        keep_out_nodes.append(pm.listRelatives(trs, children=True)[0])
    return keep_out_nodes


def connect_muscles_to_keepout(keep_out_rigs, muscle_geo):
    pm.select(keep_out_rigs, r=1)
    pm.select(muscle_geo, add=1)
    pm.mel.eval('cMuscle_keepOutAddRemMuscle(1);')
