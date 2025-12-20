import { useRef, useEffect } from 'react'
import './App.css'
import Graph from 'graphology'
import Sigma from 'sigma'

type AdjList = Record<string, string[]>

function buildGraphFromAdj(adj: AdjList): Graph {
  const g = new Graph({ allowSelfLoops: false, multi: false })

  const nodes = Object.keys(adj)
  const n = nodes.length || 1

  // Place nodes on a circle for a simple layout
  nodes.forEach((key, i) => {
    const angle = (i / n) * Math.PI * 2
    const x = Math.cos(angle)
    const y = Math.sin(angle)
    if (!g.hasNode(key)) {
      g.addNode(key, {
        label: String(key),
        x,
        y,
        size: 8,
        color: '#4f46e5',
      })
    }
  })

  // Ensure neighbors also exist as nodes
  nodes.forEach((from) => {
    const neighbors = adj[from] || []
    neighbors.forEach((to) => {
      if (!g.hasNode(to)) {
        g.addNode(to, {
          label: String(to),
          x: Math.random() * 2 - 1,
          y: Math.random() * 2 - 1,
          size: 8,
          color: '#4f46e5',
        })
      }
    })
  })

  // Add edges (directed as provided)
  nodes.forEach((from) => {
    const neighbors = adj[from] || []
    neighbors.forEach((to, idx) => {
      const edgeKey = `${from}->${to}#${idx}`
      if (!g.hasEdge(from, to)) {
        g.addEdge(from, to, { size: 1, color: '#94a3b8', key: edgeKey })
      }
    })
  })

  return g
}

// Update an existing Graphology graph in-place to match the provided
// adjacency list. Keeps existing node positions/attributes when possible.
function updateGraphInPlace(graph: Graph, adj: AdjList): void {
  // 1) Compute desired node set (include keys and their neighbors)
  const desiredNodes = new Set<string>()
  Object.keys(adj).forEach((from) => {
    desiredNodes.add(from)
    for (const to of adj[from] || []) desiredNodes.add(to)
  })

  // 2) Remove nodes that should no longer exist
  graph.forEachNode((node) => {
    if (!desiredNodes.has(String(node))) {
      graph.dropNode(node)
    }
  })

  // 3) Add missing nodes (keep random/simple placement for newcomers)
  desiredNodes.forEach((node) => {
    if (!graph.hasNode(node)) {
      graph.addNode(node, {
        label: String(node),
        x: Math.random() * 2 - 1,
        y: Math.random() * 2 - 1,
        size: 8,
        color: '#4f46e5',
      })
    }
  })

  // 4) Build desired directed edges set
  const desiredEdges = new Set<string>()
  Object.keys(adj).forEach((from) => {
    const neighbors = adj[from] || []
    neighbors.forEach((to) => {
      desiredEdges.add(`${from}->${to}`)
      if (!graph.hasNode(from)) graph.addNode(from)
      if (!graph.hasNode(to)) graph.addNode(to)
      if (!graph.hasEdge(from, to)) {
        graph.addEdge(from, to, { size: 1, color: '#94a3b8' })
      }
    })
  })

  // 5) Remove edges that are no longer desired
  graph.forEachEdge((edgeKey, attributes, source, target) => {
    const key = `${String(source)}->${String(target)}`
    if (!desiredEdges.has(key)) {
      graph.dropEdge(edgeKey)
    }
  })
}

function App() {
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Start with an empty graph
    const graph = new Graph()
    let sigmaInstance: Sigma | null = null
    let ws: WebSocket | null = null

    if (containerRef.current) {
      sigmaInstance = new Sigma(graph, containerRef.current)
    }

    // Resolve backend WS URL
    const configured = (import.meta as any).env?.VITE_BACKEND_WS_URL as string | undefined
    const wsUrl = configured || 'ws://127.0.0.1:8000/ws'

    try {
      ws = new WebSocket(wsUrl)
    } catch (e) {
      console.error('Failed to create WebSocket', e)
    }

    const handleMessage = (evt: MessageEvent) => {
      try {
        const data = JSON.parse(evt.data)
        const event: string | undefined = data?.event
        const graphData: AdjList | undefined = data?.graph

        if (!sigmaInstance || !graphData) return

        switch (event) {
          case 'graph_init':
          case 'graph_update':
          case 'graph_reset': {
            // Update the current graph in-place instead of recreating it
            updateGraphInPlace((sigmaInstance as any).graph || graph, graphData)
            break
          }
          default:
            break
        }
      } catch (err) {
        console.error('Bad WS message', err)
      }
    }

    if (ws) {
      ws.addEventListener('open', () => console.log('WS connected'))
      ws.addEventListener('message', handleMessage)
      ws.addEventListener('close', () => console.log('WS disconnected'))
      ws.addEventListener('error', (e) => console.error('WS error', e))
    }

    return () => {
      try {
        if (ws && ws.readyState === WebSocket.OPEN) ws.close()
      } catch (_) {}
      if (sigmaInstance && typeof sigmaInstance.kill === 'function') sigmaInstance.kill()
    }
  }, [])

  return (
    <>
      <div
        ref={containerRef}
        id="container"
      />
    </>
  )
}

export default App
