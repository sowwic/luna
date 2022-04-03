import luna_rig
from luna import Logger
from collections import OrderedDict
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class CharacterNode(base_component.ComponentNode):
    ID = 7
    IS_EXEC = True
    ICON = 'bindpose.png'
    DEFAULT_TITLE = 'Character'
    CATEGORY = 'Components'
    UNIQUE = True
    COMPONENT_CLASS = luna_rig.components.Character

    def init_sockets(self, reset=True):
        super(CharacterNode, self).init_sockets(reset=reset)
        self.out_self.data_type = editor_conf.DataType.CHARACTER
        self.in_name.set_value('character')
        self.in_tag.set_value('character')

        self.out_root_control = self.add_output(editor_conf.DataType.CONTROL, label='Root Control')
        self.out_deform_rig = self.add_output(editor_conf.DataType.STRING, label='Deformation Rig')
        self.out_control_rig = self.add_output(editor_conf.DataType.STRING, label='Control Rig')
        self.out_geometry_grp = self.add_output(editor_conf.DataType.STRING, label='Geometry Group')

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(self.in_meta_parent.value(), name=self.in_name.value(), tag=self.in_tag.value())
        # Set outputs
        self.out_self.set_value(self.component_instance)
        self.out_meta_parent.set_value(self.component_instance.meta_parent)
        self.out_root_control.set_value(self.component_instance.root_control.transform)
        self.out_deform_rig.set_value(self.component_instance.deformation_rig)
        self.out_control_rig.set_value(self.component_instance.control_rig)
        self.out_geometry_grp.set_value(self.component_instance.geometry_grp)


def register_plugin():
    base_component.register_plugin()
    editor_conf.register_node(CharacterNode.ID, CharacterNode)
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.get_control_rig,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  outputs_dict={'Control Rig': editor_conf.DataType.STRING},
                                  nice_name='Get Control Rig',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.get_deformation_rig,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  outputs_dict={'Deformation Rig': editor_conf.DataType.STRING},
                                  nice_name='Get Deformation Rig',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.get_geometry_grp,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  outputs_dict={'Geometry Group': editor_conf.DataType.STRING},
                                  nice_name='Get Geometry Group',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.get_root_control,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  outputs_dict={'Root Control': editor_conf.DataType.CONTROL},
                                  nice_name='Get Root Control',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.get_world_locator,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  outputs_dict={'World Locator': editor_conf.DataType.STRING},
                                  nice_name='Get World Locator',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.get_root_motion,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  outputs_dict={'Root Joint': editor_conf.DataType.STRING},
                                  nice_name='Get Root Joint',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.add_root_motion,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER),
                                      ('Follow Control', editor_conf.DataType.CONTROL),
                                      ('Root Joint', editor_conf.DataType.STRING)
                                  ]),
                                  outputs_dict={'Root Joint': editor_conf.DataType.STRING},
                                  nice_name='Add Root Motion',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.attach_to_skeleton,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER)]),
                                  nice_name='Attach To Skeleton',
                                  category='Character')
    editor_conf.register_function(CharacterNode.COMPONENT_CLASS.set_publish_mode,
                                  editor_conf.DataType.CHARACTER,
                                  inputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER),
                                      ('Publish Ready', editor_conf.DataType.BOOLEAN)]),
                                  nice_name='Set Publish Mode',
                                  category='Character')
