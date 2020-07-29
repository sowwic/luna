from Luna.utils.enumFn import Enum


class OppositeSide(Enum):
    L = "R"
    R = "L"


class Character:
    node = "C_characterNode_CTL"
    masterCtl = "C_masterWalk_CTL"
    geometry = "geometry_GRP"
    joints = "joints_GRP"
    locators = "locators_GRP"
    worldSpace = "C_worldSpace_LOC"


class AssetType(Enum):
    character = "C"
    prop = "P"
    vehicle = "V"
    enviroment = "E"
    other = "A"


class ComponentType(Enum):
    mesh = "vtx"
    nurbsSurface = "cv"
    nurbsCurve = "cv"


class ComponentDepth(Enum):
    mesh = 1
    nurbsSurface = 2
    nurbsCurve = 1


class JointLabelSide(Enum):
    C = 0
    L = 1
    R = 2
    NoSide = 3


class JointLabelType(Enum):
    NoType = 0
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
    indexFinger = 19
    middleFinger = 20
    ringFinger = 21
    pinkyFinger = 22
    extraFinger = 23
    bigToe = 24
    indexToe = 25
    middleToe = 26
    ringToe = 27
    pinkyToe = 28
    footThumb = 29


if __name__ == "__main__":
    print(Character.geometry)
