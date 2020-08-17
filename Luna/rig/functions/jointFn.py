import pymel.core as pm
from Luna import Logger
from Luna.rig.functions import nameFn


def duplicate_chain(original_chain=[], start_joint=None,
                    end_joint=None,
                    add_name="",
                    replace_name="",
                    replace_side="",
                    replace_suffix=""):
    if not original_chain:
        original_chain = joint_chain(start_joint, end_joint)

    new_chain = pm.duplicate(original_chain, po=1, rc=1)
    for old_jnt, new_jnt in zip(original_chain, new_chain):
        original_name = nameFn.deconstruct_name(str(old_jnt))
        if replace_name:
            original_name.name = replace_name
        if add_name:
            original_name.name += add_name
        if replace_side:
            original_name.side = replace_side
        if replace_suffix:
            original_name.suffix = replace_suffix

        new_name = nameFn.generate_name(original_name.name, original_name.side, original_name.suffix)
        new_jnt.rename(new_name)

    return new_chain


def joint_chain(start_joint, end_joint=None):
    """Get joint from start joint. Optionally slice the chain at end joint.

    :param start_joint: First joint in the chain
    :type start_joint: str,PyNode
    :param end_joint: Last joint in the chain, defaults to None
    :type end_joint: str, PyNode, optional
    :return: Joint chain as a list
    :rtype: list
    """
    assert pm.nodeType(start_joint) == 'joint', "{0} is not a joint".format(start_joint)
    start_joint = pm.PyNode(start_joint)
    chain = start_joint.getChildren(type="joint", ad=1) + [start_joint]
    chain.reverse()
    if not end_joint:
        return chain

    # Handle end joint
    assert pm.nodeType(end_joint) == 'joint', "{0} is not a joint".format(end_joint)
    end_joint = pm.PyNode(end_joint)
    chain = chain[:chain.index(end_joint) + 1]

    return chain
