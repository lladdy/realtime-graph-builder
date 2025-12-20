import pytest
from graph_builder_lib.simple_graph_builder import SimpleGraphBuilder


def test_add_node():
    b = SimpleGraphBuilder()
    b.add_node("A")
    g = b.get_graph()
    assert "A" in g
    assert g["A"] == []


def test_add_edge_creates_nodes():
    b = SimpleGraphBuilder()
    b.add_edge("A", "B")
    g = b.get_graph()
    assert "A" in g and "B" in g
    assert g["A"] == ["B"]
    assert g["B"] == []


def test_multiple_edges():
    b = SimpleGraphBuilder()
    b.add_edge("A", "B")
    b.add_edge("A", "C")
    assert b.get_graph()["A"] == ["B", "C"]


def test_duplicate_node_noop():
    b = SimpleGraphBuilder()
    b.add_node("A")
    b.add_node("A")
    assert list(b.get_graph().keys()).count("A") == 1
    assert b.get_graph()["A"] == []


def test_duplicate_edge_allows_duplicates():
    b = SimpleGraphBuilder()
    b.add_edge("A", "B")
    b.add_edge("A", "B")
    assert b.get_graph()["A"] == ["B", "B"]


def test_self_loop():
    b = SimpleGraphBuilder()
    b.add_edge("A", "A")
    assert b.get_graph()["A"] == ["A"]


def test_unhashable_node_raises_type_error():
    b = SimpleGraphBuilder()
    with pytest.raises(TypeError):
        b.add_node([])

    with pytest.raises(TypeError):
        b.add_edge([], "A")


def test_get_graph_returns_internal_reference():
    b = SimpleGraphBuilder()
    b.add_node("A")
    g = b.get_graph()
    # mutate returned dict and ensure the builder reflects the change
    g["B"] = []
    assert "B" in b.get_graph()
    # ensure get_graph returns the same object (current implementation)
    assert b.get_graph() is g
