import pytest

pytest.importorskip("networkx")

from graph_builder_lib.networkx_graph_builder import NetworkXGraphBuilder


def nx_neighbors_list(g, node):
    return list(g.successors(node))


def test_add_node_nx():
    b = NetworkXGraphBuilder()
    b.add_node("A")
    g = b.get_graph()
    assert "A" in g
    assert nx_neighbors_list(g, "A") == []


def test_add_edge_creates_nodes_nx():
    b = NetworkXGraphBuilder()
    b.add_edge("A", "B")
    g = b.get_graph()
    assert "A" in g and "B" in g
    assert nx_neighbors_list(g, "A") == ["B"]
    assert nx_neighbors_list(g, "B") == []


def test_multiple_edges_nx():
    b = NetworkXGraphBuilder()
    b.add_edge("A", "B")
    b.add_edge("A", "C")
    assert nx_neighbors_list(b.get_graph(), "A") == ["B", "C"]


def test_duplicate_edge_does_not_duplicate_in_digraph():
    b = NetworkXGraphBuilder()
    b.add_edge("A", "B")
    b.add_edge("A", "B")
    # In DiGraph, duplicates are not created; edge set remains single
    assert nx_neighbors_list(b.get_graph(), "A") == ["B"]


def test_self_loop_nx():
    b = NetworkXGraphBuilder()
    b.add_edge("A", "A")
    assert nx_neighbors_list(b.get_graph(), "A") == ["A"]


def test_unhashable_node_raises_type_error_nx():
    b = NetworkXGraphBuilder()
    with pytest.raises(TypeError):
        b.add_node([])

    with pytest.raises(TypeError):
        b.add_edge([], "A")


def test_get_graph_returns_internal_reference_nx():
    b = NetworkXGraphBuilder()
    g = b.get_graph()
    # ensure get_graph returns the same object (current implementation)
    assert b.get_graph() is g
