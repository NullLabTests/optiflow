"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { Lightbulb } from "lucide-react"

export default function OptimizationsPage() {
  const [suggestions, setSuggestions] = useState<any[]>([])

  useEffect(() => {
    api.listWorkflows().then(async wfs => {
      const all: any[] = []
      for (const wf of wfs) {
        try {
          const suggestions = await api.getSuggestions(wf.id) as any[]
          all.push(...suggestions.map((s: any) => ({ ...s, workflow_name: wf.name })))
        } catch {}
      }
      setSuggestions(all)
    }).catch(() => {})
  }, [])

  async function handleApply(suggestionId: string) {
    try {
      await api.applyOptimization(suggestionId)
      setSuggestions(prev => prev.map(s => s.id === suggestionId ? { ...s, applied: true, status: "applied" } : s))
    } catch (err) { console.error(err) }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Optimization Hub</h2>
      <p className="text-sm text-gray-500">
        AI-powered suggestions to improve your workflow performance.
      </p>

      <div className="space-y-3">
        {suggestions.map(s => (
          <div key={s.id} className="rounded-xl border bg-white p-4">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-amber-50 p-2 mt-0.5">
                  <Lightbulb className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-xs text-indigo-600 font-medium mb-0.5">{s.workflow_name}</p>
                  <span className="inline-block rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 mb-1">
                    {s.suggestion_type}
                  </span>
                  <h3 className="font-semibold">{s.title}</h3>
                  {s.description && <p className="text-sm text-gray-500 mt-1">{s.description}</p>}
                  {s.estimated_improvement_pct && (
                    <p className="text-xs text-green-600 mt-1">
                      Estimated improvement: {s.estimated_improvement_pct}%
                    </p>
                  )}
                </div>
              </div>
              <div className="ml-4">
                {!s.applied && s.status !== "applied" ? (
                  <button
                    onClick={() => handleApply(s.id)}
                    className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition"
                  >
                    Apply
                  </button>
                ) : (
                  <span className="rounded-lg bg-green-100 px-4 py-2 text-sm font-medium text-green-700">
                    Applied
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        {suggestions.length === 0 && (
          <div className="rounded-xl border bg-white p-12 text-center">
            <Lightbulb className="h-8 w-8 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No optimization suggestions yet.</p>
            <p className="text-xs text-gray-400 mt-1">
              Create and run workflows, then use the Analyze feature to generate suggestions.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
