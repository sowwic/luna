import timeit

from collections import deque
from luna import Logger
import luna_builder.editor.editor_conf as editor_conf


class GraphExecutor(object):
    # TODO: Step by step execution
    def __init__(self, scene):
        self.scene = scene
        self.step = 0
        self._exec_chain = deque()  # type: deque
        self._exec_set = set()  # type: set

    @property
    def exec_chain(self):
        return self._exec_chain

    @exec_chain.setter
    def exec_chain(self, queue):
        self._exec_chain = queue
        self._exec_set = set(queue)

    @property
    def exec_set(self):
        return self._exec_set

    def reset_nodes_compiled_state(self):
        for node in self.scene.nodes:
            node._is_compiled = False

    def find_input_node(self):
        input_nodes = [node for node in self.scene.nodes if node.ID == editor_conf.INPUT_NODE_ID]
        if not input_nodes:
            Logger.error('At least one input node is required!')
            return None
        elif len(input_nodes) > 1:
            Logger.warning('More than 1 input node in the scene. Only the first one added will be executed!')
        return input_nodes[0]

    def ready_to_execute(self):
        self.reset_nodes_compiled_state()
        input_node = self.find_input_node()
        if not input_node:
            return False

        self.exec_chain = input_node.get_exec_queue()
        result = self.verify_graph()
        if not result:
            Logger.warning('Invalid graph, execution canceled')
            return False
        return True

    def execute_graph(self):
        self.reset_stepped_execution()
        if not self.ready_to_execute():
            return

        Logger.info('Initiating new build...')
        start_time = timeit.default_timer()
        self.scene.is_executing = True
        for node in self.exec_chain:
            try:
                node._exec()
            except Exception:
                Logger.exception('Failed to execute {0}'.format(node.title))
                self.scene.is_executing = False
                return

        Logger.info("Build finished in {0:.2f}s".format(timeit.default_timer() - start_time))
        self.scene.is_executing = False

    def execute_step(self):
        if self.step == len(self.exec_chain):
            self.reset_stepped_execution()

        if not self.exec_chain and not self.ready_to_execute():
            return

        try:
            self.scene.is_executing = True
            node = self.exec_chain[self.step]
            node._exec()
            self.step += 1
        except Exception:
            Logger.exception('Failed to execute {0}'.format(node.title))
            self.scene.is_executing = False
            return

    def reset_stepped_execution(self):
        self.step = 0
        self.exec_chain.clear()
        self.exec_set.clear()

    def verify_graph(self):
        Logger.info('Verifing graph...')
        invalid_nodes = deque()
        for node in self.exec_chain:
            result = node.verify()
            if not result:
                node.set_invalid(True)
                invalid_nodes.append(node)
        if invalid_nodes:
            for node in invalid_nodes:
                Logger.warning('Invalid node: {0}'.format(node.title))
            return False

        return True
