from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class SDKCorrectiveComponentNode(base_component.AnimComponentNode):
    ID = 30
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'SDK Corrective'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.CorrectiveComponent

    def init_sockets(self, reset=True):
        super(SDKCorrectiveComponentNode, self).init_sockets(reset=reset)
        self.remove_socket('In Hook')
        self.remove_socket('In Hook', is_input=False)

        # Override inputs
        self.in_name.set_value('sdk_corrective')
        self.in_tag.set_value('corrective')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.SDK_CORRECTIVE_COMPONENT

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              character=self.in_character.value(),
                                                              name=self.in_name.value(),
                                                              side=self.in_side.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('SDK_CORRECTIVE_COMPONENT',
                                           luna_rig.components.CorrectiveComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='SDK Corrective',
                                           default_value=False)
    editor_conf.register_node(SDKCorrectiveComponentNode.ID, SDKCorrectiveComponentNode)
    editor_conf.register_function(SDKCorrectiveComponentNode.COMPONENT_CLASS.add_control,
                                  editor_conf.DataType.SDK_CORRECTIVE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('SDK Corrective', editor_conf.DataType.SDK_CORRECTIVE_COMPONENT),
                                      ('Constraint Parent Joint', editor_conf.DataType.STRING),
                                      ('Output Joint', editor_conf.DataType.STRING),
                                      ('Name', editor_conf.DataType.STRING)]),
                                  outputs_dict={'Corrective Control': editor_conf.DataType.CONTROL},
                                  default_values=[None, '', '', 'helper'],
                                  nice_name='Add Corrective Control',
                                  category='SDK Corrective Component')
