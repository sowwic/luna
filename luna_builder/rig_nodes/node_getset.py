from luna import Logger
import luna_builder.rig_nodes.luna_node as luna_node
import luna_builder.editor.editor_conf as editor_conf


class VarNode(luna_node.LunaNode):
    ID = None
    IS_EXEC = True
    AUTO_INIT_EXECS = False
    DEFAULT_TITLE = ''
    CATEGORY = editor_conf.INTERNAL_CATEGORY

    def __init__(self, scene, title=None):
        self._var_name = None
        super(VarNode, self).__init__(scene, title=title)

    @property
    def var_name(self):
        return self._var_name

    def set_var_name(self, name, init_sockets=False):
        self._var_name = name
        var_exists = name in self.scene.vars._vars.keys()
        self.set_invalid(not var_exists)
        if not var_exists:
            Logger.warning('Variable "{0}" no longer exists'.format(name))
            return

        self.title = '{0} {1}'.format(self.DEFAULT_TITLE, self._var_name)
        if init_sockets:
            self.init_sockets()

    def get_var_value(self):
        try:
            return self.scene.vars.get_value(self.var_name)
        except KeyError:
            return None

    def set_var_value(self, value):
        try:
            self.scene.vars.set_value(self.var_name, value)
        except KeyError:
            Logger.error('Variable {0} does not exist!')
            raise

    def update(self):
        raise NotImplementedError

    def verify(self):
        result = super(VarNode, self).verify()
        if self.var_name not in self.scene.vars._vars.keys():
            self.append_tooltip('Variable {0} does not exist'.format(self.var_name))
            result = False
        return result

    def serialize(self):
        result = super(VarNode, self).serialize()
        result['var_name'] = self.var_name
        return result

    def pre_deserilization(self, data):
        self.set_var_name(data.get('var_name'), init_sockets=True)

    def get_attrib_widget(self):
        return None


class SetNode(VarNode):
    ID = editor_conf.SET_NODE_ID
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    ICON = None
    DEFAULT_TITLE = 'Set'

    def init_sockets(self, reset=True):
        super(SetNode, self).init_sockets(reset=reset)
        if not self.var_name:
            return

        self.in_value = self.add_input(self.scene.vars.get_data_type(self.var_name, as_dict=True))
        self.out_value = self.add_output(self.scene.vars.get_data_type(self.var_name, as_dict=True), label='')
        self.out_value.value = self.get_var_value
        self.mark_input_as_required(self.in_value)

    def update(self):
        var_type = self.scene.vars.get_data_type(self.var_name, as_dict=True)
        if not self.in_value.data_type == var_type:
            self.in_value.label = var_type['label']
            self.in_value.data_type = var_type
            self.out_value.data_type = var_type
            self.in_value.update_positions()

    def execute(self):
        if not self.var_name:
            Logger.error('{0}: var_name is not set'.format(self))
            raise ValueError
        self.set_var_value(self.in_value.value())


class GetNode(VarNode):
    ID = editor_conf.GET_NODE_ID
    IS_EXEC = False
    STATUS_ICON = False
    AUTO_INIT_EXECS = False
    MIN_WIDTH = 110
    OUTPUT_POSITION = 5
    ICON = None
    DEFAULT_TITLE = 'Get'

    def init_sockets(self, reset=True):
        if not self.var_name:
            return

        super(GetNode, self).init_sockets(reset=reset)
        self.out_value = self.add_output(self.scene.vars.get_data_type(self.var_name, as_dict=True), value=self.scene.vars.get_value(self.var_name))
        self.out_value.value = self.get_var_value

    def update(self):
        var_type = self.scene.vars.get_data_type(self.var_name, as_dict=True)
        if not self.out_value.data_type == var_type:
            self.out_value.label = var_type['label']
            self.out_value.data_type = var_type
            self.out_value.update_positions()


def register_plugin():
    editor_conf.register_node(SetNode.ID, SetNode)
    editor_conf.register_node(GetNode.ID, GetNode)
