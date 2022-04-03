import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class FKDynamicsComponentNode(base_component.AnimComponentNode):
    ID = 29
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'FK Dynamics'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.FKDynamicsComponent

    def init_sockets(self, reset=True):
        super(FKDynamicsComponentNode, self).init_sockets(reset=reset)

        # Remove unused sockets
        self.remove_socket('Side')
        self.remove_socket('In Hook')
        self.remove_socket('Side', is_input=False)
        self.remove_socket('In Hook', is_input=False)

        # Override inputs
        self.in_meta_parent.data_type = 'FK_COMPONENT'
        self.in_name.set_value('fk_dynamics')

        # Override Outputs
        self.out_meta_parent.data_type = 'FK_COMPONENT'
        self.out_self.data_type = editor_conf.DataType.FK_DYNAMICS_COMPONENT

        # Create new inputs
        self.in_unique_solver = self.add_input(editor_conf.DataType.BOOLEAN, label='Unique Nucleus', value=False)

        # Mark required
        self.mark_input_as_required(self.in_meta_parent)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              character=self.in_character.value(),
                                                              name=self.in_name.value(),
                                                              tag=self.in_tag.value(),
                                                              unique_nsolver=self.in_unique_solver.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('FK_DYNAMICS_COMPONENT',
                                           luna_rig.components.FKDynamicsComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='FK Dynamics',
                                           default_value=False)
    editor_conf.register_node(FKDynamicsComponentNode.ID, FKDynamicsComponentNode)
