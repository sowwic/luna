import pymel.core as pm
from Luna import Logger
try:
    from Luna.rig.functions import jointFn
    reload(jointFn)
except ImportError:
    Logger.exception("Failed to reload jointFn")

original_chain = ["c_spine_ik_01_jnt", "c_spine_ik_02_jnt", "c_spine_ik_03_jnt"]


def create_test_scene():
    pm.newFile(force=1)
    pm.joint(n="c_spine_ik_01_jnt", p=[-1.447, 0, -0.979])
    pm.joint(n="c_spine_ik_02_jnt", p=[6.67, 0, 0], r=1)
    pm.joint(n="c_spine_ik_03_jnt", p=[5.06, 0, 0], r=1)
    pm.joint(n="c_spine_ik_04_jnt", p=[5.06, 0, 0], r=1)


def joint_chain_test():
    joint_chain = jointFn.joint_chain(start_joint=original_chain[1], end_joint=original_chain[-1])
    Logger.debug("Joint chain: {0}".format(joint_chain))


def duplicate_chain_test():
    new_chain = jointFn.duplicate_chain(original_chain, replace_type="fk")


if __name__ == "__main__":
    create_test_scene()
    duplicate_chain_test()
