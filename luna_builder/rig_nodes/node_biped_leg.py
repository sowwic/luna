from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class BipedLegComponentNode(base_component.AnimComponentNode):
    ID = 31
    IS_EXEC = True
    TITLE_EDITABLE = True
    ICON = 'leg1.png'
    DEFAULT_TITLE = 'Biped Leg'
    CATEGORY = 'Components'
    UNIQUE = False
    COMPONENT_CLASS = luna_rig.components.BipedLegComponent

    def init_sockets(self, reset=True):
        super(BipedLegComponentNode, self).init_sockets(reset=reset)
        self.out_self.data_type = editor_conf.DataType.BIPED_LEG_COMPONENT

        self.in_name.set_value('leg')
        self.in_tag.set_value("body")

        self.in_start_joint = self.add_input(
            editor_conf.DataType.STRING, label='Start Joint', value=None)
        self.in_end_joint = self.add_input(
            editor_conf.DataType.STRING, label='End Joint', value=None)
        self.in_ik_world_orient = self.add_input(
            editor_conf.DataType.BOOLEAN, label='IK World Orient', value=True)
        self.in_default_state = self.add_input(
            editor_conf.DataType.BOOLEAN, label='Default to IK', value=True)

        self.out_hook_start_jnt = self.add_output(
            editor_conf.DataType.NUMERIC, label='Hook Start', value=self.COMPONENT_CLASS.Hooks.START_JNT.value)
        self.out_hook_end_jnt = self.add_output(
            editor_conf.DataType.NUMERIC, label='Hook End', value=self.COMPONENT_CLASS.Hooks.END_JNT.value)

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(meta_parent=self.in_meta_parent.value(),
                                                              hook=self.in_hook.value(),
                                                              character=self.in_character.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              start_joint=self.in_start_joint.value(),
                                                              end_joint=self.in_end_joint.value(),
                                                              ik_world_orient=self.in_ik_world_orient.value(),
                                                              default_state=self.in_default_state.value(),
                                                              param_locator=None,
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    # ============= Data type ============ #
    editor_conf.DataType.register_datatype('BIPED_LEG_COMPONENT',
                                           luna_rig.components.BipedLegComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Biped Leg',
                                           default_value=None)

    # ============= Node ============ #
    editor_conf.register_node(BipedLegComponentNode.ID, BipedLegComponentNode)

    # ============= Functions ============ #
    editor_conf.register_function(BipedLegComponentNode.COMPONENT_CLASS.build_foot,
                                  editor_conf.DataType.BIPED_LEG_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ("Biped Leg", editor_conf.DataType.BIPED_LEG_COMPONENT),
                                      ('Reverse Chain', editor_conf.DataType.STRING),
                                      ('Foot Locators Group',
                                       editor_conf.DataType.STRING),
                                      ("Foot roll axis", editor_conf.DataType.STRING)
                                  ]),
                                  outputs_dict=OrderedDict(
                                      [
                                          ("Foot Component", "FOOT_COMPONENT")
                                      ]),
                                  default_values=["", "", "ry"],
                                  nice_name="Build Foot",
                                  category="Biped Leg")
    editor_conf.register_function(BipedLegComponentNode.COMPONENT_CLASS.get_foot,
                                  editor_conf.DataType.BIPED_LEG_COMPONENT,
                                  inputs_dict={
                                      "Biped Leg": editor_conf.DataType.BIPED_LEG_COMPONENT},
                                  outputs_dict=OrderedDict(
                                      [
                                          ("Foot Component", "FOOT_COMPONENT")
                                      ]),
                                  nice_name="Get Foot",
                                  category="Biped Leg")
    editor_conf.register_function(BipedLegComponentNode.COMPONENT_CLASS.create_twist,
                                  editor_conf.DataType.BIPED_LEG_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ("Biped Leg", editor_conf.DataType.BIPED_LEG_COMPONENT),
                                      ('Hip Joints Count',
                                       editor_conf.DataType.NUMERIC),
                                      ("Shin Joints Count",
                                       editor_conf.DataType.NUMERIC),
                                      ('Mirrored chain', editor_conf.DataType.BOOLEAN),
                                      ("Add Hooks", editor_conf.DataType.BOOLEAN)
                                  ]),
                                  outputs_dict=OrderedDict(
                                      [
                                          ("Upper Twist", "TWIST_COMPONENT"),
                                          ("Lower Twist", "TWIST_COMPONENT")
                                      ]),
                                  default_values=[2, 2, False, False],
                                  nice_name="Create Twist",
                                  category="Biped Leg")
