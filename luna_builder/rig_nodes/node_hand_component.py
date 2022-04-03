from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class HandComponentNode(base_component.AnimComponentNode):
    ID = 19
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Hand'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.HandComponent

    def init_sockets(self, reset=True):
        super(HandComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('hand')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.HAND_COMPONENT

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              hook=self.in_hook.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('HAND_COMPONENT', luna_rig.components.HandComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Hand',
                                           default_value=None)
    editor_conf.register_node(HandComponentNode.ID, HandComponentNode)
    # Functions
    editor_conf.register_function(HandComponentNode.COMPONENT_CLASS.add_fk_finger,
                                  editor_conf.DataType.HAND_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Hand', editor_conf.DataType.HAND_COMPONENT),
                                      ('Start Joint', editor_conf.DataType.STRING),
                                      ('End Joint', editor_conf.DataType.STRING),
                                      ('Name', editor_conf.DataType.STRING),
                                      ('Tip Control', editor_conf.DataType.BOOLEAN)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('FK Component', 'FK_COMPONENT')
                                  ]),
                                  default_values=[None, '', '', 'finger', False],
                                  nice_name='Add FK Finger',
                                  category='Hand Component'
                                  )
    editor_conf.register_function(HandComponentNode.COMPONENT_CLASS.five_finger_setup,
                                  editor_conf.DataType.HAND_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Hand', editor_conf.DataType.HAND_COMPONENT),
                                      ('Thumb Joint', editor_conf.DataType.STRING),
                                      ('Index Joint', editor_conf.DataType.STRING),
                                      ('Middle Joint', editor_conf.DataType.STRING),
                                      ('Ring Joint', editor_conf.DataType.STRING),
                                      ('Pinky Joint', editor_conf.DataType.STRING),
                                      ('Tip Control', editor_conf.DataType.BOOLEAN)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Thumb', 'FK_COMPONENT'),
                                      ('Index', 'FK_COMPONENT'),
                                      ('Middle', 'FK_COMPONENT'),
                                      ('Ring', 'FK_COMPONENT'),
                                      ('Pinky', 'FK_COMPONENT')
                                  ]),
                                  nice_name='Five Finger Setup',
                                  category='Hand Component'
                                  )
