 # Realtime Graph Builder

 A minimal full-stack project that builds and evolves a directed graph in the backend and streams live graph updates to the frontend over WebSockets. The frontend renders the graph and updates it in real time as new nodes/edges arrive.

 ## Overview
 - Backend: FastAPI app maintaining an in-memory graph and exposing:
   - REST endpoints to read/modify the graph
   - a WebSocket that pushes incremental updates (node/edge events)
 - Frontend: React app using Graphology + Sigma to visualize the graph and apply updates live.

 ## Architecture
 - Graph state lives in the backend (in-memory), via a simple adjacency list builder.
 - On startup, the backend seeds a small demo graph and launches a background task that periodically adds nodes/edges.
 - Clients connect to the backend WebSocket to receive events like "node_added" and "edge_added" and update the visualization accordingly.
```
     +-----------+        REST (HTTP)         +-----------+
     |           |  <-----------------------> |           |
     | Frontend  |                            |  Backend  |
     |  React +  |        WebSocket           |  FastAPI  |
     | Sigma     |  <-----------------------> |           |
     +-----------+        (stream updates)    +-----------+

```
 ## Getting Started

 ### Prerequisites
 - Backend: Python 3.11+ (managed via uv/uvicorn recommended)
 - Frontend: Node.js 18+ and pnpm/npm/yarn

 ### Backend
 Location: backend/

 Key files:
 - backend/main.py — FastAPI app with REST + WebSocket and a background graph grower
 - backend/graph_builder/ — simple in-memory graph builder implementation(s)

 Install dependencies and run (with uv):

     cd backend
     uv sync
     uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

 Alternatively with pip + uvicorn:

     pip install -r requirements.txt  # if you maintain one, or use pyproject via uv/pip-tools
     uvicorn main:app --reload --host 0.0.0.0 --port 8000

 REST endpoints (from main.py):
 - GET /graph — returns the current graph as an adjacency list
 - POST /node — body { "node": "ID" } to add a node
 - POST /edge — body { "source": "A", "target": "B" } to add a directed edge A→B
 - POST /reset — reset to an empty graph

 WebSocket:
 - GET /ws — clients connect and receive JSON events:
   - { "event": "node_added", "node": "N" }
   - { "event": "edge_added", "from": "A", "to": "B" }

 ### Frontend
 Location: frontend/

 The app connects to the backend WebSocket and keeps a Graphology graph in sync, rendered by Sigma.

 Install and run (example with npm):

     cd frontend
     npm install
     npm run dev

 Visit the printed local URL (e.g., http://localhost:5173). Ensure the backend is running at http://localhost:8000.

 WebSocket URL
 - By default, the frontend expects ws://localhost:8000/ws (adjust if you proxy or deploy differently).

 ## Development Notes
 - The backend seeds a small demo graph on startup and then periodically adds nodes/edges in a background task to showcase streaming updates.
 - The in-memory graph builder is intentionally simple; replace it with a persistent or distributed store if needed.
