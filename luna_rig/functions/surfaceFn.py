import pymel.core as pm
import pymel.api as pma
import luna_rig
from luna import Logger
import luna_rig.functions.apiFn as apiFn
import luna_rig.functions.curveFn as curveFn


def get_surface_data(surface_node):
    # type: (luna_rig.nt.NurbsSurface) -> dict
    """Get surface data

    :param surface_node: Surface to get data from.
    :type surface_node: str or luna_rig.nt.NurbsSurface
    :return: Surface data as dict
    :rtype: dict
    """
    surface_node = pm.PyNode(surface_node)
    if isinstance(surface_node, luna_rig.nt.Transform):
        surface_node = surface_node.getShape()
    if not isinstance(surface_node, luna_rig.nt.NurbsSurface):
        Logger.exception(
            "Invalid shape node type, expected NurbsSurface, got {0}".format(surface_node))
        raise RuntimeError("Faield to get surface data")

    # MObject
    mobj = apiFn.get_MObject(surface_node)
    mfn_surface = pma.MFnNurbsSurface(mobj)
    # Cvs
    cv_array = pma.MPointArray()
    mfn_surface.getCVs(cv_array)
    points = []
    for i in range(cv_array.length()):
        points.append((cv_array[i].x, cv_array[i].y, cv_array[i].z))
    # Knots
    knots_u_array = pma.MDoubleArray()
    knots_v_array = pma.MDoubleArray()
    mfn_surface.getKnotsInU(knots_u_array)
    mfn_surface.getKnotsInV(knots_v_array)
    knots_u = []
    knots_v = []
    for i in range(knots_u_array.length()):
        knots_u.append(knots_u_array[i])
    for i in range(knots_v_array.length()):
        knots_v.append(knots_v_array[i])
    # Degree
    degree_u = mfn_surface.degreeU()
    degree_v = mfn_surface.degreeV()
    # Form
    form_u = mfn_surface.formInU()
    form_v = mfn_surface.formInV()

    # Store data
    data_dict = {"points": points,
                 "knots_u": knots_u,
                 "knots_v": knots_v,
                 "degree_u": degree_u,
                 "degree_v": degree_v,
                 "form_u": form_u,
                 "form_v": form_v}

    return data_dict


def loft_from_points(points, width=1, side_vector=[1, 0, 0], history=False):
    # type: (list[float], float, list[float], bool) -> luna_rig.nt.NurbsSurface
    move_vector1 = [value * -width for value in side_vector]
    move_vector2 = [value * width for value in side_vector]
    curve1 = curveFn.curve_from_points("curve", degree=1, points=points)
    curve2 = curveFn.curve_from_points("curve", degree=1, points=points)
    pm.move(curve1, move_vector1)
    pm.move(curve2, move_vector2)
    loft_result = pm.loft(curve1, curve2, ar=1, ch=history, degree=1)[
        0]  # type: luna_rig.nt.NurbsSurface
    if not history:
        pm.delete([curve1, curve2])
    return loft_result


def rebuild_1_to_3(surface, history=False):
    # type: (luna_rig.nt.NurbsSurface | str, bool) -> luna_rig.nt.NurbsSurface
    if not isinstance(surface, pm.PyNode):
        surface = pm.PyNode(surface)  # type: luna_rig.nt.NurbsSurface
    if surface.numSpansInU() > surface.numSpansInV():
        degree_u = 3
        degree_v = 1
    else:
        degree_v = 3
        degree_u = 1
    pm.rebuildSurface(surface, du=degree_u, dv=degree_v, su=surface.numSpansInU(),
                      sv=surface.numSpansInV(), ch=history)
