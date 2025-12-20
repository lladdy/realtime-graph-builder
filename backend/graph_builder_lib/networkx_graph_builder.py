from graph_builder_lib.graph_builder import GraphBuilder
import networkx as nx


class NetworkXGraphBuilder(GraphBuilder):
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node):
        self.graph.add_node(node)

    def add_edge(self, from_node, to_node):
        self.graph.add_edge(from_node, to_node)

    def get_graph(self):
        return self.graph
