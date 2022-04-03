import sys
from luna import Logger
import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class FunctionNode(luna_node.LunaNode):
    ID = editor_conf.FUNC_NODE_ID
    IS_EXEC = True
    ICON = 'func.png'
    AUTO_INIT_EXECS = True
    DEFAULT_TITLE = 'Function'
    CATEGORY = editor_conf.INTERNAL_CATEGORY

    def __init__(self, scene, title=None):
        self._func_signature = ''
        self._func_desc = {}
        super(FunctionNode, self).__init__(scene, title=title)

    def init_sockets(self, reset=True):
        super(FunctionNode, self).init_sockets(reset=reset)
        if not self._func_desc:
            return

        for socket_name, socket_datatype in self.func_desc.get('inputs').items():
            if isinstance(socket_datatype, str):
                socket_datatype = editor_conf.DATATYPE_REGISTER[socket_datatype]
            self.add_input(socket_datatype, socket_name)

        for socket_name, socket_datatype in self.func_desc.get('outputs').items():
            if isinstance(socket_datatype, str):
                socket_datatype = editor_conf.DATATYPE_REGISTER[socket_datatype]
            self.add_output(socket_datatype, socket_name)

        # Set default input values
        for socket, input_value in zip(self.list_non_exec_inputs(), self.func_desc.get('default_values')):
            socket.set_value(input_value)

    @property
    def func_signature(self):
        return self._func_signature

    @func_signature.setter
    def func_signature(self, value):
        self.set_signature_without_reinit(value)
        self.init_sockets(reset=True)

    @property
    def func_ref(self):
        reference = self.func_desc.get('ref') if self.func_signature else None  # type: function
        return reference

    def set_signature_without_reinit(self, signature):
        self._func_signature = signature
        self._func_desc = editor_conf.get_function_from_signature(signature)
        if not self._func_signature:
            Logger.warning('{0}: Missing function signature!'.format(self))

    @property
    def func_desc(self):
        return self._func_desc

    def serialize(self):
        try:
            res = super(FunctionNode, self).serialize()
        except TypeError:
            pass
        res['func_signature'] = self.func_signature
        return res

    def pre_deserilization(self, data):
        func_sign = data.get('func_signature')  # type: str
        if sys.version_info[0] >= 3 and '__builtin__' in func_sign:
            self.func_signature = func_sign.replace('__builtin__', 'builtins')
        elif sys.version_info[0] < 3 and 'builtins' in func_sign:
            self.func_signature = func_sign.replace('builtins', '__builtin__')
        else:
            self.func_signature = func_sign

    def execute(self):
        attr_values = [socket.value() for socket in self.list_non_exec_inputs()]
        func_result = self.func_ref(*attr_values)
        Logger.debug('Function result: {0}'.format(func_result))

        # Set outputs
        if not isinstance(func_result, (list, tuple)):
            func_result = [func_result]

        non_exec_outs = self.list_non_exec_outputs()
        if non_exec_outs and non_exec_outs[0].data_type == editor_conf.DataType.LIST:
            non_exec_outs[0].set_value(func_result)
        else:
            for index, out_socket in enumerate(self.list_non_exec_outputs()):
                try:
                    out_socket.set_value(func_result[index])
                except IndexError:
                    Logger.error('Missing return result for function {0}, at index {1}'.format(self.func_ref, index))
                    raise


def register_plugin():
    editor_conf.register_node(FunctionNode.ID, FunctionNode)
