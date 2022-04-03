from collections import deque
import luna_builder.rig_nodes.luna_node as luna_node
import luna_builder.editor.editor_conf as editor_conf


class ForEachNode(luna_node.LunaNode):
    ID = None
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = 'For Each'
    CATEGORY = 'Collections'
    COLLECTION_DATATYPE = None

    def init_sockets(self, reset=True):
        super(ForEachNode, self).init_sockets(reset=reset)
        self.in_collection = self.add_input(editor_conf.DataType.LIST, label='List')
        self.out_loop_body = self.add_output(editor_conf.DataType.EXEC, label='Loop body', max_connections=1)
        self.out_item = self.add_output(self.COLLECTION_DATATYPE, label='Item')
        self.mark_input_as_required(self.in_collection)

    def list_exec_outputs(self):
        return [self.exec_out_socket]

    def get_loop_body(self):
        loop_body = deque()
        if self.out_loop_body.list_connections():
            loop_body.extend(self.out_loop_body.list_connections()[0].node.get_exec_queue())
        return loop_body

    def verify(self):
        result = super(ForEachNode, self).verify()
        if not result:
            return False
        for node in self.get_loop_body():
            result = node.verify()
            if not result:
                return False
        return True

    def execute(self):
        for item in self.in_collection.value():
            self.out_item.set_value(item)
            for node in self.get_loop_body():
                node._exec()


class ForEachComponent(ForEachNode):
    ID = 105
    DEFAULT_TITLE = "For Each Component"
    COLLECTION_DATATYPE = editor_conf.DataType.COMPONENT


class ForEachName(ForEachNode):
    ID = 106
    DEFAULT_TITLE = "For Each Name"
    COLLECTION_DATATYPE = editor_conf.DataType.STRING


def register_plugin():
    editor_conf.register_node(ForEachComponent.ID, ForEachComponent)
    editor_conf.register_node(ForEachName.ID, ForEachName)
