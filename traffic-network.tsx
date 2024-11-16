"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

// Custom network layout matching the SUMO simulation
const JUNCTION_COORDINATES = {
  1: { x: 100, y: 50 },
  2: { x: 300, y: 50 },
  3: { x: 500, y: 50 },
  4: { x: 100, y: 250 },
  5: { x: 300, y: 250 },
  6: { x: 500, y: 250 },
  7: { x: 700, y: 250 },
  8: { x: 100, y: 450 },
  9: { x: 300, y: 450 },
  10: { x: 500, y: 450 }
}

const CONNECTIONS = [
  [1, 2], [2, 3],
  [1, 4], [2, 5], [3, 6], [6, 7],
  [4, 8], [5, 9], [6, 10],
  [8, 9], [9, 10],
  [4, 5], [5, 6]
]

interface JunctionProps {
  id: number
  x: number
  y: number
  congestion: number
  signalTiming: number
  onClick: () => void
}

function Junction({ id, x, y, congestion, signalTiming, onClick }: JunctionProps) {
  const color = congestion > 0.7 ? "bg-red-500" : 
                congestion > 0.4 ? "bg-yellow-500" : "bg-green-500"
  
  return (
    <div 
      className={`absolute w-12 h-12 ${color} rounded-full flex items-center justify-center cursor-pointer
                  transform -translate-x-1/2 -translate-y-1/2 border-2 border-white transition-colors
                  hover:ring-2 hover:ring-primary`}
      style={{ left: x, top: y }}
      onClick={onClick}
    >
      <span className="text-white font-bold">{id}</span>
    </div>
  )
}

export default function Component() {
  const [selectedJunction, setSelectedJunction] = useState<number | null>(null)
  const [congestionLevels, setCongestionLevels] = useState<Record<number, number>>({})
  const [signalTimings, setSignalTimings] = useState<Record<number, number>>({})

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      const newCongestion: Record<number, number> = {}
      const newTimings: Record<number, number> = {}
      
      Object.keys(JUNCTION_COORDINATES).forEach(id => {
        const junctionId = parseInt(id)
        const congestion = Math.random()
        newCongestion[junctionId] = congestion
        
        // Dynamic signal timing based on congestion
        newTimings[junctionId] = congestion > 0.7 ? 60 :
                                congestion > 0.4 ? 45 : 30
      })
      
      setCongestionLevels(newCongestion)
      setSignalTimings(newTimings)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Dynamic Traffic Network Simulation</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative w-full h-[600px] bg-muted/20 rounded-lg overflow-hidden">
          {/* Draw connections */}
          <svg className="absolute inset-0 w-full h-full">
            {CONNECTIONS.map(([from, to], idx) => {
              const fromCoord = JUNCTION_COORDINATES[from]
              const toCoord = JUNCTION_COORDINATES[to]
              return (
                <line
                  key={idx}
                  x1={fromCoord.x}
                  y1={fromCoord.y}
                  x2={toCoord.x}
                  y2={toCoord.y}
                  stroke="black"
                  strokeWidth="4"
                />
              )
            })}
          </svg>
          
          {/* Draw junctions */}
          {Object.entries(JUNCTION_COORDINATES).map(([id, coord]) => (
            <Junction
              key={id}
              id={parseInt(id)}
              x={coord.x}
              y={coord.y}
              congestion={congestionLevels[parseInt(id)] || 0}
              signalTiming={signalTimings[parseInt(id)] || 30}
              onClick={() => setSelectedJunction(parseInt(id))}
            />
          ))}
          
          {/* Junction details popup */}
          {selectedJunction && (
            <div className="absolute bottom-4 left-4 bg-white p-4 rounded-lg shadow-lg">
              <h3 className="font-bold mb-2">Junction {selectedJunction}</h3>
              <p>Congestion: {(congestionLevels[selectedJunction] * 100).toFixed(1)}%</p>
              <p>Signal Timing: {signalTimings[selectedJunction]}s</p>
              <button 
                onClick={() => setSelectedJunction(null)}
                className="mt-2 px-2 py-1 bg-primary text-primary-foreground rounded hover:bg-primary/90"
              >
                Close
              </button>
            </div>
          )}
          
          {/* Legend */}
          <div className="absolute top-4 right-4 bg-white p-4 rounded-lg shadow-lg">
            <h4 className="font-bold mb-2">Congestion Levels</h4>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-green-500 rounded-full" />
                <span>Low (&lt;40%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-yellow-500 rounded-full" />
                <span>Medium (40-70%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-red-500 rounded-full" />
                <span>High (&gt;70%)</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}