import pymel.core as pm
from collections import OrderedDict
import luna_builder.rig_nodes.luna_node as luna_node
import luna_builder.editor.editor_conf as editor_conf


class ConnectAttribNode(luna_node.LunaNode):
    ID = 23
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    ICON = None
    DEFAULT_TITLE = 'Connect Attributes'
    CATEGORY = 'Functions/Pymel'

    def init_sockets(self, reset=True):
        super(ConnectAttribNode, self).init_sockets(reset=reset)
        self.in_source_node_name = self.add_input(editor_conf.DataType.STRING, label='Source Node')
        self.in_source_attr_name = self.add_input(editor_conf.DataType.STRING, label='Source Attribute')
        self.in_dest_node_name = self.add_input(editor_conf.DataType.STRING, label='Destination Node')
        self.in_dest_attr_name = self.add_input(editor_conf.DataType.STRING, label='Destination Attribute')

        self.mark_inputs_required((self.in_source_node_name,
                                   self.in_source_attr_name,
                                   self.in_dest_node_name,
                                   self.in_dest_attr_name))

    def execute(self):
        pm.connectAttr('{0}.{1}'.format(self.in_source_node_name.value(), self.in_source_attr_name.value()),
                       '{0}.{1}'.format(self.in_dest_node_name.value(), self.in_dest_attr_name.value()))


class AddToggleAttribNode(luna_node.LunaNode):
    ID = 24
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    ICON = None
    DEFAULT_TITLE = 'Add Toggle Attribute'
    CATEGORY = 'Functions/Pymel'

    def init_sockets(self, reset=True):
        super(AddToggleAttribNode, self).init_sockets(reset=reset)
        self.in_node_name = self.add_input(editor_conf.DataType.STRING, label='Node')
        self.in_attr_name = self.add_input(editor_conf.DataType.STRING, label='Name', value='newAttr')
        self.in_default_value = self.add_input(editor_conf.DataType.BOOLEAN, label='Value', value=False)

    def execute(self):
        pm.addAttr(self.in_node_name.value(), ln=self.in_attr_name.value(), at='bool', k=True, dv=self.in_default_value.value())


def register_plugin():
    editor_conf.register_node(ConnectAttribNode.ID, ConnectAttribNode)
    editor_conf.register_node(AddToggleAttribNode.ID, AddToggleAttribNode)

    editor_conf.register_function(pm.parent,
                                  None,
                                  OrderedDict([
                                      ('Child', editor_conf.DataType.STRING),
                                      ('Parent', editor_conf.DataType.STRING)]),
                                  nice_name='Parent',
                                  category='Pymel')
