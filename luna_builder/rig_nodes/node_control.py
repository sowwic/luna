import luna_rig
from collections import OrderedDict
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ControlNode(luna_node.LunaNode):
    ID = 2
    IS_EXEC = True
    TITLE_EDITABLE = True
    ICON = None
    DEFAULT_TITLE = 'Control'
    CATEGORY = 'Utils'
    UNIQUE = False

    def init_sockets(self, reset=True):
        super(ControlNode, self).init_sockets(reset=reset)

        self.in_name = self.add_input(editor_conf.DataType.STRING, label='Name', value='control')
        self.in_side = self.add_input(editor_conf.DataType.STRING, label='Side', value='c')
        self.in_guide = self.add_input(editor_conf.DataType.STRING, label='Guide')
        self.in_delete_guide = self.add_input(editor_conf.DataType.BOOLEAN, label='Delete Guide', value=False)
        self.in_parent = self.add_input(editor_conf.DataType.STRING, label='Parent')
        self.in_attribs = self.add_input(editor_conf.DataType.STRING, label='Attributes', value='tr')
        self.in_match_pos = self.add_input(editor_conf.DataType.BOOLEAN, label='Match Position', value=True)
        self.in_match_orient = self.add_input(editor_conf.DataType.BOOLEAN, label='Match Orient', value=True)
        self.in_match_pivot = self.add_input(editor_conf.DataType.BOOLEAN, label='Match Pivot', value=True)
        self.in_color_index = self.add_input(editor_conf.DataType.NUMERIC, label='Color', value=0)
        self.in_offset_grp = self.add_input(editor_conf.DataType.BOOLEAN, label='Offset Group', value=True)
        self.in_joint = self.add_input(editor_conf.DataType.BOOLEAN, label='Joint', value=True)
        self.in_shape = self.add_input(editor_conf.DataType.STRING, label='Shape', value='cube')
        self.in_tag = self.add_input(editor_conf.DataType.STRING, label='Tag', value='')
        self.in_component = self.add_input(editor_conf.DataType.ANIM_COMPONENT, label='Component', value=None)
        self.in_orient_axis = self.add_input(editor_conf.DataType.STRING, label='Orient Axis', value='x')
        self.in_scale = self.add_input(editor_conf.DataType.NUMERIC, label='Scale', value=1.0)

        self.out_control = self.add_output(editor_conf.DataType.CONTROL, label='Control')
        self.out_transform = self.add_output(editor_conf.DataType.STRING, label='Transform', value='')

        # Mark required
        self.mark_inputs_required([self.in_name,
                                   self.in_side,
                                   self.in_orient_axis])

    def execute(self):
        attribs = self.in_attribs.value()
        attribs = attribs.split(',') if 'x' in attribs or 'y' in attribs or 'z' in attribs else attribs
        parent = self.in_parent.value() if self.in_parent.value() else None

        self.control_instance = luna_rig.Control.create(name=self.in_name.value(),
                                                        side=self.in_side.value(),
                                                        guide=self.in_guide.value(),
                                                        parent=parent,
                                                        attributes=attribs,
                                                        delete_guide=self.in_delete_guide.value(),
                                                        match_pos=self.in_match_pos.value(),
                                                        match_orient=self.in_match_orient.value(),
                                                        match_pivot=self.in_match_pivot.value(),
                                                        color=self.in_color_index.value(),
                                                        offset_grp=self.in_offset_grp.value(),
                                                        joint=self.in_joint.value(),
                                                        shape=self.in_shape.value(),
                                                        tag=self.in_tag.value(),
                                                        component=self.in_component.value(),
                                                        orient_axis=self.in_orient_axis.value(),
                                                        scale=self.in_scale.value())

        self.out_control.set_value(self.control_instance)
        self.out_transform.set_value(self.control_instance.transform)


def register_plugin():
    editor_conf.register_node(ControlNode.ID, ControlNode)
    editor_conf.register_function(luna_rig.Control.connect_via_remap,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Source Plug', editor_conf.DataType.STRING),
                                      ('Destination Plug', editor_conf.DataType.STRING),
                                      ('Destination Plug', editor_conf.DataType.STRING),
                                      ('Remap Name', editor_conf.DataType.STRING),
                                      ('Input Min', editor_conf.DataType.NUMERIC),
                                      ('Input Max', editor_conf.DataType.NUMERIC),
                                      ('Output Min', editor_conf.DataType.NUMERIC),
                                      ('Output Max', editor_conf.DataType.NUMERIC)
                                  ]),
                                  default_values=[None, '', '', 'remap', 0.0, 10.0, 0.0, 1.0],
                                  nice_name='Connect Via Remap',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.add_space,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Space Control', editor_conf.DataType.CONTROL),
                                      ('Space Name', editor_conf.DataType.STRING),
                                      ('Use Offset Matrix', editor_conf.DataType.BOOLEAN)
                                  ]),
                                  default_values=[None, None, 'newSpace', False],
                                  nice_name='Add Space',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.add_world_space,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Use Offset Matrix', editor_conf.DataType.BOOLEAN)
                                  ]),
                                  default_values=[None, False],
                                  nice_name='Add World Space',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.add_orient_switch,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Orient Target', editor_conf.DataType.STRING),
                                      ('Local Parent', editor_conf.DataType.CONTROL),
                                      ('Default State', editor_conf.DataType.BOOLEAN),
                                  ]),
                                  default_values=[None, '', None, True],
                                  nice_name='Add Orient Switch',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.constrain_geometry,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Geometry', editor_conf.DataType.STRING),
                                      ('Scale', editor_conf.DataType.BOOLEAN),
                                      ('Inherits Transfom', editor_conf.DataType.BOOLEAN),
                                  ]),
                                  default_values=[None, '', True, True],
                                  nice_name='Constrain Geometry',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.get_parent,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Generations', editor_conf.DataType.NUMERIC)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Parent', editor_conf.DataType.CONTROL),
                                  ]),
                                  default_values=[None, 1],
                                  nice_name='Get Parent',
                                  category='Control')

    editor_conf.register_function(luna_rig.Control.set_parent,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('Parent Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Set Parent',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_tag,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Tag', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Tag',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_joint,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Joint', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Joint',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_transform,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Transform', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Transform',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_connected_component,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Anim Component', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  nice_name='Get Component',
                                  category='Control')
    editor_conf.register_function(luna_rig.Control.get_character,
                                  editor_conf.DataType.CONTROL,
                                  inputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER),
                                  ]),
                                  nice_name='Get Character',
                                  category='Control')
