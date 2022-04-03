from collections import OrderedDict
from luna import Logger
import luna_rig
import luna_rig.components.spine_component as spine_component
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class SpineNode(base_component.AnimComponentNode):
    ID = None
    IS_EXEC = True
    ICON = 'body.png'
    DEFAULT_TITLE = 'Spine'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = spine_component.SpineComponent

    def init_sockets(self, reset=True):
        super(SpineNode, self).init_sockets(reset=reset)
        self.in_name.set_value('spine')
        self.in_tag.set_value('body')
        self.out_self.data_type = editor_conf.DataType.SPINE_COMPONENT


class FKIKSpineNode(SpineNode):
    ID = 8
    DEFAULT_TITLE = 'FKIK Spine'
    COMPONENT_CLASS = luna_rig.components.FKIKSpineComponent

    def init_sockets(self, reset=True):
        super(FKIKSpineNode, self).init_sockets(reset=reset)
        # Override types
        self.out_self.data_type = editor_conf.DataType.FKIK_SPINE_COMPONENT

        # Add inputs
        self.in_start_joint = self.add_input(editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(editor_conf.DataType.STRING, label='End Joint', value=None)
        self.mark_input_as_required(self.in_start_joint)

        self.out_hook_root = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Root', value=self.COMPONENT_CLASS.Hooks.ROOT.value)
        self.out_hook_hips = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Hips', value=self.COMPONENT_CLASS.Hooks.HIPS.value)
        self.out_hook_mid = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Mid', value=self.COMPONENT_CLASS.Hooks.MID.value)
        self.out_hook_chest = self.add_output(editor_conf.DataType.NUMERIC, label='Hook Chest', value=self.COMPONENT_CLASS.Hooks.CHEST.value)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              tag=self.in_tag.value())
        # Set outputs
        self.out_self.set_value(self.component_instance)


def register_plugin():
    # ============== Data types =================#
    editor_conf.DataType.register_datatype('SPINE_COMPONENT',
                                           spine_component.SpineComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Spine',
                                           default_value=None)
    editor_conf.DataType.register_datatype('FKIK_SPINE_COMPONENT',
                                           luna_rig.components.FKIKSpineComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='FKIK Spine',
                                           default_value=None)
    # ============== Nodes functions =================#
    editor_conf.register_node(FKIKSpineNode.ID, FKIKSpineNode)

    # ============== Base Spine functions =================#
    editor_conf.register_function(SpineNode.COMPONENT_CLASS.get_root_control,
                                  editor_conf.DataType.SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Spine', editor_conf.DataType.SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Root Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Root Control',
                                  category='Spine')
    editor_conf.register_function(SpineNode.COMPONENT_CLASS.get_hips_control,
                                  editor_conf.DataType.SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Spine', editor_conf.DataType.SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hips Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Hips Control',
                                  category='Spine')
    editor_conf.register_function(SpineNode.COMPONENT_CLASS.get_chest_control,
                                  editor_conf.DataType.SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Spine', editor_conf.DataType.SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Chest Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Chest Control',
                                  category='Spine')

    # ============== FKIK Spine functions =================#
    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_fk1_control,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('FK1 Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='FK1 Control',
                                  category='FKIK Spine')

    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_fk2_control,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('FK2 Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='FK2 Control',
                                  category='FKIK Spine')

    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_mid_control,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Mid Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Mid Control',
                                  category='FKIK Spine')

    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_pivot_control,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Pivot Control', editor_conf.DataType.CONTROL)
                                  ]),
                                  nice_name='Pivot Control',
                                  category='FKIK Spine')
    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_ik_curve,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Pivot Control', editor_conf.DataType.STRING)
                                  ]),
                                  nice_name='IK Curve',
                                  category='FKIK Spine')
    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_root_hook_index,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Root', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Root Hook',
                                  category='FKIK Spine')
    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_hips_hook_index,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Hips', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Hips Hook',
                                  category='FKIK Spine')
    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_mid_hook_index,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Mid', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Mid Hook',
                                  category='FKIK Spine')
    editor_conf.register_function(FKIKSpineNode.COMPONENT_CLASS.get_chest_hook_index,
                                  editor_conf.DataType.FKIK_SPINE_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('FKIK Spine', editor_conf.DataType.FKIK_SPINE_COMPONENT)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Hook Chest', editor_conf.DataType.NUMERIC)
                                  ]),
                                  nice_name='Get Chest Hook',
                                  category='FKIK Spine')
