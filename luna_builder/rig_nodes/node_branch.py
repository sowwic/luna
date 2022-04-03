import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class BranchNode(luna_node.LunaNode):
    ID = 1
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    ICON = 'branch.png'
    DEFAULT_TITLE = 'Branch'
    CATEGORY = 'Utils'

    def init_sockets(self, reset=True):
        super(BranchNode, self).init_sockets(reset=reset)
        self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
        self.in_condition = self.add_input(editor_conf.DataType.BOOLEAN)

        self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC, label='True')
        self.out_true = self.exec_out_socket
        self.out_false = self.add_output(editor_conf.DataType.EXEC, label='False')
        self.update_title()

    def create_connections(self):
        super(BranchNode, self).create_connections()
        self.in_condition.signals.value_changed.connect(self.update_title)

    def update_title(self):
        self.title = '{0}: {1}'.format(self.DEFAULT_TITLE, self.in_condition.value())

    def list_exec_outputs(self):
        if self.in_condition.value():
            return [self.out_true]
        else:
            return [self.out_false]


def register_plugin():
    editor_conf.register_node(BranchNode.ID, BranchNode)
