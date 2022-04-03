from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class TwistComponentNode(base_component.AnimComponentNode):
    ID = 18
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Twist'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.TwistComponent

    def init_sockets(self, reset=True):
        super(TwistComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('twist')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.TWIST_COMPONENT

        # Delete sockets
        self.remove_socket('In Hook', is_input=True)
        self.remove_socket('In Hook', is_input=False)

        # # Create new inputs
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_start_object = self.add_input(editor_conf.DataType.STRING, label='Start Object', value=None)
        self.in_end_object = self.add_input(editor_conf.DataType.STRING, label='End Object', value=None)
        self.in_num_joints = self.add_input(editor_conf.DataType.NUMERIC, label='Num Joints', value=2)
        self.in_is_mirrored = self.add_input(editor_conf.DataType.BOOLEAN, label='Is Mirrored', value=False)

        # Mark required
        self.mark_input_as_required(self.in_start_joint)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(self.in_meta_parent.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              start_object=self.in_start_object.value(),
                                                              end_object=self.in_end_object.value(),
                                                              mirrored_chain=self.in_is_mirrored.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('TWIST_COMPONENT', luna_rig.components.TwistComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Twist Component',
                                           default_value=None)
    editor_conf.register_node(TwistComponentNode.ID, TwistComponentNode)
    editor_conf.register_function(TwistComponentNode.COMPONENT_CLASS.get_start_hook_index,
                                  editor_conf.DataType.TWIST_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Twist Component', editor_conf.DataType.TWIST_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Start', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Start Hook',
                                  category='Twist Component')
    editor_conf.register_function(TwistComponentNode.COMPONENT_CLASS.get_end_hook_index,
                                  editor_conf.DataType.TWIST_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Twist Component', editor_conf.DataType.TWIST_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook End', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get End Hook',
                                  category='Twist Component')
