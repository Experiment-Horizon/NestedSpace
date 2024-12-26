import os
import uuid
import json
import src.schema as schema
from datetime import datetime
import networkx as nx


class SpaceManager:
    def __init__(self, path="./"):
        self.graph = None
        self.path = path

    @staticmethod
    def get_time():
        now = datetime.now()
        current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return current_time_str

    def create_graph(self):
        self.graph = nx.DiGraph()

    def create_node(self, context, **kwargs):

        node_id = str(uuid.uuid4())
        self.graph.add_node(
            node_id,
            created_at=SpaceManager.get_time(),
            last_updated=SpaceManager.get_time(),
            **kwargs
        )
        return node_id

    def create_edge(self, prev_node_id, curr_node_id):
        self.graph.add_edge(prev_node_id, curr_node_id)

    def get_node_properties(self, node_id):
        if node_id in self.graph.nodes:
            return self.graph.nodes[node_id]
        else:
            return None

    def update_node_property(self, node_id, property_name, property_value, add_new=False):
        if not property_name in self.graph.nodes[node_id] and not add_new:
            print("Incorrect property")
        if node_id in self.graph.nodes:
            self.graph.nodes[node_id][property_name] = property_value
        else:
            print("Incorrect ID")
