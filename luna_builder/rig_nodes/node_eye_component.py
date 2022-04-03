import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class EyeComponentNode(base_component.AnimComponentNode):
    ID = 27
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Eye'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.EyeComponent

    def init_sockets(self, reset=True):
        super(EyeComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('eye')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.EYE_COMPONENT

        # Create new inputs
        self.in_aim_locator = self.add_input(editor_conf.DataType.STRING, label='Aim Locator')
        self.in_eye_joint = self.add_input(editor_conf.DataType.STRING, label='Eye Joint')
        self.in_aim_vector = self.add_input(editor_conf.DataType.STRING, label='Aim Vector', value='z')
        self.in_up_vector = self.add_input(editor_conf.DataType.STRING, label='Up Vector', value='y')
        self.in_target_wire = self.add_input(editor_conf.DataType.BOOLEAN, label='Target Lines', value=False)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(self.in_aim_locator.value(),
                                                              self.in_eye_joint.value(),
                                                              meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              tag=self.in_tag.value(),
                                                              aim_vector=self.in_aim_vector.value(),
                                                              up_vector=self.in_up_vector.value(),
                                                              target_wire=self.in_target_wire.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('EYE_COMPONENT',
                                           luna_rig.components.EyeComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Eye',
                                           default_value=None)
    editor_conf.register_node(EyeComponentNode.ID, EyeComponentNode)

    editor_conf.register_function(EyeComponentNode.COMPONENT_CLASS.get_aim_control,
                                  editor_conf.DataType.EYE_COMPONENT,
                                  inputs_dict={'Eye': editor_conf.DataType.EYE_COMPONENT},
                                  outputs_dict={'Control': editor_conf.DataType.CONTROL},
                                  nice_name='Get Aim Control',
                                  category='Eye Component')

    editor_conf.register_function(EyeComponentNode.COMPONENT_CLASS.get_fk_control,
                                  editor_conf.DataType.EYE_COMPONENT,
                                  inputs_dict={'Eye': editor_conf.DataType.EYE_COMPONENT},
                                  outputs_dict={'Control': editor_conf.DataType.CONTROL},
                                  nice_name='Get FK Control',
                                  category='Eye Component')
