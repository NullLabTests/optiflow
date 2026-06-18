"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { formatDuration } from "@/lib/utils"
import Link from "next/link"
import { Play, Plus, Zap, TrendingUp, Activity, Workflow } from "lucide-react"
import { useRouter } from "next/navigation"

interface Analytics {
  total_workflows: number
  total_runs: number
  total_task_executions: number
  successful_runs: number
  failed_runs: number
  success_rate: number
}

export default function DashboardHome() {
  const router = useRouter()
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [workflows, setWorkflows] = useState<Array<{ id: string; name: string; task_count: number }>>([])
  const [nlPrompt, setNlPrompt] = useState("")
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    api.getAnalyticsSummary().then(setAnalytics).catch(() => {})
    api.listWorkflows().then(setWorkflows).catch(() => {})
  }, [])

  async function handleNLCreate() {
    if (!nlPrompt.trim()) return
    setCreating(true)
    try {
      await api.createWorkflowFromNL(nlPrompt)
      setNlPrompt("")
      router.push("/workflows")
    } catch (e) {
      console.error(e)
    }
    setCreating(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Dashboard</h2>
        <Link
          href="/workflows"
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition"
        >
          <Plus className="h-4 w-4" /> New Workflow
        </Link>
      </div>

      <div className="rounded-xl border bg-white p-4">
        <div className="flex gap-2">
          <input
            value={nlPrompt}
            onChange={e => setNlPrompt(e.target.value)}
            placeholder="Describe a workflow in natural language... e.g., 'Fetch data from an API, transform it, then simulate processing'"
            className="flex-1 rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            onKeyDown={e => e.key === "Enter" && handleNLCreate()}
          />
          <button
            onClick={handleNLCreate}
            disabled={creating || !nlPrompt.trim()}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {creating ? "Creating..." : "Create with AI"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MetricCard icon={Workflow} label="Workflows" value={analytics?.total_workflows ?? "—"} />
        <MetricCard icon={Play} label="Total Runs" value={analytics?.total_runs ?? "—"} />
        <MetricCard icon={Activity} label="Task Executions" value={analytics?.total_task_executions ?? "—"} />
        <MetricCard icon={TrendingUp} label="Success Rate" value={analytics ? `${analytics.success_rate.toFixed(0)}%` : "—"} />
      </div>

      <div className="rounded-xl border bg-white">
        <div className="border-b px-6 py-4">
          <h3 className="font-semibold">Recent Workflows</h3>
        </div>
        <div className="divide-y">
          {workflows.slice(0, 5).map(wf => (
            <Link key={wf.id} href={`/workflows/${wf.id}`} className="flex items-center justify-between px-6 py-3 hover:bg-gray-50 transition">
              <span className="font-medium">{wf.name}</span>
              <span className="text-sm text-gray-500">{wf.task_count} tasks</span>
            </Link>
          ))}
          {workflows.length === 0 && (
            <p className="px-6 py-8 text-center text-sm text-gray-400">
              No workflows yet. Create one with AI above or go to Workflows.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function MetricCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-indigo-50 p-2">
          <Icon className="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <p className="text-xs text-gray-500">{label}</p>
          <p className="text-xl font-bold">{value}</p>
        </div>
      </div>
    </div>
  )
}
