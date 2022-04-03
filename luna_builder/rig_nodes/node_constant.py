import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ConstantNode(luna_node.LunaNode):
    IS_EXEC = False
    DEFAULT_TITLE = 'Constant'
    STATUS_ICON = False
    CATEGORY = 'Constants'
    MIN_WIDTH = 100
    CONSTANT_DATA_TYPE = None

    def __init__(self, scene, title=None):
        self.data_type = getattr(editor_conf.DataType, self.CONSTANT_DATA_TYPE)
        super(ConstantNode, self).__init__(scene, title=title)
        self.update_title()

    def init_sockets(self, reset=True):
        self.out_value = self.add_output(self.data_type, label='Value', value=None)

    def create_connections(self):
        super(ConstantNode, self).create_connections()
        self.out_value.signals.value_changed.connect(self.update_title)

    def update_title(self):
        self.title = '{0}: {1}'.format(self.DEFAULT_TITLE, self.out_value.value())


class ConstantFloatNode(ConstantNode):
    ID = 12
    CONSTANT_DATA_TYPE = 'NUMERIC'
    DEFAULT_TITLE = 'Number'


class ConstantStringNode(ConstantNode):
    ID = 13
    CONSTANT_DATA_TYPE = 'STRING'
    DEFAULT_TITLE = 'String'


class ConstantBoolNode(ConstantNode):
    ID = 14
    CONSTANT_DATA_TYPE = 'BOOLEAN'
    DEFAULT_TITLE = 'Boolean'


def register_plugin():
    for cls in [ConstantFloatNode, ConstantStringNode, ConstantBoolNode]:
        editor_conf.register_node(cls.ID, cls)
