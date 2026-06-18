"use client"
import { useState } from "react"
import { api } from "@/lib/api"

export default function LoginPage({ onLogin }: { onLogin: (token: string) => void }) {
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [error, setError] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    try {
      const res = isRegister
        ? await api.register(email, password, name)
        : await api.login(email, password)
      api.setToken(res.access_token)
      onLogin(res.access_token)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Authentication failed")
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-indigo-900 via-purple-900 to-slate-900">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
        <div className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-indigo-600">OptiFlow</h1>
          <p className="mt-1 text-sm text-gray-500">Intelligent Workflow Orchestrator</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <input
              type="text" placeholder="Display Name"
              value={name} onChange={e => setName(e.target.value)}
              className="w-full rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            />
          )}
          <input
            type="email" placeholder="Email" required
            value={email} onChange={e => setEmail(e.target.value)}
            className="w-full rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <input
            type="password" placeholder="Password" required
            value={password} onChange={e => setPassword(e.target.value)}
            className="w-full rounded-lg border px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition"
          >
            {isRegister ? "Create Account" : "Sign In"}
          </button>
        </form>
        <p className="mt-4 text-center text-xs text-gray-500">
          {isRegister ? "Already have an account?" : "Don't have an account?"}{" "}
          <button onClick={() => setIsRegister(!isRegister)} className="text-indigo-600 hover:underline">
            {isRegister ? "Sign In" : "Register"}
          </button>
        </p>
      </div>
    </div>
  )
}
