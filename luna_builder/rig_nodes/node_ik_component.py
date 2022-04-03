from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class IKComponentNode(base_component.AnimComponentNode):
    ID = 25
    IS_EXEC = True
    ICON = 'ikfk.png'
    DEFAULT_TITLE = 'IK'
    CATEGORY = 'Components'
    COMPONENT_CLASS = luna_rig.components.IKComponent

    def init_sockets(self, reset=True):
        super(IKComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('ik_component')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.IK_COMPONENT

        # Create new inputs
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint')
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint')
        self.in_world_orient = self.add_input(editor_conf.DataType.BOOLEAN, label='World Orient', value=False)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(character=self.in_character.value(),
                                                              meta_parent=self.in_meta_parent.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              hook=self.in_hook.value(),
                                                              tag=self.in_tag.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              control_world_orient=self.in_world_orient.value())
        self.out_self.set_value(self.component_instance)


class IKSplineComponentNode(base_component.AnimComponentNode):
    ID = 26
    IS_EXEC = True
    ICON = 'ikfk.png'
    DEFAULT_TITLE = 'IK Spline'
    CATEGORY = 'Components'
    COMPONENT_CLASS = luna_rig.components.IKSplineComponent

    def init_sockets(self, reset=True):
        super(IKSplineComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('ik_spline')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.IK_SPLINE_COMPONENT

        # Create new inputs
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint')
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint')
        self.in_curve = self.add_input(editor_conf.DataType.STRING, label='Curve')
        self.in_num_controls = self.add_input(editor_conf.DataType.NUMERIC, label='Num Controls', value=0)
        self.in_control_lines = self.add_input(editor_conf.DataType.BOOLEAN, label="Control lines", value=True)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(character=self.in_character.value(),
                                                              meta_parent=self.in_meta_parent.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              hook=self.in_hook.value(),
                                                              tag=self.in_tag.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              ik_curve=self.in_curve.value(),
                                                              num_controls=self.in_num_controls.value(),
                                                              control_lines=self.in_control_lines.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    # Datatypes
    editor_conf.DataType.register_datatype('IK_COMPONENT', luna_rig.components.IKComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='IK Component',
                                           default_value=None)
    editor_conf.DataType.register_datatype('IK_SPLINE_COMPONENT', luna_rig.components.IKSplineComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='IK Spline',
                                           default_value=None)

    # Nodes
    editor_conf.register_node(IKComponentNode.ID, IKComponentNode)
    editor_conf.register_node(IKSplineComponentNode.ID, IKSplineComponentNode)

    # Functions
    # IK Component
    editor_conf.register_function(IKComponentNode.COMPONENT_CLASS.get_ik_control,
                                  editor_conf.DataType.IK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Component', editor_conf.DataType.IK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get IK Control',
                                  category='IK Component')

    editor_conf.register_function(IKComponentNode.COMPONENT_CLASS.get_pv_control,
                                  editor_conf.DataType.IK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Component', editor_conf.DataType.IK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get PV Control',
                                  category='IK Component')

    editor_conf.register_function(IKComponentNode.COMPONENT_CLASS.get_handle,
                                  editor_conf.DataType.IK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Component', editor_conf.DataType.IK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('IK Handle', editor_conf.DataType.STRING)
                                  ]),
                                  nice_name='Get IK Handle',
                                  category='IK Component')

    editor_conf.register_function(IKComponentNode.COMPONENT_CLASS.get_start_hook_index,
                                  editor_conf.DataType.IK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Component', editor_conf.DataType.IK_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Start', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Start Hook',
                                  category='IK Component')
    editor_conf.register_function(IKComponentNode.COMPONENT_CLASS.get_end_hook_index,
                                  editor_conf.DataType.IK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Component', editor_conf.DataType.IK_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook End', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get End Hook',
                                  category='IK Component')

    editor_conf.register_function(IKComponentNode.COMPONENT_CLASS.get_end_hook_index,
                                  editor_conf.DataType.IK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Component', editor_conf.DataType.IK_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook End', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get End Hook',
                                  category='IK Component')

    # IK Spline Component
    editor_conf.register_function(IKSplineComponentNode.COMPONENT_CLASS.get_ik_curve,
                                  editor_conf.DataType.IK_SPLINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Spline', editor_conf.DataType.IK_SPLINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Curve', editor_conf.DataType.STRING)
                                  ]),
                                  nice_name='Get IK Curve',
                                  category='IK Spline Component')

    editor_conf.register_function(IKSplineComponentNode.COMPONENT_CLASS.get_root_control,
                                  editor_conf.DataType.IK_SPLINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Spline', editor_conf.DataType.IK_SPLINE_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get Root Control',
                                  category='IK Spline Component')

    editor_conf.register_function(IKSplineComponentNode.COMPONENT_CLASS.get_shape_controls,
                                  editor_conf.DataType.IK_SPLINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('IK Spline', editor_conf.DataType.IK_SPLINE_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Controls List', editor_conf.DataType.LIST)
                                  ]),
                                  nice_name='Get Shape Controls',
                                  category='IK Spline Component')
