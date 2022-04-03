import itertools
from collections import deque
from luna import Logger
from luna import Config
from luna import BuilderVars


class SceneHistory(object):

    SCENE_INIT_DESC = 'SceneInit'

    def __len__(self):
        return len(self.stack)

    def __init__(self, scene):
        self.scene = scene

        self.enabled = Config.get(BuilderVars.history_enabled, default=True, cached=True)
        self._size = Config.get(BuilderVars.history_size, default=32, cached=True)
        self.stack = deque(maxlen=self._size)
        self.current_step = -1

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size):
        self._size = new_size
        self.stack = deque(self.stack, maxlen=new_size)

    def clear(self):
        self.stack.clear()
        self.current_step = -1

    def undo(self):
        if not self.enabled:
            Logger.warning('History is disabled')
            return

        if self.current_step > 0:
            Logger.info('> Undo {0}'.format(self.stack[self.current_step]['desc']))
            self.current_step -= 1
            self.restore_history()
        else:
            Logger.warning('No more steps to undo')

    def redo(self):
        if not self.enabled:
            Logger.warning('History is disabled')
            return

        if self.current_step + 1 < len(self.stack):
            self.current_step += 1
            self.restore_history()
        else:
            Logger.warning('No more steps to redo')

    def restore_history(self):
        self.enabled = False
        # Logger.debug('Restoring history | \nStep: @{0} | Stack: {1}'.format(self.current_step, len(self)))
        self.restore_stamp(self.stack[self.current_step])
        self.scene.has_been_modified = True
        self.enabled = True

    def store_history(self, description, set_modified=True):
        if not self.enabled:
            return

        # if the pointer (current_step) is not at the end of stack
        if self.current_step + 1 < len(self.stack):
            self.stack = deque(itertools.islice(self.stack, self.current_step + 1))

        hs = self.create_stamp(description)

        # Increment step if possible
        self.stack.append(hs)
        if not self.stack.maxlen or self.current_step + 1 < self.stack.maxlen:
            self.current_step += 1

        # Log change
        if description != SceneHistory.SCENE_INIT_DESC:
            Logger.info('> {0}'.format(description))
        else:
            set_modified = False

        if set_modified:
            self.scene.has_been_modified = True

    def create_stamp(self, description):
        sel_obj = {'nodes': [node.uid for node in self.scene.selected_nodes],
                   'edges': [edge.uid for edge in self.scene.selected_edges]}

        stamp = {
            'desc': description,
            'snapshot': self.scene.serialize(),
            'selection': sel_obj
        }

        return stamp

    def restore_stamp(self, stamp):

        try:
            self.scene.deserialize(stamp['snapshot'])
            self.scene.gr_scene.clearSelection()

            # Restore selection
            for edge_uid in stamp['selection']['edges']:
                for edge in self.scene.edges:
                    if edge.uid == edge_uid:
                        edge.gr_edge.setSelected(True)
                        break

            for node_uid in stamp['selection']['nodes']:
                for node in self.scene.nodes:
                    if node.uid == node_uid:
                        node.gr_node.setSelected(True)
                        break
        except Exception:
            Logger.exception('Restore history stamp exception.')
            raise

    def debug_varibles(self):
        for step, stamp in enumerate(self.stack):
            Logger.debug('Step {0} - {1}'.format(step, stamp['snapshot']['vars']))
