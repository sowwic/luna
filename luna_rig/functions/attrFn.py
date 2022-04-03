import pymel.core as pm
from luna import Logger


def add_meta_attr(nodes):
    """Add metaParent attribute to node.

    :param node: Node to add attribute to
    :type node: str or PyNode
    :return: Added attribute
    :rtype: pm.Attribute
    """
    if not isinstance(nodes, list):
        nodes = [nodes]
    for node in nodes:
        if not isinstance(node, pm.PyNode):
            node = pm.PyNode(node)
        if not node.hasAttr("metaParent"):
            node.addAttr("metaParent", at="message")


def lock(node, attributes, channelBox=False, key=False):
    locked_attrs = []
    for attr in attributes:
        pm.setAttr(node + "." + attr, lock=1, cb=channelBox, k=key)
        locked_attrs.append("." + attr)
    return locked_attrs


def get_enums(attribute):
    """Get enums values as sorted list

    :param attribute: Attribute to get enums from.
    :type attribute: pm.Attribute
    :return: List of enums as list of tuples (name, index)
    :rtype: list[(str, int)]
    """
    try:
        enum_list = attribute.getEnums().items()
        enum_list = sorted(enum_list, key=lambda pair: pair[1])
    except TypeError:
        return []
    return enum_list


def add_divider(node, attr_name="divider"):
    if not isinstance(node, pm.PyNode):
        node = pm.PyNode(node)
    node.addAttr(attr_name, at="enum", en=["--------------"])
    node.attr(attr_name).set(channelBox=True)
    node.attr(attr_name).lock()


def transfer_attr(source, destination, attr_list=None, connect=False, ** kwargs):
    # type: (pm.PyNode, pm.PyNode, list[pm.Attribute], bool, dict) -> dict
    attr_alias = {}
    attr_list = attr_list if attr_list is not None else []
    if not attr_list:
        transfer_list = source.listAttr(k=1, r=1, s=1, **kwargs)
    else:
        transfer_list = attr_list
    for attr in transfer_list:
        if not attr.exists() or attr.isCompound() or attr in source.listAttr(ra=1):
            continue
        if destination.hasAttr(attr.attrName(longName=True)):
            Logger.warning("{0}: clashing attr {1}, skipping transfer...".format(
                destination, attr.attrName()))
            continue
        try:
            if attr.type() == "enum":
                enum_names = [enum[0] for enum in get_enums(attr)]
                destination.addAttr(attr.attrName(longName=True), at="enum",
                                    en=enum_names, dv=attr.get(), k=1)
            else:
                min_value = attr.getMin()
                max_value = attr.getMax()
                default_val = attr.get()
                if min_value is None and max_value is None:
                    destination.addAttr(attr.attrName(longName=True),
                                        at=attr.type(), k=1, dv=default_val)
                elif min_value is None and max_value is not None:
                    destination.addAttr(attr.attrName(longName=True),
                                        at=attr.type(), k=1, max=max_value, dv=default_val)
                elif min_value is not None and max_value is None:
                    destination.addAttr(attr.attrName(longName=True),
                                        at=attr.type(), k=1, min=min_value, dv=default_val)
                else:
                    destination.addAttr(attr.attrName(longName=True), at=attr.type(),
                                        k=1, min=min_value, max=max_value, dv=default_val)
            # Store attr aliases
            attr_alias[attr] = destination.attr(attr.attrName(longName=True))
        except Exception:
            Logger.exception("Failed to transfer attr: {0}".format(attr))

    if connect:
        for orig_attr, copied_attr in attr_alias.items():
            if orig_attr.isConnected():
                continue
            copied_attr.connect(orig_attr)
    return attr_alias


def connect_transform_attrs(src_transform, dest_transform):
    if not isinstance(src_transform, pm.PyNode):
        src_transform = pm.PyNode(src_transform)
    if not isinstance(dest_transform, pm.PyNode):
        src_transform = pm.PyNode(dest_transform)
    src_transform.translate.connect(dest_transform.translate)
    src_transform.rotate.connect(dest_transform.rotate)
    src_transform.scale.connect(dest_transform.scale)
