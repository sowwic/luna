from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ComponentNode(luna_node.LunaNode):

    DEFAULT_TITLE = 'Component'
    COMPONENT_CLASS = luna_rig.Component
    TITLE_EDITABLE = True

    def __init__(self, scene, title=None):
        super(ComponentNode, self).__init__(scene, title=title)
        self.component_instance = None

    def init_sockets(self, reset=True):
        super(ComponentNode, self).init_sockets(reset=reset)
        # Inputs
        self.in_meta_parent = self.add_input(editor_conf.DataType.COMPONENT, label='Parent', value=None)
        self.in_side = self.add_input(editor_conf.DataType.STRING, label='Side', value='c')
        self.in_name = self.add_input(editor_conf.DataType.STRING, label='Name', value='component')
        self.in_tag = self.add_input(editor_conf.DataType.STRING, label='Tag', value='')

        self.mark_input_as_required(self.in_name)
        self.mark_input_as_required(self.in_side)

        # Outputs
        # Inputs
        self.out_self = self.add_output(editor_conf.DataType.COMPONENT, label='Self', value=None)
        self.out_meta_parent = self.add_output(editor_conf.DataType.COMPONENT, label='Parent', value=None)
        self.out_meta_children = self.add_output(editor_conf.DataType.LIST, label='Children')
        self.out_side = self.add_output(editor_conf.DataType.STRING, label='Side', value='c')
        self.out_name = self.add_output(editor_conf.DataType.STRING, label='Name', value='component')
        self.out_tag = self.add_output(editor_conf.DataType.STRING, label='Tag', value='')

        self.in_meta_parent.affects(self.out_meta_parent)
        self.in_side.affects(self.out_side)
        self.in_name.affects(self.out_name)
        self.in_tag.affects(self.in_tag)


class AnimComponentNode(ComponentNode):

    DEFAULT_TITLE = 'Anim Component'
    COMPONENT_CLASS = luna_rig.AnimComponent

    def init_sockets(self, reset=True):
        super(AnimComponentNode, self).init_sockets(reset=reset)
        # Override types
        self.out_self.data_type = editor_conf.DataType.ANIM_COMPONENT
        self.in_meta_parent.data_type = self.out_meta_parent.data_type = editor_conf.DataType.ANIM_COMPONENT
        self.in_name.set_value('anim_component')

        # Inputs
        self.in_character = self.add_input(editor_conf.DataType.CHARACTER, label='Character')
        self.in_hook = self.add_input(editor_conf.DataType.NUMERIC, label='In Hook')
        self.mark_input_as_required(self.in_character)

        # Outputs
        self.out_character = self.add_output(editor_conf.DataType.CHARACTER, label='Character')
        self.out_in_hook = self.add_output(editor_conf.DataType.NUMERIC, label='In Hook')

        # Affects
        self.in_character.affects(self.out_character)
        self.in_hook.affects(self.out_in_hook)

        # Set default
        self.in_hook.set_value(None)


class GetComponentAsNode(luna_node.LunaNode):
    ID = 3
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = "Get Component As"

    def init_sockets(self, reset=True):
        super(GetComponentAsNode, self).init_sockets(reset=reset)
        self.in_component = self.add_input(editor_conf.DataType.COMPONENT)
        self.in_sample_component = self.add_input(editor_conf.DataType.COMPONENT, label='Sample Type')
        self.out_component = self.add_output(editor_conf.DataType.COMPONENT, label='Cast Result')

        self.mark_input_as_required(self.in_sample_component)

        # Connection
        self.in_sample_component.signals.connection_changed.connect(self.update_out_component_type)

    def execute(self):
        comp_class = self.in_sample_component.value().__class__  # type: luna_rig.Component
        cast_instance = comp_class(self.in_component.value().pynode)
        self.out_component.set_value(cast_instance)

    def update_out_component_type(self):
        if not self.in_sample_component.list_connections():
            self.out_component.data_type = editor_conf.DataType.COMPONENT
            return
        self.out_component.data_type = self.in_sample_component.list_connections()[0].data_type


def register_plugin():
    editor_conf.register_node(GetComponentAsNode.ID, GetComponentAsNode)
    # Component methods
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_side,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Side', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Side',
                                  category='Component')
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_name,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Name', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Name',
                                  category='Component')
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_tag,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Tag', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Tag',
                                  category='Component')
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_meta_parent,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Parent Component', editor_conf.DataType.COMPONENT),
                                  ]),
                                  nice_name='Get Parent',
                                  category='Component')
    editor_conf.register_function(ComponentNode.COMPONENT_CLASS.get_meta_children,
                                  editor_conf.DataType.COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('Component', editor_conf.DataType.COMPONENT),
                                      ('Sample Type', editor_conf.DataType.COMPONENT),
                                      ('By Tag', editor_conf.DataType.STRING)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Children', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='Get Children',
                                  category='Component')

    # Anim Component methods
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_meta_parent,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Parent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  nice_name='Get Parent',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_character,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict={'AnimComponent': editor_conf.DataType.ANIM_COMPONENT},
                                  outputs_dict={'Character': editor_conf.DataType.CHARACTER},
                                  nice_name='Get Character',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_in_hook_index,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict={'AnimComponent': editor_conf.DataType.ANIM_COMPONENT},
                                  outputs_dict={'Hook Index': editor_conf.DataType.NUMERIC},
                                  nice_name='Get In Hook Index',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.list_controls,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Controls', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='List Controls',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_ctl_chain,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Joint Chain', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='Get Ctl Chain',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_character,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Character', editor_conf.DataType.CHARACTER),
                                  ]),
                                  nice_name='Get Character',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_bind_joints,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Bind Joints', editor_conf.DataType.LIST),
                                  ]),
                                  nice_name='Get Bind Joints',
                                  category='Anim Component')

    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_root,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Root Group', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Root',
                                  category='Anim Component')
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_group_ctls,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Ctls Group', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Group Ctls',
                                  category='Anim Component')
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_group_joints,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Joints Group', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Joints Ctls',
                                  category='Anim Component')
    editor_conf.register_function(AnimComponentNode.COMPONENT_CLASS.get_hook_transform,
                                  editor_conf.DataType.ANIM_COMPONENT,
                                  inputs_dict=OrderedDict([
                                      ('AnimComponent', editor_conf.DataType.ANIM_COMPONENT),
                                      ('Hook Index', editor_conf.DataType.NUMERIC)
                                  ]),
                                  outputs_dict=OrderedDict([
                                      ('Transform', editor_conf.DataType.STRING),
                                  ]),
                                  nice_name='Get Hook Transform',
                                  category='Anim Component')
