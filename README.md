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

- For backend setup, installation, running, and development instructions, see:
  - backend/README.md

- For frontend setup, installation, running, and development instructions, see:
  - frontend/README.md

## Development Notes

- The backend seeds a small demo graph on startup and then periodically adds nodes/edges in a background task to showcase streaming updates.
- The in-memory graph builder is intentionally simple; replace it with a persistent or distributed store if needed.
