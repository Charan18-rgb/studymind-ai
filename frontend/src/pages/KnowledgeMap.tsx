import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Network,
  AlertCircle,
  CheckCircle,
  Zap,
  ArrowRight,
  Sparkles,
  Layers,
  LayoutGrid,
} from 'lucide-react'
import { api, GraphNode, GraphEdge, AdaptiveExplanation } from '@/lib/api'

export default function KnowledgeMap() {
  const navigate = useNavigate()
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [explanation, setExplanation] = useState<AdaptiveExplanation | null>(null)
  const [loadingExp, setLoadingExp] = useState(false)
  const [viewMode, setViewMode] = useState<'graph' | 'grid'>('graph')

  useEffect(() => {
    const requestedId = Number(new URLSearchParams(window.location.search).get('concept'))
    loadGraph(Number.isFinite(requestedId) && requestedId > 0 ? requestedId : undefined)
  }, [])

  const loadGraph = async (preferredConceptId?: number) => {
    setLoading(true)
    try {
      const data = await api.getKnowledgeGraph()
      setNodes(data.nodes || [])
      setEdges(data.edges || [])
      if (data.nodes && data.nodes.length > 0) {
        // Select the weakest topic by default or first node
        const preferred = data.nodes.find((node) => node.id === preferredConceptId)
        const weakest = [...data.nodes].sort((a, b) => a.mastery - b.mastery)[0]
        selectConcept(preferred || weakest || data.nodes[0])
      }
    } catch (err) {
      console.error('Failed to load knowledge graph:', err)
    } finally {
      setLoading(false)
    }
  }

  const selectConcept = async (node: GraphNode) => {
    setSelectedNode(node)
    setLoadingExp(true)
    try {
      const exp = await api.getAdaptiveExplanation(node.id)
      setExplanation(exp)
    } catch (err) {
      console.error('Failed to load explanation:', err)
      setExplanation(null)
    } finally {
      setLoadingExp(false)
    }
  }

  const getNodeColor = (status: string, mastery: number) => {
    if (mastery >= 80 || status === 'mastered') return { bg: 'bg-emerald-500', text: 'text-emerald-300', border: 'border-emerald-400', light: 'bg-emerald-500/10' }
    if (mastery >= 60 || status === 'proficient') return { bg: 'bg-blue-500', text: 'text-blue-300', border: 'border-blue-400', light: 'bg-blue-500/10' }
    if (mastery >= 40 || status === 'developing') return { bg: 'bg-amber-500', text: 'text-amber-300', border: 'border-amber-400', light: 'bg-amber-500/10' }
    if (mastery > 0 || status === 'needs_foundation') return { bg: 'bg-rose-500', text: 'text-rose-300', border: 'border-rose-400', light: 'bg-rose-500/10' }
    return { bg: 'bg-slate-400', text: 'text-slate-300', border: 'border-slate-400', light: 'bg-slate-400/10' }
  }

  // Pre-calculated node coordinates on SVG canvas for balanced layout
  const getNodeCoordinates = (index: number, total: number) => {
    const layoutCoords: Record<string, { x: number; y: number }> = {
      Arrays: { x: 120, y: 100 },
      'Linked Lists': { x: 300, y: 100 },
      Stacks: { x: 120, y: 260 },
      Queues: { x: 300, y: 260 },
      Recursion: { x: 500, y: 100 },
      Trees: { x: 500, y: 260 },
      Graphs: { x: 700, y: 180 },
    }

    const nodeName = nodes[index]?.name
    if (nodeName && layoutCoords[nodeName]) {
      return layoutCoords[nodeName]
    }

    // Default radial fallback
    const angle = (index / total) * 2 * Math.PI - Math.PI / 2
    const rx = 320
    const ry = 140
    return {
      x: 420 + rx * Math.cos(angle),
      y: 200 + ry * Math.sin(angle),
    }
  }

  const getPrerequisitesForSelected = () => {
    if (!selectedNode) return []
    const prereqEdges = edges.filter(
      (e) => e.target === selectedNode.id && e.relationship === 'prerequisite'
    )
    return prereqEdges.map((e) => {
      const sourceNode = nodes.find((n) => n.id === e.source)
      return {
        id: e.source,
        name: sourceNode?.name || `Concept #${e.source}`,
        mastery: sourceNode?.mastery ?? 0,
        status: sourceNode?.status || 'unknown',
      }
    })
  }

  const prereqs = getPrerequisitesForSelected()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Interactive Knowledge Map</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Structural concept hierarchy and prerequisites connected with your live learner mastery model.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'graph' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('graph')}
            className="gap-1.5"
          >
            <Network className="w-4 h-4" />
            Graph View
          </Button>
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
            className="gap-1.5"
          >
            <LayoutGrid className="w-4 h-4" />
            List / Card View
          </Button>
        </div>
      </div>

      {/* Legend */}
      <Card className="bg-card/50">
        <CardContent className="p-3.5">
          <div className="flex flex-wrap items-center justify-between gap-4 text-xs font-medium">
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-emerald-400/30" />
              <span>Mastered (80%+)</span>
            </div>
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-blue-500 ring-2 ring-blue-400/30" />
              <span>Proficient (60-79%)</span>
            </div>
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500 ring-2 ring-amber-400/30" />
              <span>Developing (40-59%)</span>
            </div>
            <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-rose-500 ring-2 ring-rose-400/30" />
              <span>Needs Attention (&lt;40%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 border-b-2 border-dashed border-rose-400" />
              <span className="text-muted-foreground">Dashed arrow points from prerequisite to dependent concept</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Grid: Graph on Left, Interactive Detail Panel on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Visual Graph / Cards */}
        <div className="lg:col-span-7 xl:col-span-8 space-y-4">
          {viewMode === 'graph' ? (
            <Card className="overflow-hidden border-2 shadow-sm">
              <CardHeader className="py-3 px-4 bg-muted/30 border-b flex flex-row items-center justify-between">
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Network className="w-4 h-4 text-primary" />
                  Concept Network & Prerequisites
                </CardTitle>
                <span className="text-xs text-muted-foreground">Click any node to inspect & practice</span>
              </CardHeader>
              <CardContent className="p-0">
                {loading ? (
                  <div className="h-[460px] flex items-center justify-center text-muted-foreground animate-pulse">
                    Building your knowledge map...
                  </div>
                ) : (
                  <div className="map-grid relative w-full h-[460px] overflow-x-auto">
                    <svg
                      viewBox="0 0 840 400"
                      className="w-full h-full min-w-[700px] select-none"
                    >
                      <defs>
                        <filter id="node-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="8" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
                        <radialGradient id="node-sheen" cx="30%" cy="25%"><stop offset="0%" stopColor="#ffffff" stopOpacity=".32" /><stop offset="100%" stopColor="#ffffff" stopOpacity="0" /></radialGradient>
                        <marker
                          id="arrow-prereq"
                          viewBox="0 0 10 10"
                          refX="26"
                          refY="5"
                          markerWidth="6"
                          markerHeight="6"
                          orient="auto-start-reverse"
                        >
                          <path d="M 0 1 L 10 5 L 0 9 z" fill="#f43f5e" />
                        </marker>
                        <marker
                          id="arrow-related"
                          viewBox="0 0 10 10"
                          refX="24"
                          refY="5"
                          markerWidth="5"
                          markerHeight="5"
                          orient="auto-start-reverse"
                        >
                          <path d="M 0 1 L 10 5 L 0 9 z" fill="#94a3b8" />
                        </marker>
                      </defs>

                      {/* Edges */}
                      {edges.map((edge, idx) => {
                        const sIdx = nodes.findIndex((n) => n.id === edge.source)
                        const tIdx = nodes.findIndex((n) => n.id === edge.target)
                        if (sIdx === -1 || tIdx === -1) return null

                        const sourcePos = getNodeCoordinates(sIdx, nodes.length)
                        const targetPos = getNodeCoordinates(tIdx, nodes.length)
                        const isPrereq = edge.relationship === 'prerequisite'

                        return (
                          <g key={idx}>
                            <line
                              x1={sourcePos.x}
                              y1={sourcePos.y}
                              x2={targetPos.x}
                              y2={targetPos.y}
                              stroke={isPrereq ? '#f43f5e' : '#94a3b8'}
                              strokeWidth={isPrereq ? 2.5 : 1.5}
                              strokeDasharray={isPrereq ? '5,4' : undefined}
                              markerEnd={isPrereq ? 'url(#arrow-prereq)' : 'url(#arrow-related)'}
                              className={isPrereq ? 'map-edge transition-all duration-300 opacity-85' : 'transition-all duration-300 opacity-55'}
                            />
                            {/* Midpoint Label for Prerequisite */}
                            {isPrereq && (
                              <text
                                x={(sourcePos.x + targetPos.x) / 2}
                                y={(sourcePos.y + targetPos.y) / 2 - 6}
                                textAnchor="middle"
                                className="fill-rose-500 text-[10px] font-semibold bg-white"
                              >
                                prerequisite
                              </text>
                            )}
                          </g>
                        )
                      })}

                      {/* Nodes */}
                      {nodes.map((node, idx) => {
                        const pos = getNodeCoordinates(idx, nodes.length)
                        const color = getNodeColor(node.status, node.mastery)
                        const isSelected = selectedNode?.id === node.id

                        return (
                          <g
                            key={node.id}
                            transform={`translate(${pos.x}, ${pos.y})`}
                            onClick={() => selectConcept(node)}
                            role="button"
                            tabIndex={0}
                            aria-label={`${node.name}, ${Math.round(node.mastery)} percent mastery`}
                            onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectConcept(node) } }}
                            className={`map-node cursor-pointer ${isSelected ? 'map-node-selected' : ''}`}
                          >
                            {/* Selected highlight ring */}
                            {isSelected && (
                              <circle
                                r="36"
                                fill="none"
                                stroke="#6366f1"
                                strokeWidth="3"
                                strokeDasharray="4,3"
                                className="opacity-80"
                              />
                            )}

                            {/* Node circle */}
                            <circle
                              r="28"
                              className={`${color.bg} transition-all`}
                              stroke={isSelected ? '#8ce8ff' : 'rgb(255 255 255 / 46%)'}
                              strokeWidth={isSelected ? 3 : 1.5}
                              filter={isSelected ? 'url(#node-glow)' : undefined}
                            />
                            <circle r="27" fill="url(#node-sheen)" pointerEvents="none" />

                            {/* Inner score */}
                            <text
                              textAnchor="middle"
                              dy="-2"
                              className="fill-white font-bold text-xs pointer-events-none"
                            >
                              {Math.round(node.mastery)}%
                            </text>
                            <text
                              textAnchor="middle"
                              dy="11"
                              className="fill-white/80 font-medium text-[9px] pointer-events-none uppercase"
                            >
                              {node.difficulty || 'med'}
                            </text>

                            {/* Node name under node */}
                            <text
                              textAnchor="middle"
                              dy="44"
                              className={`text-xs font-semibold select-none ${
                                isSelected ? 'fill-cyan-200 font-bold text-sm' : 'fill-slate-100'
                              }`}
                            >
                              {node.name}
                            </text>

                            {/* Warning alert if needs foundation */}
                            {node.mastery < 50 && (
                              <g transform="translate(16, -26)">
                                <circle r="9" fill="#f43f5e" />
                                <text
                                  textAnchor="middle"
                                  dy="3"
                                  className="fill-white font-black text-[10px]"
                                >
                                  !
                                </text>
                              </g>
                            )}
                          </g>
                        )
                      })}
                    </svg>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            /* Responsive Grid / Cards Fallback */
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {nodes.map((node) => {
                const color = getNodeColor(node.status, node.mastery)
                const isSelected = selectedNode?.id === node.id

                return (
                  <Card
                    key={node.id}
                    onClick={() => selectConcept(node)}
                    className={`cursor-pointer transition-all hover:border-primary ${
                      isSelected ? 'border-2 border-primary bg-primary/[0.03]' : ''
                    }`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div>
                          <h4 className="font-semibold text-base">{node.name}</h4>
                          <p className="text-xs text-muted-foreground line-clamp-1">
                            {node.description || 'Core study concept'}
                          </p>
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded text-xs font-bold text-white ${color.bg}`}
                        >
                          {Math.round(node.mastery)}%
                        </span>
                      </div>
                      <Progress value={node.mastery} className="h-1.5 mb-2" />
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="capitalize">{node.status.replace('_', ' ')}</span>
                        <span>{node.accuracy ? `${Math.round(node.accuracy)}% acc` : '0 attempts'}</span>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </div>

        {/* Right Column: Concept Deep Dive & Adaptive Action Drawer */}
        <div className="lg:col-span-5 xl:col-span-4">
          {selectedNode ? (
            <Card className="ambient-panel border-white/10 shadow-xl">
              <CardHeader className="bg-white/[0.025] pb-3 border-b border-white/10">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Badge
                      variant={
                        selectedNode.mastery >= 80
                          ? 'default'
                          : selectedNode.mastery < 40
                          ? 'destructive'
                          : 'secondary'
                      }
                      className="mb-1.5"
                    >
                      {selectedNode.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <CardTitle className="text-2xl font-bold">{selectedNode.name}</CardTitle>
                  </div>
                  <div className="text-right">
                    <span className="text-2xl font-extrabold text-primary">
                      {Math.round(selectedNode.mastery)}%
                    </span>
                    <p className="text-[11px] text-muted-foreground">Mastery Score</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">{selectedNode.description}</p>
              </CardHeader>

              <CardContent className="p-5 space-y-5">
                {/* Accuracy & Attempts stats */}
                <div className="grid grid-cols-2 gap-3 p-3 bg-muted/40 rounded-lg text-center">
                  <div>
                    <span className="text-xs text-muted-foreground block">Historical Accuracy</span>
                    <span className="text-base font-bold text-foreground">
                      {selectedNode.accuracy ? `${Math.round(selectedNode.accuracy)}%` : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-muted-foreground block">Practice Attempts</span>
                    <span className="text-base font-bold text-foreground">
                      {selectedNode.correct_attempts ?? 0} / {selectedNode.total_attempts ?? 0}
                    </span>
                  </div>
                </div>

                {/* Prerequisites Check */}
                <div>
                  <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5" />
                    Prerequisites & Dependencies
                  </h4>
                  {prereqs.length > 0 ? (
                    <div className="space-y-1.5">
                      {prereqs.map((p) => (
                        <div
                          key={p.id}
                          className="flex items-center justify-between p-2 rounded bg-muted/30 text-xs border"
                        >
                          <div className="flex items-center gap-2">
                            {p.mastery >= 60 ? (
                              <CheckCircle className="w-4 h-4 text-emerald-500" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-amber-500" />
                            )}
                            <span className="font-medium">{p.name}</span>
                          </div>
                          <Badge variant={p.mastery >= 60 ? 'outline' : 'destructive'} className="text-[10px]">
                            {Math.round(p.mastery)}% mastery
                          </Badge>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground italic">No prerequisites required.</p>
                  )}
                </div>

                {/* Adaptive Explanation Section */}
                <div className="space-y-3 pt-2 border-t">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-primary" />
                      Adaptive Explanation
                    </h4>
                    {explanation?.level_label && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary font-medium">
                        {explanation.level_label}
                      </span>
                    )}
                  </div>

                  {loadingExp ? (
                    <div className="p-4 text-xs text-muted-foreground animate-pulse">
                      Generating tailored explanation...
                    </div>
                  ) : explanation ? (
                    <div className="space-y-2.5 text-xs text-foreground/90">
                      <p className="p-2.5 bg-primary/5 rounded border border-primary/10 leading-relaxed">
                        {explanation.simple_explanation}
                      </p>

                      {explanation.real_world_analogy && (
                        <div className="p-2.5 bg-blue-50/50 dark:bg-blue-950/20 rounded border border-blue-200/50 text-blue-900 dark:text-blue-200">
                          <span className="font-semibold block mb-0.5">💡 Analogy:</span>
                          {explanation.real_world_analogy}
                        </div>
                      )}

                      {explanation.common_mistakes && explanation.common_mistakes.length > 0 && (
                        <div className="p-2.5 bg-rose-50/50 dark:bg-rose-950/20 rounded border border-rose-200/50 text-rose-900 dark:text-rose-200">
                          <span className="font-semibold block mb-0.5">⚠️ Common Pitfall:</span>
                          {explanation.common_mistakes[0]}
                        </div>
                      )}
                    </div>
                  ) : null}
                </div>

                {/* Targeted Action Buttons */}
                <div className="pt-3 space-y-2">
                  <Button
                    className="w-full gap-2 shadow"
                    size="lg"
                    onClick={() => navigate('/adaptive-practice')}
                  >
                    <Zap className="w-4 h-4" />
                    Practice {selectedNode.name}
                    <ArrowRight className="w-4 h-4 ml-auto" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="h-full flex items-center justify-center p-8 text-center text-muted-foreground">
              <div>
                <Network className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Select a concept from the knowledge graph to view details and adaptive guidance.</p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
