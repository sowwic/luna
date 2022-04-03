from collections import OrderedDict
from luna import Logger
import luna_builder.editor.node_node as node_node
import luna_builder.editor.node_edge as node_edge


class SceneClipboard(object):
    def __init__(self, scene):
        self.scene = scene

    def serialize_selected(self, delete=False):
        sel_nodes = []
        sel_sockets = {}
        sel_edges = self.scene.selected_edges  # type: list

        # Sort edges and nodes
        for node in self.scene.selected_nodes:
            sel_nodes.append(node.serialize())
            for socket in node.inputs + node.outputs:
                sel_sockets[socket.uid] = socket

        # Remove all edges not connected to a node in selected list
        edges_to_remove = []
        for edge in sel_edges:
            if edge.start_socket.uid not in sel_sockets or edge.end_socket.uid not in sel_sockets:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            sel_edges.remove(edge)
        # Make final list of serialized edges
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final)
        ])
        # if cut -> remove selected items
        if delete:
            self.scene.delete_selected(store_history=False)
            # Store history
            self.scene.history.store_history('Cut items', set_modified=True)

        return data

    def deserialize_from_clip(self, data):
        hashmap = {}

        # Calculate mouse pointer - paste position
        view = self.scene.view
        mouse_scene_pos = view.last_scene_mouse_pos
        mouse_x, mouse_y = mouse_scene_pos.x(), mouse_scene_pos.y()

        # Calculate selected objects bbox and center
        minx, maxx, miny, maxy = 10000000, -10000000, 10000000, -10000000
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            minx = min(x, minx)
            maxx = max(x, maxx)
            miny = min(y, miny)
            maxy = max(y, maxy)

        created_nodes = []
        # Create each node
        for node_data in data['nodes']:
            node_class = self.scene.get_class_from_node_data(node_data)
            new_node = node_class(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False)
            created_nodes.append(new_node)

            # Adjust node position
            pos_x, pos_y = new_node.position.x(), new_node.position.y()
            new_x, new_y = mouse_x + pos_x - minx, mouse_y + pos_y - miny
            new_node.set_position(new_x, new_y)

        # Create each edge
        for edge_data in data['edges']:
            new_edge = node_edge.Edge(self.scene)
            new_edge.deserialize(edge_data, hashmap, restore_id=False)

        self.scene.history.store_history('Paste items', set_modified=True)
        return created_nodes
