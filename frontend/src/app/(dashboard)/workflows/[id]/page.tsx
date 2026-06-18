"use client"
import { useEffect, useState, useCallback, useRef } from "react"
import { api } from "@/lib/api"
import { useParams, useRouter } from "next/navigation"
import {
  ReactFlow, addEdge, applyNodeChanges, applyEdgeChanges,
  Node, Edge, Background, Controls, MiniMap, useNodesState, useEdgesState,
} from "reactflow"
import "reactflow/dist/style.css"
import { Play, BarChart3, Lightbulb, Plus, X } from "lucide-react"

const taskTypeColors: Record<string, string> = {
  python: "#6366f1",
  http: "#22c55e",
  simulate: "#f59e0b",
  file: "#ef4444",
}

export default function WorkflowDetail() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const [wf, setWf] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [suggestions, setSuggestions] = useState<any[]>([])
  const [executing, setExecuting] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [showNewTask, setShowNewTask] = useState(false)
  const [taskName, setTaskName] = useState("")
  const [taskType, setTaskType] = useState("simulate")

  useEffect(() => {
    api.getWorkflow(id).then(wf => {
      setWf(wf)
      setNodes(wf.tasks.map((t: any) => ({
        id: t.id,
        type: "default",
        position: { x: t.position_x || 100, y: t.position_y || 100 },
        data: {
          label: (
            <div className="text-xs">
              <div className="font-semibold">{t.name}</div>
              <div className="text-gray-400">{t.task_type}</div>
            </div>
          ),
        },
        style: {
          background: taskTypeColors[t.task_type] || "#6366f1",
          color: "#fff",
          border: "none",
          borderRadius: 8,
          padding: "8px 16px",
          minWidth: 140,
        },
      })))
      setEdges(wf.edges.map((e: any) => ({
        id: e.id,
        source: e.source_task_id,
        target: e.target_task_id,
        animated: true,
        style: { stroke: "#94a3b8", strokeWidth: 2 },
      })))
    }).catch(() => router.push("/workflows"))
    api.getWorkflowRuns(id).then((r: any) => setRuns(r as any[])).catch(() => {})
    api.getSuggestions(id).then((s: any) => setSuggestions(s as any[])).catch(() => {})
  }, [id, router])

  const onConnect = useCallback((params: any) => {
    setEdges(eds => addEdge({ ...params, animated: true, style: { stroke: "#94a3b8", strokeWidth: 2 } }, eds))
  }, [setEdges])

  async function handleExecute() {
    setExecuting(true)
    try {
      const run = await api.executeWorkflow(id)
      router.push(`/runs/${run.id}`)
    } catch (err) { console.error(err) }
    setExecuting(false)
  }

  async function handleAnalyze() {
    setAnalyzing(true)
    try {
      const suggestions = await api.analyzeWorkflow(id, runs[0]?.id)
      setSuggestions(suggestions)
    } catch (err) { console.error(err) }
    setAnalyzing(false)
  }

  async function handleAddTask(e: React.FormEvent) {
    e.preventDefault()
    if (!taskName.trim()) return
    try {
      const currentWf = await api.getWorkflow(id)
      const newTask = {
        name: taskName,
        task_type: taskType,
        config: { code: "# Add your Python code here\nresult = 'hello'" },
        position_x: 100 + (currentWf.tasks?.length || 0) * 220,
        position_y: 300,
      }
      await api.createWorkflow({
        name: currentWf.name,
        tasks: [...(currentWf.tasks || []), newTask],
        edges: currentWf.edges || [],
      })
      setTaskName("")
      setShowNewTask(false)
      window.location.reload()
    } catch (err) { console.error(err) }
  }

  async function handleApplySuggestion(suggestionId: string) {
    try {
      await api.applyOptimization(suggestionId)
      setSuggestions(prev => prev.map(s => s.id === suggestionId ? { ...s, applied: true, status: "applied" } : s))
    } catch (err) { console.error(err) }
  }

  if (!wf) return <div className="flex h-64 items-center justify-center text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">{wf.name}</h2>
          {wf.description && <p className="text-sm text-gray-500">{wf.description}</p>}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowNewTask(true)}
            className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition"
          >
            <Plus className="h-3 w-3" /> Add Task
          </button>
          <button
            onClick={handleAnalyze} disabled={analyzing}
            className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium text-amber-600 hover:bg-amber-50 transition"
          >
            <Lightbulb className="h-3 w-3" /> {analyzing ? "Analyzing..." : "Analyze"}
          </button>
          <button
            onClick={handleExecute} disabled={executing}
            className="flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 transition"
          >
            <Play className="h-3 w-3" /> {executing ? "Running..." : "Execute"}
          </button>
        </div>
      </div>

      {showNewTask && (
        <form onSubmit={handleAddTask} className="rounded-xl border bg-white p-4 space-y-3">
          <div className="flex gap-3">
            <input
              type="text" placeholder="Task name" required
              value={taskName} onChange={e => setTaskName(e.target.value)}
              className="flex-1 rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            />
            <select
              value={taskType} onChange={e => setTaskType(e.target.value)}
              className="rounded-lg border px-4 py-2 text-sm"
            >
              <option value="simulate">Simulate</option>
              <option value="python">Python</option>
              <option value="http">HTTP</option>
            </select>
            <button type="submit" className="rounded-lg bg-indigo-600 px-4 py-2 text-sm text-white">Add</button>
            <button type="button" onClick={() => setShowNewTask(false)} className="text-gray-400 hover:text-gray-600">
              <X className="h-5 w-5" />
            </button>
          </div>
        </form>
      )}

      <div className="h-[400px] rounded-xl border bg-white">
        <ReactFlow
          nodes={nodes} edges={edges}
          onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-xl border bg-white">
          <div className="border-b px-4 py-3">
            <h3 className="font-semibold text-sm">Run History</h3>
          </div>
          <div className="divide-y text-sm">
            {runs.slice(0, 10).map(run => (
              <div
                key={run.id}
                onClick={() => router.push(`/runs/${run.id}`)}
                className="px-4 py-2.5 flex items-center justify-between hover:bg-gray-50 cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${
                    run.status === "completed" ? "bg-green-500" :
                    run.status === "failed" ? "bg-red-500" :
                    run.status === "running" ? "bg-blue-500" : "bg-yellow-500"
                  }`} />
                  <span>{run.status}</span>
                </div>
                <span className="text-gray-400">{run.total_duration_ms ? `${run.total_duration_ms.toFixed(0)}ms` : "—"}</span>
              </div>
            ))}
            {runs.length === 0 && <p className="px-4 py-6 text-center text-gray-400">No runs yet</p>}
          </div>
        </div>

        <div className="rounded-xl border bg-white">
          <div className="border-b px-4 py-3 flex justify-between items-center">
            <h3 className="font-semibold text-sm">Optimization Suggestions</h3>
            <button onClick={handleAnalyze} className="text-xs text-indigo-600 hover:underline">
              Refresh
            </button>
          </div>
          <div className="divide-y text-sm">
            {suggestions.map(s => (
              <div key={s.id} className="px-4 py-3">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="inline-block rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 mb-1">
                      {s.suggestion_type}
                    </span>
                    <p className="font-medium">{s.title}</p>
                    {s.description && <p className="text-xs text-gray-500 mt-0.5">{s.description}</p>}
                    {s.estimated_improvement_pct && (
                      <p className="text-xs text-green-600 mt-0.5">
                        Est. {s.estimated_improvement_pct}% improvement
                      </p>
                    )}
                  </div>
                  <div className="flex gap-1 ml-2">
                    {!s.applied && s.status !== "applied" ? (
                      <button
                        onClick={() => handleApplySuggestion(s.id)}
                        className="rounded bg-indigo-600 px-2 py-1 text-xs text-white hover:bg-indigo-700"
                      >
                        Apply
                      </button>
                    ) : (
                      <span className="rounded bg-green-100 px-2 py-1 text-xs text-green-700">
                        Applied
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {suggestions.length === 0 && (
              <p className="px-4 py-6 text-center text-gray-400">
                Run the workflow and click Analyze for suggestions
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
