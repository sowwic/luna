from collections import OrderedDict
import luna_rig
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.base_component as base_component


class IKSplineStretchComponentNode(base_component.ComponentNode):
    ID = 21
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'Spline Stretch'
    CATEGORY = 'Components'
    COMPONENT_CLASS = luna_rig.components.IKSplineStretchComponent

    def init_sockets(self, reset=True):
        super(IKSplineStretchComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('stretch')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.IK_SPLINE_STRETCH_COMPONENT

        self.in_switch_control = self.add_input(editor_conf.DataType.CONTROL, label='Switch Control')
        self.in_default_state = self.add_input(editor_conf.DataType.BOOLEAN, label='Default State', value=False)
        self.in_switch_attr_name = self.add_input(editor_conf.DataType.STRING, label='Stretch Attribute', value='stretch')
        self.in_stretch_axis = self.add_input(editor_conf.DataType.STRING, label='Stretch Axis', value='x')

        # Mark required
        self.mark_inputs_required((self.in_meta_parent,
                                   self.in_switch_attr_name,
                                   self.in_stretch_axis))

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(self.in_meta_parent.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              switch_control=self.in_switch_control.value(),
                                                              default_state=self.in_default_state.value(),
                                                              switch_attr=self.in_switch_attr_name.value(),
                                                              stretch_axis=self.in_stretch_axis.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


class IKStretchComponentNode(base_component.ComponentNode):
    ID = 22
    IS_EXEC = True
    ICON = None
    DEFAULT_TITLE = 'IK Stretch'
    CATEGORY = 'Components'
    COMPONENT_CLASS = luna_rig.components.IKStretchComponent

    def init_sockets(self, reset=True):
        super(IKStretchComponentNode, self).init_sockets(reset=reset)
        # Override inputs
        self.in_name.set_value('stretch')

        # Override Outputs
        self.out_self.data_type = editor_conf.DataType.IK_STRETCH_COMPONENT

        self.in_switch_control = self.add_input(editor_conf.DataType.CONTROL, label='Switch Control')
        self.in_default_state = self.add_input(editor_conf.DataType.BOOLEAN, label='Default State', value=False)
        self.in_toggle_attr_name = self.add_input(editor_conf.DataType.STRING, label='Stretch Attribute', value='stretch')
        self.in_stretch_axis = self.add_input(editor_conf.DataType.STRING, label='Stretch Axis', value='x')
        self.in_threshold = self.add_input(editor_conf.DataType.NUMERIC, label='Threshold', value=0.0)
        self.in_threshold_attr_name = self.add_input(editor_conf.DataType.STRING, label='Threshold Attribute', value='stretchThreshold')

    def execute(self):
        self.component_instance = self.COMPONENT_CLASS.create(self.in_meta_parent.value(),
                                                              side=self.in_side.value(),
                                                              name=self.in_name.value(),
                                                              switch_control=self.in_switch_control.value(),
                                                              default_state=self.in_default_state.value(),
                                                              toggle_attr_name=self.in_toggle_attr_name.value(),
                                                              stretch_axis=self.in_stretch_axis.value(),
                                                              threshold=self.in_threshold.value(),
                                                              threshold_attr_name=self.in_threshold_attr_name.value(),
                                                              tag=self.in_tag.value())
        self.out_self.set_value(self.component_instance)


def register_plugin():
    editor_conf.DataType.register_datatype('IK_SPLINE_STRETCH_COMPONENT', luna_rig.components.IKSplineStretchComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='Spline Stretch',
                                           default_value=None)
    editor_conf.DataType.register_datatype('IK_STRETCH_COMPONENT', luna_rig.components.IKStretchComponent,
                                           editor_conf.DataType.COMPONENT.get('color'),
                                           label='IK Stretch',
                                           default_value=None)
    editor_conf.register_node(IKSplineStretchComponentNode.ID, IKSplineStretchComponentNode)
    editor_conf.register_node(IKStretchComponentNode.ID, IKStretchComponentNode)
