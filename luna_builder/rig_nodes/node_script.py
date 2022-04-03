import luna_builder.editor.editor_conf as editor_conf
import luna_builder.rig_nodes.luna_node as luna_node


class ScriptNode(luna_node.LunaNode):
    ID = 6
    IS_EXEC = True
    AUTO_INIT_EXECS = True
    TITLE_EDITABLE = True
    ICON = 'python.png'
    DEFAULT_TITLE = 'Script'
    PALETTE_LABEL = 'Script (Python)'
    CATEGORY = 'Utils'

    def __init__(self, scene, title=None):
        super(ScriptNode, self).__init__(scene, title=title)
        self.code = ''

    def execute(self):
        exec(self.code)


def register_plugin():
    editor_conf.register_node(ScriptNode.ID, ScriptNode)
