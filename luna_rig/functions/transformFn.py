import pymel.core as pm
import pymel.api as pma
from pymel.core import datatypes

from luna import Logger
import luna.utils.enumFn as enumFn
import luna.static as static
import luna_rig
import luna_rig.functions.nameFn as nameFn
import luna_rig.functions.nodeFn as nodeFn


class WorldVector(enumFn.Enum):
    X = datatypes.Vector(1.0, 0, 0)
    Y = datatypes.Vector(0, 1.0, 0)
    Z = datatypes.Vector(0, 0, 1.0)


# Modified from https://gist.github.com/rondreas/1c6d4e5fc6535649780d5b65fc5a9283
def mirror_xform(transforms=None, across="yz", behavior=True, space="world"):
    """
    :param transforms: Transforms to mirror, defaults to None
    :type transforms: list or str or pm.PyNode, optional
    :param across: Plane to mirror across, options("YZ", "XY", "XZ"), defaults to 'YZ'
    :type across: str, optional
    :param behavior: If behavior should be mirrored, defaults to True
    :type behavior: bool, optional
    :param space: Space to mirror across, valid options(transform or "world") , defaults to "world"
    :type space: str, optional
    :raises ValueError: If invalid object passed as transform.
    :raises ValueError: If invalid mirror plane
    """
    transforms = transforms if transforms is not None else []
    if isinstance(transforms, str) or isinstance(transforms, pm.PyNode):
        transforms = [transforms]
    transforms = [pm.PyNode(node) for node in transforms]  # type: list[luna_rig.nt.Transform]
    # Check to see all provided objects is an instance of pymel transform node,
    if not all(map(lambda x: isinstance(x, pm.nt.Transform), transforms)):
        raise ValueError("Passed node which wasn't of type: Transform")

    # Validate plane which to mirror across
    across = across.lower()
    if across not in ('xy', 'yz', 'xz'):
        raise ValueError("Keyword Argument: 'across' not of accepted value ('xy', 'yz', 'xz').")

    stored_matrices = {}
    for transform in transforms:
        # Get the worldspace matrix, as a list of 16 float values
        if space == "world":
            mtx = pm.xform(transform, q=True, ws=True, m=True)
        else:
            mtx = matrix_to_list(relative_world_matrix(transform, space))
        mtx = mirror_matrix(mtx, behavior=behavior, across=across)
        stored_matrices[transform] = mtx
    for transform in transforms:
        transform.setMatrix(stored_matrices[transform], ws=(space == "world"))


def mirror_matrix(mtx, behavior=True, across="yz"):
    if not isinstance(mtx, list):
        mtx = matrix_to_list(mtx)
    # Invert rotation columns,
    rx = [n * -1 for n in mtx[0:9:4]]
    ry = [n * -1 for n in mtx[1:10:4]]
    rz = [n * -1 for n in mtx[2:11:4]]
    # Invert translation row,
    t = [n * -1 for n in mtx[12:15]]
    # Set matrix based on given plane, and whether to include behavior or not.
    if across == "xy":
        mtx[14] = t[2]    # set inverse of the Z translation
        # Set inverse of all rotation columns but for the one we've set translate to.
        if behavior:
            mtx[0:9:4] = rx
            mtx[1:10:4] = ry
    elif across == "yz":
        mtx[12] = t[0]    # set inverse of the X translation
        if behavior:
            mtx[1:10:4] = ry
            mtx[2:11:4] = rz
    else:
        mtx[13] = t[1]    # set inverse of the Y translation

        if behavior:
            mtx[0:9:4] = rx
            mtx[2:11:4] = rz

    return mtx


def world_matrix(transform):
    """Get transform world matrix

    :param transform: Transform obj
    :type transform: str or pm.PyNode
    :return: World matrix
    :rtype: MMatrix
    """
    transform = pm.PyNode(transform)
    return pma.MMatrix(transform.getMatrix(ws=True))


def relative_world_matrix(transform, parent_space):
    """Get relative matrix

    :param transform: Transform object
    :type transform: str or pm.PyNode
    :param parent_space: Relative space transform
    :type parent_space: str or pm.PyNode
    :return: Relative matrix
    :rtype: MMatrix
    """
    transform = pm.PyNode(transform)
    parent_space = pm.PyNode(parent_space)
    mtx = world_matrix(transform) * world_matrix(parent_space).inverse()
    return mtx


def matrix_to_list(mtx):
    """Convert MMatrix to python list.

    :param mtx: Matrix to convert.
    :type mtx: pymel.api.MMatrix
    :return: Matrix as list
    :rtype: list
    """
    mtx_list = list(mtx)
    flat_list = [value for array in mtx_list for value in list(array)]
    return flat_list


def get_vector(source, destination, space="world"):
    return destination.getTranslation(space=space) - source.getTranslation(space=space)


def snap_to_object_center(target_object, snap_objects):
    centroid = pm.objectCenter(target_object)
    if not isinstance(snap_objects, list):
        snap_objects = [snap_objects]
    center_locator = pm.spaceLocator(n="temp_center_loc")
    center_locator.translate.set(centroid)
    for obj in snap_objects:
        pm.matchTransform(obj, center_locator, pos=True)
    pm.delete(center_locator)


def snap_to_components_center(components, snap_object):
    if not isinstance(snap_object, pm.PyNode):
        snap_object = pm.PyNode(snap_object)
    if not isinstance(snap_object, luna_rig.nt.Transform):
        pm.displayError("Invalid snap object, expected Transform got {0}".format(type(snap_object)))
        return

    # Mesh
    if all([isinstance(comp, pm.MeshVertex) for comp in components]):
        unpacked_verticies = []
        for vtx_pack in components:
            for vtx in vtx_pack:
                unpacked_verticies.append(vtx)
        all_points = [vtx.getPosition(space="world") for vtx in unpacked_verticies]
    # Invalid
    else:
        pm.displayError("Invalid component types: {0}".format([type(comp) for comp in components]))
        return
    # Calculate centroid
    centroid = [0.0, 0.0, 0.0]
    for pt in all_points:
        centroid += pt
    centroid = centroid / len(all_points)
    # Match to centroid
    center_locator = pm.spaceLocator(n="temp_center_loc")
    center_locator.translate.set(centroid)
    pm.matchTransform(snap_object, center_locator, pos=True)
    pm.delete(center_locator)


def get_axis_name_from_vector3(vector3):
    if not isinstance(vector3, pm.dt.Vector):
        vector3 = pm.dt.Vector(*vector3)
    if vector3.x:
        if vector3.x > 0:
            return "x"
        else:
            return "-x"

    if vector3.y:
        if vector3.y > 0:
            return "y"
        else:
            return "-y"

    if vector3.z:
        if vector3.z > 0:
            return "z"
        else:
            return "-z"


def get_world_position(transform):
    return datatypes.FloatVector(pm.xform(transform, sp=True, q=True, ws=True))


def mirror_geometry(transform=None, across='yz', rename=True):
    scaleMap = {"yz": "x",
                "xz": "y",
                "xy": "z"}

    # Prepare
    mirror_object = pm.PyNode(transform)  # type: luna_rig.nt.Transform
    if rename:
        try:
            name_parts = nameFn.deconstruct_name(mirror_object)
            if name_parts.side in static.OppositeSide:
                name_parts.side = static.OppositeSide[name_parts.side]
            new_name = nameFn.generate_name(name_parts.name, name_parts.side, name_parts.suffix)
        except Exception:
            name_parts = None
            Logger.warning(
                "Unable to get old side value for {0}, auto renaming won't be performed.".format(mirror_object))

    original_parent = mirror_object.getParent()

    # Mirror
    mirror_result = pm.duplicate(transform, n=new_name, rc=1)
    mirror_grp = pm.createNode("transform", n="temp_mirror_GRP")
    pm.parent(mirror_result, mirror_grp)
    if scaleMap[across] == "x":
        pm.scale(mirror_grp, -1, scaleX=1)
    elif scaleMap[across] == "y":
        pm.scale(-1, mirror_grp, scaleY=1)
    elif scaleMap[across] == "z":
        pm.scale(-1, mirror_grp, scaleZ=1)
    else:
        raise Exception("Invalid mirror plane {0}".format(across))

    # Get new children names
    if rename:
        for child in pm.listRelatives(mirror_object, ad=1):
            try:
                old_child_name = child.name()
                child_parts = nameFn.deconstruct_name(child)
                if name_parts.side not in static.OppositeSide:
                    Logger.warning("{0} side isn't in {1}. Skipping renaming...".format(
                        child, list(static.OppositeSide)))
                    continue
                child_parts.side = static.OppositeSide[child_parts.side]
                nameFn.rename(child, side=child_parts.side,
                              name=child_parts.name, index=child_parts.index)
                Logger.info('Renamed child {0} -> {1}'.format(old_child_name, child.name()))
            except Exception:
                Logger.warning('Unable to rename child {0}'.format(child))
                continue

    # Parent back and cleanup
    pm.makeIdentity(mirror_grp, apply=1, pn=1)
    if original_parent:
        pm.parent(mirror_result, original_parent)
    else:
        pm.parent(mirror_result, None)

    pm.delete(mirror_grp)


def position_along_curve(curve,
                         transforms,
                         closed_curve=False):
    for index, trs in enumerate(transforms):
        if closed_curve:
            param = float(index) / float(len(transforms))
        else:
            param = float(index) / float(len(transforms) - 1)
        point = pm.pointOnCurve(curve, pr=param, top=1)
        trs.setTranslation(point, space="world")


def attach_to_curve_at_param(curve,
                             transform,
                             param,
                             pt_curve_info_name='pointoncurve',
                             pt_curve_info_side='c'):
    if not isinstance(curve, pm.PyNode):
        curve = pm.PyNode(curve)

    pt_on_curve_info = nodeFn.create('pointOnCurveInfo', pt_curve_info_name,
                                     pt_curve_info_side, suffix="ptcrv")  # type: luna_rig.nt.PointOnCurveInfo
    curve.worldSpace[0].connect(pt_on_curve_info.inputCurve)
    pt_on_curve_info.parameter.set(param)
    pt_on_curve_info.turnOnPercentage.set(1)
    pt_on_curve_info.result.position.connect(transform.translate)
    return pt_on_curve_info


def attach_all_to_curve(curve,
                        transforms,
                        closed_curve=False,
                        pt_curve_info_name='pointoncurve',
                        pt_curve_info_side='c'):
    if not isinstance(curve, pm.PyNode):
        curve = pm.PyNode(curve)

    point_on_curve_nodes = []
    for index, trs in enumerate(transforms):
        if closed_curve:
            param = float(index) / float(len(transforms))
        else:
            param = float(index) / float(len(transforms) - 1)
        pt_on_curve_info = attach_to_curve_at_param(
            curve, trs, param, pt_curve_info_name, pt_curve_info_side)
        point_on_curve_nodes.append(pt_on_curve_info)
    return point_on_curve_nodes


if __name__ == "__main__":
    pass
