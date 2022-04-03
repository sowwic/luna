import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class RibbonComponentNode(base_component.AnimComponentNode):
    ID = 28
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Ribbon'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.RibbonComponent

    def init_sockets(self, reset=True):
        super(RibbonComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('ribbon')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.RIBBON_COMPONENT

        # Create new inputs
        self.in_surface = self.add_input(editor_conf.DataType.STRING, label='Surface')
        self.in_num_controls = self.add_input(editor_conf.DataType.NUMERIC, label='Num Controls', value=3)
        self.in_skel_joint_parent = self.add_input(editor_conf.DataType.STRING, label='Parent Skeleton Joint')
        self.in_span = self.add_input(editor_conf.DataType.STRING, label='Span', value='u')
        self.in_num_rivets_override = self.add_input(editor_conf.DataType.NUMERIC, label='Override rivets number', value=0)
        self.in_fk_hierachy = self.add_input(editor_conf.DataType.BOOLEAN, label='FK Hierachy', value=False)
        self.in_single_joint_hierarchy = self.add_input(editor_conf.DataType.BOOLEAN, label="Single joint heirarchy", value=False)
        self.in_flip_rivets_normal = self.add_input(editor_conf.DataType.BOOLEAN, label='Flip Rivets Normal', value=False)

        # Mark required
        self.mark_inputs_required((self.in_surface,
                                   self.in_span))

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(character=self.in_character.value(),
                                                              meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              tag=self.in_tag.value(),
                                                              surface=self.in_surface.value(),
                                                              num_controls=self.in_num_controls.value(),
                                                              skel_joint_parent=self.in_skel_joint_parent.value(),
                                                              use_span=self.in_span.value(),
                                                              fk_hierarchy=self.in_fk_hierachy.value(),
                                                              single_joint_hierarchy=self.in_single_joint_hierarchy.value(),
                                                              override_num_rivets=self.in_num_rivets_override.value(),
                                                              flip_rivets_normal=self.in_flip_rivets_normal.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('RIBBON_COMPONENT',
                                           luna_rig.components.RibbonComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Ribbon',
                                           default_value=None)
    editor_conf.register_node(RibbonComponentNode.ID, RibbonComponentNode)

    editor_conf.register_function(RibbonComponentNode.COMPONENT_CLASS.get_surface,
                                  editor_conf.DataType.RIBBON_COMPONENT,
                                  inputs_dict={'Ribbon': editor_conf.DataType.RIBBON_COMPONENT},
                                  outputs_dict={'Surface': editor_conf.DataType.STRING},
                                  nice_name='Get Surface',
                                  category='Ribbon Component')

    editor_conf.register_function(RibbonComponentNode.COMPONENT_CLASS.get_shape_controls,
                                  editor_conf.DataType.RIBBON_COMPONENT,
                                  inputs_dict={'Ribbon': editor_conf.DataType.RIBBON_COMPONENT},
                                  outputs_dict={'Controls List': editor_conf.DataType.LIST},
                                  nice_name='Get Shape Controls',
                                  category='Ribbon Component')

    editor_conf.register_function(RibbonComponentNode.COMPONENT_CLASS.get_main_control,
                                  editor_conf.DataType.RIBBON_COMPONENT,
                                  inputs_dict={'Ribbon': editor_conf.DataType.RIBBON_COMPONENT},
                                  outputs_dict={'Control': editor_conf.DataType.CONTROL},
                                  nice_name='Get Main Control',
                                  category='Ribbon Component')

    editor_conf.register_function(RibbonComponentNode.COMPONENT_CLASS.get_is_fk,
                                  editor_conf.DataType.RIBBON_COMPONENT,
                                  inputs_dict={'Ribbon': editor_conf.DataType.RIBBON_COMPONENT},
                                  outputs_dict={'State': editor_conf.DataType.BOOLEAN},
                                  nice_name='Get Is FK',
                                  category='Ribbon Component')
