"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import { useParams, useRouter } from "next/navigation"
import { formatDuration, statusColor } from "@/lib/utils"
import { BarChart3, Clock, CheckCircle, XCircle, ArrowLeft } from "lucide-react"

export default function RunDetail() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const [run, setRun] = useState<any>(null)
  const [profile, setProfile] = useState<any>(null)

  useEffect(() => {
    api.getRun(id).then(setRun).catch(() => router.push("/workflows"))
    api.getProfile(id).then(setProfile).catch(() => {})
  }, [id, router])

  if (!run) return <div className="flex h-64 items-center justify-center text-gray-400">Loading...</div>

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" /> Back
      </button>

      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Run Details</h2>
          <p className="text-sm text-gray-500">ID: {run.id.slice(0, 8)}...</p>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs font-medium ${statusColor(run.status)}`}>
          {run.status}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <StatCard icon={Clock} label="Total Duration" value={formatDuration(run.total_duration_ms)} />
        <StatCard icon={CheckCircle} label="Tasks" value={`${run.task_executions?.length || 0}`} />
        <StatCard icon={CheckCircle} label="Completed" value={`${run.task_executions?.filter((t: any) => t.status === "completed").length || 0}`} />
        <StatCard icon={XCircle} label="Failed" value={`${run.task_executions?.filter((t: any) => t.status === "failed").length || 0}`} />
      </div>

      {profile && (
        <div className="rounded-xl border bg-white">
          <div className="border-b px-6 py-4">
            <h3 className="font-semibold flex items-center gap-2">
              <BarChart3 className="h-4 w-4" /> Profile Report
            </h3>
          </div>
          <div className="p-6 grid grid-cols-3 gap-4 text-sm">
            <ProfileRow label="Avg Task Duration" value={formatDuration(profile.avg_task_duration_ms)} />
            <ProfileRow label="Max Task Duration" value={formatDuration(profile.max_task_duration_ms)} />
            <ProfileRow label="Min Task Duration" value={formatDuration(profile.min_task_duration_ms)} />
            <ProfileRow label="Median Task Duration" value={formatDuration(profile.median_task_duration_ms)} />
            <ProfileRow label="Parallelism Efficiency" value={`${(profile.parallelism_efficiency * 100).toFixed(0)}%`} />
            <ProfileRow label="Total CPU Time" value={formatDuration(profile.total_cpu_time_ms)} />
            {profile.bottlenecks.length > 0 && (
              <div className="col-span-3">
                <h4 className="font-semibold text-amber-600 mb-2">Bottlenecks Detected</h4>
                {profile.bottlenecks.map((b: any, i: number) => (
                  <div key={i} className="rounded-lg bg-amber-50 border border-amber-200 p-3 mb-2 text-xs">
                    Task {b.task_id.slice(0, 8)}... — {formatDuration(b.duration_ms)} — {b.reason}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="rounded-xl border bg-white">
        <div className="border-b px-6 py-4">
          <h3 className="font-semibold">Task Executions</h3>
        </div>
        <div className="divide-y text-sm">
          {run.task_executions?.map((te: any) => (
            <div key={te.id} className="px-6 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${
                  te.status === "completed" ? "bg-green-500" :
                  te.status === "failed" ? "bg-red-500" :
                  te.status === "running" ? "bg-blue-500" : "bg-yellow-500"
                }`} />
                <div>
                  <p className="font-medium">{te.task_id.slice(0, 8)}...</p>
                  {te.error_message && <p className="text-xs text-red-500 mt-0.5">{te.error_message.slice(0, 100)}</p>}
                </div>
              </div>
              <div className="text-right text-xs text-gray-500">
                <p>{formatDuration(te.duration_ms)}</p>
                <p>Attempt {te.attempt_number}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-indigo-50 p-2">
          <Icon className="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <p className="text-xs text-gray-500">{label}</p>
          <p className="text-lg font-bold">{value}</p>
        </div>
      </div>
    </div>
  )
}

function ProfileRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between rounded-lg bg-gray-50 px-3 py-2">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  )
}
