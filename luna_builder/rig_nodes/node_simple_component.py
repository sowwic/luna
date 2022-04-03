from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class SimpleComponentNode(base_component.AnimComponentNode):
    ID = 15
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Simple'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.SimpleComponent

    def init_sockets(self, reset=True):
        super(SimpleComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('simple')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.SIMPLE_COMPONENT

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('SIMPLE_COMPONENT', luna_rig.components.SimpleComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Simple Component',
                                           default_value=None)
    editor_conf.register_node(SimpleComponentNode.ID, SimpleComponentNode)
    editor_conf.register_function(SimpleComponentNode.COMPONENT_CLASS.add_existing_control,
                                  editor_conf.DataType.SIMPLE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Simple Component', editor_conf.DataType.SIMPLE_COMPONENT),
                                      ('Control', editor_conf.DataType.CONTROL),
                                      ('As Hook', editor_conf.DataType.BOOLEAN),
                                      ('Bind Joint', editor_conf.DataType.STRING)
                                  ]),
                                  nice_name='Add Control',
                                  category='Simple Component'
                                  )
