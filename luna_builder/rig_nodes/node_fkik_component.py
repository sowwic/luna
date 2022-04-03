from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class FKIKComponentNode(base_component.AnimComponentNode):
    ID = 9
    IS_EXEC = True
    ICON = 'ikfk.png'
    DEFAULT_TITLE = 'FKIK'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.FKIKComponent

    def init_sockets(self, reset=True):
        super(FKIKComponentNode, self).init_sockets(reset=reset)
        self.out_self.data_type = editor_conf.DataType.FKIK_COMPONENT

        self.in_name.set_value('fkik_component')
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_ik_world_orient = self.add_input(editor_conf.DataType.BOOLEAN, label='IK World Orient', value=False)
        self.in_default_state = self.add_input(editor_conf.DataType.BOOLEAN, label='Default to IK', value=True)
        self.in_param_locator = self.add_input(editor_conf.DataType.STRING, 'Param Locator')

        self.out_hook_start_jnt = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Start', value=self.COMPONENT_CLASS.Hooks.START_JNT.value)
        self.out_hook_end_jnt = self.add_output(editor_conf.DataType.NUMERIC, label='Hook End', value=self.COMPONENT_CLASS.Hooks.END_JNT.value)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              ik_world_orient=self.in_ik_world_orient.value(),
                                                              default_state=self.in_default_state.value(),
                                                              param_locator=self.in_param_locator.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    # ============= Data type ============ #
    editor_conf.DataType.register_datatype('FKIK_COMPONENT',
                                           luna_rig.components.FKIKComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='FKIK Component',
                                           default_value=None)

    # ============= Node ============ #
    editor_conf.register_node(FKIKComponentNode.ID, FKIKComponentNode)

    # ============= Functions ============ #
    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_ik_control,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get IK Control',
                                  category='FKIK Component')

    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_pv_control,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get PV Control',
                                  category='FKIK Component')

    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_param_control,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get Param Control',
                                  category='FKIK Component')

    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_fk_controls,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Controls', editor_conf.DataType.LIST)
                                  ]),
                                  nice_name='Get FK Controls',
                                  category='FKIK Component')

    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_handle,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('IK Handle', editor_conf.DataType.STRING)
                                  ]),
                                  nice_name='Get IK Handle',
                                  category='FKIK Component')
    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.hide_last_fk,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT)
                                  ]),
                                  nice_name='Hide last FK',
                                  category='FKIK Component')
    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_fk_control_at,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT),
                                      ('Index', editor_conf.DataType.NUMERIC)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('FK Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get FK Control At',
                                  category='FKIK Component')
    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_start_hook_index,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Start', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Start Hook',
                                  category='FKIK Component')
    editor_conf.register_function(FKIKComponentNode.COMPONENT_CLASS.get_end_hook_index,
                                  editor_conf.DataType.FKIK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Component', editor_conf.DataType.FKIK_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook End', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get End Hook',
                                  category='FKIK Component')
