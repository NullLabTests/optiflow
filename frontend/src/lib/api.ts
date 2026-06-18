const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

interface RequestOptions {
  method?: string
  body?: unknown
  token?: string
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = "ApiError"
  }
}

async function request(path: string, options: RequestOptions = {}): Promise<any> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }
  if (options.token) {
    headers["Authorization"] = `Bearer ${options.token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (res.status === 204) return undefined
  if (!res.ok) {
    const err = await res.text()
    throw new ApiError(res.status, err || res.statusText)
  }
  return res.json()
}

function getToken(): string {
  if (typeof window === "undefined") return ""
  return localStorage.getItem("optiflow_token") || ""
}

export const api = {
  setToken(token: string) {
    localStorage.setItem("optiflow_token", token)
  },

  getToken,

  async login(email: string, password: string) {
    return request("/auth/login", { method: "POST", body: { email, password } })
  },

  async register(email: string, password: string, display_name?: string) {
    return request("/auth/register", { method: "POST", body: { email, password, display_name } })
  },

  async getMe() {
    return request("/auth/me", { token: getToken() })
  },

  async listWorkflows() {
    return request("/workflows", { token: getToken() })
  },

  async getWorkflow(id: string) {
    return request(`/workflows/${id}`, { token: getToken() })
  },

  async createWorkflow(data: Record<string, unknown>) {
    return request("/workflows", { method: "POST", body: data, token: getToken() })
  },

  async createWorkflowFromNL(prompt: string) {
    return request("/workflows/from-nl", { method: "POST", body: { prompt }, token: getToken() })
  },

  async executeWorkflow(id: string) {
    return request(`/workflows/${id}/execute`, { method: "POST", token: getToken() })
  },

  async getWorkflowRuns(workflowId: string) {
    return request(`/workflows/${workflowId}/runs`, { token: getToken() })
  },

  async getRun(runId: string) {
    return request(`/runs/${runId}`, { token: getToken() })
  },

  async getProfile(runId: string) {
    return request(`/runs/${runId}/profile`, { token: getToken() })
  },

  async analyzeWorkflow(workflowId: string, runId?: string) {
    return request(`/workflows/${workflowId}/analyze`, {
      method: "POST", body: { run_id: runId || null }, token: getToken()
    })
  },

  async getSuggestions(workflowId: string) {
    return request(`/workflows/${workflowId}/suggestions`, { token: getToken() })
  },

  async applyOptimization(suggestionId: string) {
    return request("/optimizations/apply", { method: "POST", body: { suggestion_id: suggestionId }, token: getToken() })
  },

  async getAnalyticsSummary() {
    return request("/analytics/summary", { token: getToken() })
  },
}
