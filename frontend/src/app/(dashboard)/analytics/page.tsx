"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { TrendingUp, Activity, CheckCircle, XCircle } from "lucide-react"

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<any>(null)
  const [suggestions, setSuggestions] = useState<any[]>([])

  useEffect(() => {
    api.getAnalyticsSummary().then(setSummary).catch(() => {})
    api.listWorkflows().then(async wfs => {
      const all: any[] = []
      for (const wf of wfs.slice(0, 5)) {
        try {
          const s: any[] = await api.getSuggestions(wf.id) as any[]
          all.push(...s)
        } catch {}
      }
      setSuggestions(all)
    }).catch(() => {})
  }, [])

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Analytics</h2>

      <div className="grid grid-cols-4 gap-4">
        <AnalyticCard icon={Activity} label="Total Workflows" value={summary?.total_workflows ?? "—"} />
        <AnalyticCard icon={TrendingUp} label="Total Runs" value={summary?.total_runs ?? "—"} />
        <AnalyticCard icon={CheckCircle} label="Success Rate" value={summary ? `${summary.success_rate.toFixed(1)}%` : "—"} />
        <AnalyticCard icon={XCircle} label="Failed Runs" value={summary?.failed_runs ?? "—"} />
      </div>

      <div className="rounded-xl border bg-white">
        <div className="border-b px-6 py-4">
          <h3 className="font-semibold">All Optimization Suggestions</h3>
        </div>
        <div className="divide-y text-sm">
          {suggestions.map(s => (
            <div key={s.id} className="px-6 py-3 flex justify-between items-center">
              <div>
                <span className="inline-block rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 mr-2">
                  {s.suggestion_type}
                </span>
                {s.title}
              </div>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                {s.estimated_improvement_pct && (
                  <span className="text-green-600">+{s.estimated_improvement_pct}%</span>
                )}
                <span className={s.applied ? "text-green-600" : "text-gray-400"}>
                  {s.applied ? "Applied" : s.status}
                </span>
              </div>
            </div>
          ))}
          {suggestions.length === 0 && (
            <p className="px-6 py-8 text-center text-gray-400">
              Run some workflows and analyze them to see suggestions here.
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function AnalyticCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
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
