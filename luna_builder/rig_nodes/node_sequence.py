import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class SequenceNode(luna_node.LunaNode):
    ID = 5
    IS_EXEC = True
    TITLE_EDITABLE = True
    ICON = 'sequence.png'
    AUTO_INIT_EXECS = False
    DEFAULT_TITLE = 'Sequence'
    CATEGORY = 'Utils'

    def init_sockets(self, reset=True):
        self.exec_in_socket = self.add_input(editor_conf.DataType.EXEC)
        self.exec_out_socket = self.add_output(editor_conf.DataType.EXEC, label='Then 0')
        for i in range(1, 6):
            self.add_output(editor_conf.DataType.EXEC, label='Then {0}'.format(i))


def register_plugin():
    editor_conf.register_node(SequenceNode.ID, SequenceNode)
