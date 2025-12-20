from graph_builder.graph_builder import GraphBuilder


class NetworkXGraphBuilder(GraphBuilder):
    def __init__(self):
        import networkx as nx
        self.graph = nx.DiGraph()

    def add_node(self, node):
        self.graph.add_node(node)

    def add_edge(self, from_node, to_node):
        self.graph.add_edge(from_node, to_node)

    def get_graph(self):
        return self.graph
