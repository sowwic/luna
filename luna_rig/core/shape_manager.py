import os
import pymel.core as pm

import luna
import luna_rig
from luna import Logger
from luna.utils import fileFn
from luna.utils import enumFn
from luna import static
from luna.static import directories
from luna_rig.functions import curveFn


class ShapeManager:

    SHAPES_LIB = directories.SHAPES_LIB_PATH
    COPIED_SHAPE_FILE = "luna_copied_shape.json"
    COPIED_COLOR_FILE = "luna_copied_color.json"

    @classmethod
    def get_shapes(cls, node):
        node = pm.PyNode(node)
        shapes_list = []
        if isinstance(node, luna_rig.nt.Transform):
            child_shapes = node.getShapes()
        elif isinstance(node, luna_rig.nt.Shape):
            child_shapes = node.getTransform().getShapes()
        if not child_shapes:
            Logger.warning("No child shapes found for {0}".format(node))
            return []

        elif isinstance(child_shapes[0], luna_rig.nt.NurbsCurve):
            for shape_node in child_shapes:
                shape_data = curveFn.get_curve_data(shape_node)
                shapes_list.append(shape_data)

        return shapes_list

    @classmethod
    def set_shape_from_lib(cls, node, shape_name):
        node = pm.PyNode(node)
        # Store default values
        default_color = 0
        old_color = default_color

        # Get child shapes
        if isinstance(node, luna_rig.nt.Transform):
            child_shapes = node.getShapes()
        elif isinstance(node, luna_rig.nt.Shape):
            node = node.getTransform()
            child_shapes = node.getShapes()
        # Get old shapes color
        if child_shapes:
            old_color = child_shapes[0].overrideColor.get()

        # Iterate over loaded shape
        loaded_shape_list = cls.load_shape_from_lib(shape_name)
        cls.apply_shape(node, loaded_shape_list, default_color=old_color)
        pm.select(node, r=1)

    @classmethod
    def apply_shape(cls, node, shape_list, default_color=0):
        if not pm.objExists(node):
            return False
        node = pm.PyNode(node)  # type: luna_rig.nt.Transform
        pm.delete(node.getShapes())
        line_width = luna.Config.get(luna.RigVars.line_width, default=2.0, cached=True)  # type: float
        for index, shape_dict in enumerate(shape_list):
            # Create temporary curve
            tmp_curve = pm.curve(p=shape_dict.get("points"), k=shape_dict.get("knots"), d=shape_dict.get("degree"))
            new_shape_node = tmp_curve.getShape()
            # Parent new shape node to transform
            pm.parent(new_shape_node, node, r=1, s=1)
            pm.delete(tmp_curve)
            # Rename newly creted shape node
            new_shape_node = pm.rename(new_shape_node, str(node) + "Shape" + str(index + 1).zfill(2))
            new_shape_node.overrideEnabled.set(1)
            cls.set_line_width(node, line_width)
            # Set color for new shape
            if "color" in shape_dict.keys():
                cls.set_color(new_shape_node, shape_dict.get("color"))
            else:
                cls.set_color(new_shape_node, default_color)
        return True

    @classmethod
    def load_shape_from_lib(cls, shape_name):
        path = os.path.join(cls.SHAPES_LIB, shape_name + ".json")
        if not os.path.isfile(path):
            Logger.exception("Shape file doesn't exist {0}".format(path))
            path = os.path.join(cls.SHAPES_LIB, "cube.json")
        data = fileFn.load_json(path)  # type: dict
        return data

    @classmethod
    def save_shape(cls, transform, name, path=None):
        if not path:
            path = cls.SHAPES_LIB
        transform = pm.PyNode(transform)
        shape_list = cls.get_shapes(transform)
        save_path = os.path.join(path, name)
        for data_dict in shape_list:
            data_dict.pop("color", None)
        fileFn.write_json(save_path, shape_list)

    @classmethod
    def copy_shape(cls, transform=None):
        if not transform:
            if not pm.selected():
                pm.warning("Select transform to copy shape.")
                return
            transform = pm.selected()[-1]
        cls.save_shape(transform, cls.COPIED_SHAPE_FILE, path=directories.TMP_PATH)
        Logger.info("Copied shape {0}".format(transform))

    @classmethod
    def paste_shape(cls, object_list):
        saved_path = os.path.join(directories.TMP_PATH, cls.COPIED_SHAPE_FILE)
        if not os.path.isfile(saved_path):
            Logger.warning("Shape clipboard is empty")
            return
        if not object_list:
            object_list = pm.selected()

        shape_list = fileFn.load_json(saved_path)
        for obj in object_list:
            if isinstance(obj, luna_rig.nt.Transform):
                old_color = cls.get_color(obj)
                cls.apply_shape(obj, shape_list, default_color=old_color)

    @classmethod
    def copy_color(cls):
        sel = pm.selected()
        if not sel:
            Logger.warning("Select transform to get color from.")
            return
        else:
            transform = sel[-1]
        save_path = os.path.join(directories.TMP_PATH, cls.COPIED_COLOR_FILE)
        data = {"color": cls.get_color(transform)}
        fileFn.write_json(save_path, data)
        Logger.info("Copied color {0}".format(transform))

    @classmethod
    def paste_color(cls):
        saved_path = os.path.join(directories.TMP_PATH, cls.COPIED_COLOR_FILE)
        if not os.path.isfile(saved_path):
            Logger.warning("Color clipboard is empty")
            return
        color_int = fileFn.load_json(saved_path).get("color", 0)
        for obj in pm.selected():
            cls.set_color(obj, color_int)

    @classmethod
    def set_color(cls, nodes, color):
        # Handle nodes
        if not nodes:
            nodes = pm.selected()
        if not isinstance(nodes, list):
            nodes = [nodes]
            nodes = [pm.PyNode(node) for node in nodes]
        # Handle color
        if isinstance(color, enumFn.Enum):
            color = color.value
        elif isinstance(color, str):
            color = static.ColorIndex[color].value
        # Get shape nodes
        shape_nodes = []
        for node in nodes:
            if isinstance(node, luna_rig.nt.Transform):
                shape_nodes += node.getShapes()
            elif isinstance(node, luna_rig.nt.Shape):
                shape_nodes.append(node)
        # Apply color
        for shape in shape_nodes:
            shape.overrideEnabled.set(1)
            shape.overrideColor.set(color)

    @classmethod
    def get_color(cls, node):
        if not isinstance(node, pm.PyNode):
            node = pm.PyNode(node)
        color = 0
        if isinstance(node, luna_rig.nt.Transform):
            shapes = node.getShapes()
            if not shapes:
                Logger.warning("No shapes found for {0}".format(node))
                return color
            child_shape = shapes[0]
            if isinstance(child_shape, luna_rig.nt.NurbsCurve):
                color = child_shape.overrideColor.get()
        else:
            Logger.error("Invalid transform {0}, cant't get color!".format(node))

        return color

    @classmethod
    def set_line_width(cls, transform, value):
        if not isinstance(transform, pm.PyNode):
            transform = pm.PyNode(transform)
        if isinstance(transform, luna_rig.nt.Transform):
            for shape_node in transform.getShapes():
                if isinstance(shape_node, luna_rig.nt.NurbsCurve):
                    shape_node.lineWidth.set(value)
        else:
            Logger.error("Invalid transform {0}, cant't set line width!".format(shape_node))
