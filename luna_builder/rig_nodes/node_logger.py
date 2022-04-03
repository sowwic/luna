from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class LoggerNode(luna_node.LunaNode):
    ID = 11
    IS_EXEC = True
    ICON = 'func.png'
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = 'Log'
    CATEGORY = 'Utils'

    def init_sockets(self, reset=True):
        super(LoggerNode, self).init_sockets(reset=reset)
        self.in_message = self.add_input(editor_conf.DataType.STRING, 'Message')
        self.in_info = self.add_input(editor_conf.DataType.BOOLEAN, 'As Info', value=True)
        self.in_warning = self.add_input(editor_conf.DataType.BOOLEAN, 'As Warning', value=False)
        self.in_error = self.add_input(editor_conf.DataType.BOOLEAN, 'As Error', value=False)
        self.update_title()

    def create_connections(self):
        super(LoggerNode, self).create_connections()
        self.in_message.signals.value_changed.connect(self.update_title)

    def update_title(self):
        self.title = '{0}: {1}'.format(self.DEFAULT_TITLE, self.in_message.value())

    def execute(self):
        if self.in_info.value():
            Logger.info(self.in_message.value())
        if self.in_warning.value():
            Logger.warning(self.in_message.value())
        if self.in_error.value():
            Logger.error(self.in_message.value())


def register_plugin():
    editor_conf.register_node(LoggerNode.ID, LoggerNode)
