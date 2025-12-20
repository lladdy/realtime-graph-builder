import asyncio
from typing import Any, Dict, Optional, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from graph_builder.simple_graph_builder import SimpleGraphBuilder

app = FastAPI()

# Initialize a single in-memory graph builder instance for the API lifecycle
builder = SimpleGraphBuilder()
grow_task: Optional[asyncio.Task] = None


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

    # Start background worker that slowly grows the graph
    global grow_task
    if grow_task is None or grow_task.done():
        grow_task = asyncio.create_task(grow_graph_worker())


async def grow_graph_worker() -> None:
    """Background task that periodically grows the graph and broadcasts updates."""
    counter = 1
    try:
        while True:
            # Wait a bit between updates to grow the graph slowly
            await asyncio.sleep(10)

            # Create a new node name and add it
            new_node = f"N{counter}"
            builder.add_node(new_node)

            # Connect the new node to an existing node (round-robin selection)
            graph = builder.get_graph()
            existing_nodes = [n for n in graph.keys() if n != new_node]
            if existing_nodes:
                print(f"Connecting new node {new_node} to existing node {existing_nodes[counter % len(existing_nodes)]}")
                parent = existing_nodes[counter % len(existing_nodes)]
                builder.add_edge(parent, new_node)

            # Notify subscribers incrementally: node added, then edge added (if any)
            await manager.broadcast({"event": "node_added", "node": new_node})
            if existing_nodes:
                await manager.broadcast({
                    "event": "edge_added",
                    "from": parent,
                    "to": new_node,
                })
            counter += 1
    except asyncio.CancelledError:
        # Graceful cancellation on shutdown
        pass


# Replace raw WebSocket handling with a Connection abstraction that encapsulates
# send/receive and failure detection.
class Connection:
    """Wrap a WebSocket and provide resilient send/receive operations."""

    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket
        self.open = True

    async def accept(self) -> None:
        await self.websocket.accept()

    async def send_json(self, message: Dict[str, Any]) -> bool:
        """Send a JSON message. Return True if send succeeded, False otherwise."""
        try:
            await self.websocket.send_json(message)
            return True
        except Exception:
            # mark as closed / failed; caller (manager) will remove it
            self.open = False
            return False

    async def receive_text(self) -> str:
        return await self.websocket.receive_text()

    def __hash__(self) -> int:
        # Use the underlying websocket identity for set membership
        return hash(self.websocket)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Connection) and other.websocket == self.websocket


class ConnectionManager:
    """Simple in-memory WebSocket connection manager using Connection objects."""

    def __init__(self) -> None:
        self.active_connections: Set[Connection] = set()

    async def connect(self, websocket: WebSocket) -> Connection:
        conn = Connection(websocket)
        await conn.accept()
        self.active_connections.add(conn)
        return conn

    def disconnect(self, conn: Connection) -> None:
        self.active_connections.discard(conn)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        # Send to a copy to avoid mutation during iteration
        dead: Set[Connection] = set()
        for conn in list(self.active_connections):
            ok = await conn.send_json(message)
            if not ok:
                dead.add(conn)
        for conn in dead:
            self.disconnect(conn)


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
    # Notify subscribers about the new node only
    await manager.broadcast({"event": "node_added", "node": payload.node})
    return {"status": "ok", "node": payload.node}


@app.post("/edges")
async def add_edge(payload: EdgeIn):
    builder.add_edge(payload.from_node, payload.to_node)
    # Notify subscribers about the new edge only
    await manager.broadcast({
        "event": "edge_added",
        "from": payload.from_node,
        "to": payload.to_node,
    })
    return {"status": "ok", "from": payload.from_node, "to": payload.to_node}


@app.delete("/graph")
async def reset_graph():
    global builder
    builder = SimpleGraphBuilder()
    # Notify subscribers that the graph has been reset (no payload needed)
    await manager.broadcast({"event": "graph_reset"})
    return {"status": "ok", "message": "graph reset"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept and register the connection via the Connection abstraction
    conn = await manager.connect(websocket)
    # Send the current graph immediately upon connection
    try:
        await conn.send_json({"event": "graph_init", "graph": builder.get_graph()})
        while True:
            # Keep the connection open; ignore any incoming messages
            await conn.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(conn)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Ensure background worker is stopped when the app shuts down."""
    global grow_task
    if grow_task is not None:
        grow_task.cancel()
        try:
            await grow_task
        except asyncio.CancelledError:
            pass
        grow_task = None
