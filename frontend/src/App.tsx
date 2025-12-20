import { useRef, useEffect } from 'react'
import './App.css'
import Graph from 'graphology'
import Sigma from 'sigma'

function App() {
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const graph = new Graph()
    graph.addNode('1', { label: 'Node 1', x: 0, y: 0, size: 10, color: 'blue' })
    graph.addNode('2', { label: 'Node 2', x: 1, y: 1, size: 20, color: 'red' })
    graph.addEdge('1', '2', { size: 5, color: 'purple' })

    let sigmaInstance: any = null
    if (containerRef.current) {
      sigmaInstance = new Sigma(graph, containerRef.current)
    }

    return () => {
      if (sigmaInstance && typeof sigmaInstance.kill === 'function') sigmaInstance.kill()
    }
  }, [])

  return (
    <>
      {/* container for sigma: fixed full-screen so it fills the viewport */}
      <div
        ref={containerRef}
        id="container"
      />
    </>
  )
}

export default App
