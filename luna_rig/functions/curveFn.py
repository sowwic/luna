import pymel.core as pm
from luna import Logger
import luna_rig
from luna_rig.functions import transformFn


def get_curve_data(curve):
    curve = pm.PyNode(curve)
    data_dict = {}
    if not isinstance(curve, luna_rig.nt.NurbsCurve):
        Logger.exception("Invalid NurbsCurve {}".format(curve))
        return data_dict

    # Ponts
    points = []
    for i in range(curve.controlPoints.get(s=1)):
        point_xyz = list(curve.controlPoints[i].get())
        points.append(point_xyz)

    data_dict["points"] = points
    data_dict["knots"] = curve.getKnots()
    data_dict["form"] = curve.form().index
    data_dict["degree"] = curve.degree()
    data_dict["color"] = curve.overrideColor.get()

    return data_dict


def curve_from_points(name, degree=1, points=None, parent=None):
    # type: (str, int, list, luna_rig.nt.Transform) -> luna_rig.nt.Transform
    points = points if points is not None else []
    knot_len = len(points) + degree - 1
    knot_vecs = [v for v in range(knot_len)]

    new_curve = pm.curve(n=name, p=points, d=1, k=knot_vecs)  # type: luna_rig.nt.NurbsCurve
    if degree != 1:
        pm.rebuildCurve(new_curve, d=degree, ch=0)
    if parent:
        pm.parent(new_curve, parent)
    return new_curve


def curve_from_transforms(name, degree=1, transforms=None, parent=None):
    # type: (str, int, list[luna_rig.nt.Tranform], luna_rig.nt.Tranform) -> luna_rig.nt.Tranform
    transforms = transforms if transforms is not None else []
    for index in range(0, len(transforms)):
        if not isinstance(transforms[index], pm.PyNode):
            transforms[index] = pm.PyNode(transforms[index])
    points = [trs.getTranslation(space="world") for trs in transforms]
    new_curve = curve_from_points(name, degree=degree, points=points, parent=parent)
    return new_curve


def flip_shape(transform, across="yz"):
    if across not in ["yz", "xy", "xz"]:
        Logger.error("Invalid flip plane: {0}".format(across))
        return
    scale_vec = {"yz": [-1, 1, 1],
                 "xy": [1, 1, -1],
                 "xz": [1, -1, 1]}
    for shape in transform.getShapes():
        pm.scale(shape + ".cv[0:1000]", scale_vec.get(across), os=True)


def mirror_shape(transform, across="yz", behaviour=True, flip=False, flip_across="yz", space="transform"):
    """Mirrors control's shape
    """
    if space == "transform":
        space = transform
    # Create temp transform, parent shapes to it and mirror
    temp_transform = pm.createNode("transform", n="mirror_shape_grp", p=transform)
    for shape in transform.getShapes():
        shape.setParent(temp_transform, r=1)
    transformFn.mirror_xform(temp_transform, across=across, behaviour=behaviour, space=space)
    # Flip shape
    if flip:
        flip_shape(temp_transform, across=flip_across)
    pm.makeIdentity(temp_transform, apply=1)
    # Parent back to control
    for shape in temp_transform.getShapes():
        shape.setParent(transform, r=1)
    pm.delete(temp_transform)
    pm.select(cl=1)


def select_cvs(transform=None):
    if not transform:
        transform = pm.selected()
    if not transform:
        return
    else:
        transform = transform[-1]  # type:luna_rig.nt.Transform
    pm.select(cl=1)
    for shape in transform.getShapes():
        pm.select(shape + ".cv[0:]", add=1)


def insert_end_knots(curve):
    """Inserts extra knots on both ends of the curve.
    NOTE: Curve must be not uniform

    :param curve: Curve transform node
    :type curve: str or PyNode
    """
    if not isinstance(curve, pm.PyNode):
        curve = pm.PyNode(curve)  # type: luna_rig.nt.Transform
    # Get params
    shape_node = curve.getShape()  # type: luna_rig.nt.NurbsCurve
    start_param, end_param = shape_node.getKnotDomain()
    end_insert_param = (end_param - 1.0) + (2.0 / 3.0)
    start_insert_param = 1.0 / 3.0
    # Insert
    pm.insertKnotCurve(curve + ".u[{0}]".format(start_insert_param),
                       ch=0, cos=1, nk=1, add=0, ib=1, rpo=1)
    pm.insertKnotCurve(curve + ".u[{0}]".format(end_insert_param),
                       ch=0, cos=1, nk=1, add=0, ib=1, rpo=1)


def get_skin_persent(curve, skin, cv_index):
    if not isinstance(curve, pm.PyNode):
        curve = pm.PyNode(curve)  # type: luna_rig.nt.Transform
    if not isinstance(skin, pm.PyNode):
        curve = pm.PyNode(skin)  # type: luna_rig.nt.SkinCluster

    skin_percents = []
    for influence_obj in skin.getWeightedInfluence():
        weight = pm.skinPercent(skin, curve.getShape(
        ).cv[cv_index], transform=influence_obj, q=True)
        skin_percents.append((influence_obj, weight))
    return skin_percents
