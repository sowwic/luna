from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class WireComponentNode(base_component.AnimComponentNode):
    ID = 20
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Wire'
    CATEGORY = 'Components'
    COMPONENT_CLASS = luna_rig.components.WireComponent

    def init_sockets(self, reset=True):
        super(WireComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('wire')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.WIRE_COMPONENT

        # Create new inputs
        self.in_curve = self.add_input(editor_conf.DataType.STRING, label='Curve')
        self.in_geometry = self.add_input(editor_conf.DataType.STRING, label='Geometry')
        self.in_dropoff_distance = self.add_input(editor_conf.DataType.NUMERIC, label='Dropoff', value=100.0)
        self.in_num_controls = self.add_input(editor_conf.DataType.NUMERIC, label='Number Controls', value=4)
        self.in_control_lines = self.add_input(editor_conf.DataType.BOOLEAN, label='Control Lines', value=True)

        # Mark required
        self.mark_inputs_required((self.in_curve, self.in_geometry))

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(character=self.in_character.value(),
                                                              meta_parent=self.in_meta_parent.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              hook=self.in_hook.value(),
                                                              tag=self.in_tag.value(),
                                                              curve=self.in_curve.value(),
                                                              geometry=self.in_geometry.value(),
                                                              dropoff_distance=self.in_dropoff_distance.value(),
                                                              num_controls=self.in_num_controls.value(),
                                                              control_lines=self.in_control_lines.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('WIRE_COMPONENT', luna_rig.components.WireComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Wire Component',
                                           default_value=None)
    editor_conf.register_node(WireComponentNode.ID, WireComponentNode)

    editor_conf.register_function(WireComponentNode.COMPONENT_CLASS.get_wire_curve,
                                  editor_conf.DataType.WIRE_COMPONENT,
                                  inputs_dict={'Wire': editor_conf.DataType.WIRE_COMPONENT},
                                  outputs_dict={'Curve': editor_conf.DataType.STRING},
                                  nice_name='Get Wire Curve',
                                  category='Wire Component')

    editor_conf.register_function(WireComponentNode.COMPONENT_CLASS.get_geometry,
                                  editor_conf.DataType.WIRE_COMPONENT,
                                  inputs_dict={'Wire': editor_conf.DataType.WIRE_COMPONENT},
                                  outputs_dict={'Geometry': editor_conf.DataType.STRING},
                                  nice_name='Get Wire Geometry',
                                  category='Wire Component')

    editor_conf.register_function(WireComponentNode.COMPONENT_CLASS.get_wire_deformer,
                                  editor_conf.DataType.WIRE_COMPONENT,
                                  inputs_dict={'Wire': editor_conf.DataType.WIRE_COMPONENT},
                                  outputs_dict={'Deformer': editor_conf.DataType.STRING},
                                  nice_name='Get Wire Deformer',
                                  category='Wire Component')

    editor_conf.register_function(WireComponentNode.COMPONENT_CLASS.get_root_control,
                                  editor_conf.DataType.WIRE_COMPONENT,
                                  inputs_dict={'Wire': editor_conf.DataType.WIRE_COMPONENT},
                                  outputs_dict={'Control': editor_conf.DataType.CONTROL},
                                  nice_name='Get Root Control',
                                  category='Wire Component')

    editor_conf.register_function(WireComponentNode.COMPONENT_CLASS.get_shape_controls,
                                  editor_conf.DataType.WIRE_COMPONENT,
                                  inputs_dict={'Wire': editor_conf.DataType.WIRE_COMPONENT},
                                  outputs_dict={'Curve': editor_conf.DataType.LIST},
                                  nice_name='Get Shape Controls',
                                  category='Wire Component')
