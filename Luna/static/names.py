from Luna.utils.enumFn import Enum


class OppositeSide(Enum):
    l = "r"  # noqa: E741
    r = "l"


class Character(Enum):
    node = "character_grp"
    control_rig = "control_rig_grp"
    geometry = "geometry_grp"
    deformation_rig = "deformation_rig_grp"
    locators = "locators_grp"
    world_space = "c_world_space_loc"


class ComponentType(Enum):
    mesh = "vtx"
    nurbsSurface = "cv"
    nurbsCurve = "cv"


class ComponentDepth(Enum):
    mesh = 1
    nurbsSurface = 2
    nurbsCurve = 1


class JointLabelSide(Enum):
    c = 0
    l = 1  # noqa: E741
    r = 2
    no_side = 3


class JointLabelType(Enum):
    no_type = 0
    root = 1
    hip = 2
    knee = 3
    foot = 4
    toe = 5
    spine = 6
    neck = 7
    head = 8
    collar = 9
    shoulder = 10
    elbow = 11
    hand = 12
    finger = 13
    thumb = 14
    propA = 15
    propB = 16
    propC = 17
    other = 18
    index_finger = 19
    middle_finger = 20
    ring_finger = 21
    pinky_finger = 22
    extra_finger = 23
    big_toe = 24
    index_toe = 25
    middle_toe = 26
    ring_toe = 27
    pinky_toe = 28
    foot_thumb = 29
