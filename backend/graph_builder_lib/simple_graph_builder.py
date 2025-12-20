from graph_builder_lib.graph_builder import GraphBuilder


class SimpleGraphBuilder(GraphBuilder):
    def __init__(self):
        self.graph = {}

    def add_node(self, node):
        if node not in self.graph:
            self.graph[node] = []

    def add_edge(self, from_node, to_node):
        if from_node not in self.graph:
            self.add_node(from_node)
        if to_node not in self.graph:
            self.add_node(to_node)
        self.graph[from_node].append(to_node)

    def get_graph(self):
        return self.graph

