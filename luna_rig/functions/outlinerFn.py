import pymel.core as pm
from luna import Logger
from luna.static import ColorIndex


def hide(node, visibility=False):
    """Hide node

    :param node: Node to hide
    :type node: str or PyNode
    :param visibility: Node visibility attr, defaults to False
    :type visibility: bool, optional
    """
    if pm.objExists(node):
        pm.setAttr(node + '.v', visibility)
        pm.setAttr(node + '.hiddenInOutliner', True)


def fade(node):
    """Fade node in outliner

    :param node: Node to fade
    :type node: str or PyNode
    """
    pm.setAttr(node + '.useOutlinerColor', True)
    pm.setAttr(node + '.outlinerColor', 0.5, 0.5, 0.5)


def set_color(node, color=[0, 0, 0]):
    """Set color in outliner.

    :param node: Node to set color for.
    :type node: str or Pynode
    :param rgb: RGB values, defaults to []
    :type rgb: list, optional
    """
    if isinstance(color, list) or isinstance(color, tuple):
        while len(color) < 3:
            color.append(0.0)
    elif isinstance(color, int):
        color = ColorIndex.index_to_rgb(color)
    elif isinstance(color, str):
        color = ColorIndex.index_to_rgb(ColorIndex[color].value)
    else:
        Logger.exception("Failed to set outliner color: {0}".format(color))
        return
    # Apply colors
    pm.setAttr(node + '.useOutlinerColor', True)
    pm.setAttr(node + '.outlinerColor', color[0], color[1], color[2])
