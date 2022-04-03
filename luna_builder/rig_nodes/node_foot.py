from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class FootComponentNode(base_component.AnimComponentNode):
    ID = 10
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Foot'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.FootComponent

    def init_sockets(self, reset=True):
        super(FootComponentNode, self).init_sockets(reset=reset)

        # Override inputs
        self.in_name.set_value('foot')
        self.in_tag.set_value('body')
        # Override outputs
        self.in_meta_parent.data_type = 'FKIK_COMPONENT'
        self.out_self.data_type = editor_conf.DataType.FOOT_COMPONENT

        # Create new inputs
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_rv_chain = self.add_input(editor_conf.DataType.STRING, label='Reverse Chain', value=None)
        self.in_foot_loc_grp = self.add_input(editor_conf.DataType.STRING, label='Foot Locators', value=None)
        self.in_roll_axis = self.add_input(editor_conf.DataType.STRING, label='Rotate Axis', value='ry')

        # Mark required
        self.mark_inputs_required((self.in_meta_parent,
                                   self.in_start_joint,
                                   self.in_end_joint,
                                   self.in_rv_chain,
                                   self.in_foot_loc_grp,
                                   self.in_roll_axis))

    def execute(self):
        super(FootComponentNode, self).execute()
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              rv_chain=self.in_rv_chain.value(),
                                                              foot_locators_grp=self.in_foot_loc_grp.value(),
                                                              roll_axis=self.in_roll_axis.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    # ============= Data type ============ #
    editor_conf.DataType.register_datatype('FOOT_COMPONENT',
                                           FootComponentNode.COMPONENT_CLASS,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Foot',
                                           default_value=None)
    # ============= Node ============ #
    editor_conf.register_node(FootComponentNode.ID, FootComponentNode)
    # ============= Functions ============ #
    editor_conf.register_function(FootComponentNode.COMPONENT_CLASS.get_roll_axis,
                                  editor_conf.DataType.FOOT_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Foot', editor_conf.DataType.FOOT_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Roll Axis', editor_conf.DataType.STRING)
                                  ]),
                                  nice_name='Get Roll Axis',
                                  category='Foot Component')
    editor_conf.register_function(FootComponentNode.COMPONENT_CLASS.get_fk_control,
                                  editor_conf.DataType.FOOT_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Foot', editor_conf.DataType.FOOT_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Get FK Control',
                                  category='Foot Component')
