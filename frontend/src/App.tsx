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

function App() {
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Start with an empty graph
    const initial = new Graph()
    let sigmaInstance: Sigma | null = null
    let ws: WebSocket | null = null

    if (containerRef.current) {
      sigmaInstance = new Sigma(initial, containerRef.current)
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
            const g = buildGraphFromAdj(graphData)
            // Replace the current graph in Sigma
            // @ts-ignore (sigma types may not include setGraph depending on version)
            if (typeof (sigmaInstance as any).setGraph === 'function') {
              ;(sigmaInstance as any).setGraph(g)
            } else {
              // Fallback: kill and recreate
              sigmaInstance.kill()
              if (containerRef.current) {
                sigmaInstance = new Sigma(g, containerRef.current)
              }
            }
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
