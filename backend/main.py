from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from graph_builder_lib.simple_graph_builder import SimpleGraphBuilder

app = FastAPI()

# Initialize a single in-memory graph builder instance for the API lifecycle
builder = SimpleGraphBuilder()


class NodeIn(BaseModel):
    node: Any


class EdgeIn(BaseModel):
    from_node: Any
    to_node: Any


@app.get("/graph")
async def get_graph() -> Dict[Any, list]:
    """Return the current in-memory graph as an adjacency list."""
    return builder.get_graph()


@app.post("/nodes")
async def add_node(payload: NodeIn):
    builder.add_node(payload.node)
    return {"status": "ok", "node": payload.node}


@app.post("/edges")
async def add_edge(payload: EdgeIn):
    builder.add_edge(payload.from_node, payload.to_node)
    return {"status": "ok", "from": payload.from_node, "to": payload.to_node}


@app.delete("/graph")
async def reset_graph():
    global builder
    builder = SimpleGraphBuilder()
    return {"status": "ok", "message": "graph reset"}
