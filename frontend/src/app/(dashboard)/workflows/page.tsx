"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import Link from "next/link"
import { Plus, Play, Trash2 } from "lucide-react"
import { formatDuration } from "@/lib/utils"
import { useRouter } from "next/navigation"

export default function WorkflowsPage() {
  const router = useRouter()
  const [workflows, setWorkflows] = useState<Array<{
    id: string; name: string; description: string | null
    task_count: number; created_at: string
  }>>([])
  const [creating, setCreating] = useState(false)
  const [showNewForm, setShowNewForm] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")

  useEffect(() => { api.listWorkflows().then(setWorkflows).catch(() => {}) }, [])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setCreating(true)
    try {
      const wf = await api.createWorkflow({ name, description, tasks: [], edges: [] })
      setShowNewForm(false)
      setName("")
      setDescription("")
      router.push(`/workflows/${wf.id}`)
    } catch (err) { console.error(err) }
    setCreating(false)
  }

  async function handleExecute(id: string) {
    try {
      const run = await api.executeWorkflow(id)
      router.push(`/runs/${run.id}`)
    } catch (err) { console.error(err) }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Workflows</h2>
        <button
          onClick={() => setShowNewForm(!showNewForm)}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition"
        >
          <Plus className="h-4 w-4" /> New Workflow
        </button>
      </div>

      {showNewForm && (
        <form onSubmit={handleCreate} className="rounded-xl border bg-white p-4 space-y-3">
          <input
            type="text" placeholder="Workflow name" required
            value={name} onChange={e => setName(e.target.value)}
            className="w-full rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <textarea
            placeholder="Description (optional)"
            value={description} onChange={e => setDescription(e.target.value)}
            className="w-full rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            rows={2}
          />
          <div className="flex gap-2">
            <button
              type="submit" disabled={creating}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {creating ? "Creating..." : "Create"}
            </button>
            <button
              type="button" onClick={() => setShowNewForm(false)}
              className="rounded-lg border px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {workflows.map(wf => (
          <div key={wf.id} className="rounded-xl border bg-white p-4 flex items-center justify-between hover:shadow-sm transition">
            <div>
              <Link href={`/workflows/${wf.id}`} className="font-semibold hover:text-indigo-600">
                {wf.name}
              </Link>
              {wf.description && <p className="text-sm text-gray-500 mt-0.5">{wf.description}</p>}
              <p className="text-xs text-gray-400 mt-1">{wf.task_count} tasks</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleExecute(wf.id)}
                className="flex items-center gap-1 rounded-lg border px-3 py-1.5 text-xs font-medium text-green-600 hover:bg-green-50 transition"
              >
                <Play className="h-3 w-3" /> Run
              </button>
              <Link
                href={`/workflows/${wf.id}`}
                className="rounded-lg border px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition"
              >
                Edit
              </Link>
            </div>
          </div>
        ))}
        {workflows.length === 0 && (
          <p className="text-center text-sm text-gray-400 py-12">No workflows yet. Create one!</p>
        )}
      </div>
    </div>
  )
}
