from abc import ABC, abstractmethod


class GraphBuilder(ABC):
    """Abstract base class for graph builders."""

    @abstractmethod
    def add_node(self, node):
        """Add a node to the graph."""
        pass

    @abstractmethod
    def add_edge(self, from_node, to_node):
        """Add a directed edge from from_node to to_node."""
        pass

    @abstractmethod
    def get_graph(self):
        """Return the underlying graph representation."""
        pass
