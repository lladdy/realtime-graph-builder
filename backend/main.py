from typing import Any, Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from graph_builder.simple_graph_builder import SimpleGraphBuilder

app = FastAPI()

# Initialize a single in-memory graph builder instance for the API lifecycle
builder = SimpleGraphBuilder()


@app.on_event("startup")
async def seed_demo_graph() -> None:
    """Seed a simple demo graph at application startup."""
    # Clear any existing state just in case (fresh builder created on import)
    # Add demo nodes
    for n in ["A", "B", "C", "D"]:
        builder.add_node(n)

    # Add demo edges
    demo_edges = [
        ("A", "B"),
        ("A", "C"),
        ("B", "D"),
        ("C", "D"),
    ]
    for u, v in demo_edges:
        builder.add_edge(u, v)


class ConnectionManager:
    """Simple in-memory WebSocket connection manager."""

    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        # Send to a copy to avoid mutation during iteration
        dead: Set[WebSocket] = set()
        for ws in list(self.active_connections):
            try:
                await ws.send_json(message)
            except Exception:
                # Mark broken sockets for cleanup
                dead.add(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


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
    # Notify subscribers about the update
    await manager.broadcast({"event": "graph_update", "graph": builder.get_graph()})
    return {"status": "ok", "node": payload.node}


@app.post("/edges")
async def add_edge(payload: EdgeIn):
    builder.add_edge(payload.from_node, payload.to_node)
    # Notify subscribers about the update
    await manager.broadcast({"event": "graph_update", "graph": builder.get_graph()})
    return {"status": "ok", "from": payload.from_node, "to": payload.to_node}


@app.delete("/graph")
async def reset_graph():
    global builder
    builder = SimpleGraphBuilder()
    # Notify subscribers that the graph has been reset
    await manager.broadcast({"event": "graph_reset", "graph": builder.get_graph()})
    return {"status": "ok", "message": "graph reset"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept and register the connection
    await manager.connect(websocket)
    # Send the current graph immediately upon connection
    try:
        await websocket.send_json({"event": "graph_init", "graph": builder.get_graph()})
        while True:
            # Keep the connection open; ignore any incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
