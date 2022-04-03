from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class FKComponentNode(base_component.AnimComponentNode):
    ID = 16
    IS_EXEC = True
    ICON = 'ikfk.png'
    DEFAULT_TITLE = 'FK'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.FKComponent

    def init_sockets(self, reset=True):
        super(FKComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('fk_component')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.FK_COMPONENT

        # Create new inputs
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_lock_translate = self.add_input(editor_conf.DataType.BOOLEAN, label='Lock Translation', value=True)
        self.in_add_end_ctl = self.add_input(editor_conf.DataType.BOOLEAN, label='End Control', value=True)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              add_end_ctl=self.in_add_end_ctl.value(),
                                                              lock_translate=self.in_lock_translate.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


class HeadComponentNode(FKComponentNode):
    ID = 17
    IS_EXEC = True
    ICON = 'skull.png'
    DEFAULT_TITLE = 'Head'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.HeadComponent

    def init_sockets(self, reset=True):
        super(HeadComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('head')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.HEAD_COMPONENT

        # Create new inputs
        self.remove_socket('End Control', is_input=True)
        self.in_head_joint_index = self.add_input(editor_conf.DataType.NUMERIC, label='Head Index', value=-2)
        # Create new outputs
        self.out_head_hook = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Head', value=self.COMPONENT_CLASS.Hooks.HEAD)
        self.out_base_hook = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Base', value=self.COMPONENT_CLASS.Hooks.NECK_BASE)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              head_joint_index=self.in_head_joint_index.value(),
                                                              lock_translate=self.in_lock_translate.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    # ============= Data type ============ #
    editor_conf.DataType.register_datatype('FK_COMPONENT',
                                           luna_rig.components.FKComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='FK Component',
                                           default_value=None)
    editor_conf.DataType.register_datatype('HEAD_COMPONENT',
                                           luna_rig.components.HeadComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Head',
                                           default_value=None)

    # ============= Node ============ #
    editor_conf.register_node(FKComponentNode.ID, FKComponentNode)
    editor_conf.register_node(HeadComponentNode.ID, HeadComponentNode)

    # ============= Functions ============ #
    editor_conf.register_function(FKComponentNode.COMPONENT_CLASS.add_auto_aim,
                                  editor_conf.DataType.FK_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FK Component', editor_conf.DataType.FK_COMPONENT),
                                      ('Follow Control', editor_conf.DataType.CONTROL),
                                      ('Is Mirrored', editor_conf.DataType.BOOLEAN),
                                      ('Default Blend', editor_conf.DataType.NUMERIC)
                                  ]),
                                  default_values=[None, None, False, 5.0],
                                  nice_name='Add Auto Aim',
                                  category='FK Component')

    editor_conf.register_function(HeadComponentNode.COMPONENT_CLASS.add_orient_attr,
                                  editor_conf.DataType.HEAD_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Head', editor_conf.DataType.HEAD_COMPONENT)
                                  ]),
                                  nice_name='Add Orient Attr',
                                  category='Head Component')
    editor_conf.register_function(HeadComponentNode.COMPONENT_CLASS.get_head_hook_index,
                                  editor_conf.DataType.HEAD_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Head', editor_conf.DataType.HEAD_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Head', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Head Hook',
                                  category='Head Component')
    editor_conf.register_function(HeadComponentNode.COMPONENT_CLASS.get_neck_base_hook_index,
                                  editor_conf.DataType.HEAD_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Head', editor_conf.DataType.HEAD_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Neck', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Neck Hook',
                                  category='Head Component')
