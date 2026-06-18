"use client"
import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import LoginPage from "@/components/LoginPage"
import DashboardLayout from "@/components/DashboardLayout"
import DashboardHome from "@/components/DashboardHome"

export default function Home() {
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const t = api.getToken()
    if (t) {
      api.getMe().then(() => setToken(t)).catch(() => {
        localStorage.removeItem("optiflow_token")
        setToken(null)
      }).finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  if (loading) return <div className="flex h-screen items-center justify-center">Loading...</div>
  if (!token) return <LoginPage onLogin={setToken} />

  return (
    <DashboardLayout onLogout={() => { localStorage.removeItem("optiflow_token"); setToken(null) }}>
      <DashboardHome />
    </DashboardLayout>
  )
}
