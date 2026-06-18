<div align="center">

# ⚡ OptiFlow

**Intelligent Workflow Orchestrator & Self-Optimizing System**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![React Flow](https://img.shields.io/badge/React%20Flow-DAG-FF4154?style=for-the-badge&logo=react&logoColor=white)](https://reactflow.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![AI](https://img.shields.io/badge/AI-DeepSeek-4F46E5?style=for-the-badge&logo=openai&logoColor=white)](https://deepseek.com)
[![Status](https://img.shields.io/badge/Status-MVP%20%7C%20Active-22c55e?style=for-the-badge)]()

---

> **Define → Execute → Profile → Optimize → Repeat.**  
> OptiFlow turns complex multi-step workflows into self-improving pipelines.

</div>

## 🧠 What is OptiFlow?

OptiFlow is a full-stack application that lets you define complex, multi-step workflows as **directed acyclic graphs (DAGs)**, executes them with full parallelism and error handling, **profiles every run** down to the millisecond, automatically detects bottlenecks, and uses **AI to suggest and apply optimizations**.

The system embodies a continuous improvement loop: **build → run → measure → learn → improve**.

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Core
- **DAG Workflow Editor** — Visual drag-and-drop with React Flow
- **Natural Language Creation** — Describe a workflow, AI generates the DAG
- **4 Task Types** — Python, HTTP, File, Simulate (for profiling demos)
- **Execution Engine** — Async DAG scheduler with parallelism, retries, timeouts
- **Real-time Dashboard** — Run history, execution timelines, live status

</td>
<td width="50%">

### 🚀 Intelligence
- **Deep Profiling** — Per-task timing, resource estimates, variance analysis
- **Bottleneck Detection** — Automatic identification of slow paths
- **AI Optimization** — DeepSeek-powered suggestions (parallelize, cache, restructure)
- **One-Click Apply** — Apply suggestions and re-run to measure impact
- **Analytics** — Success rates, avg durations, optimization impact over time

</td>
</tr>
</table>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    🖥️  Frontend (Next.js 16)                 │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  │
│  │Dashboard │  │ DAG Editor│  │  Profile │  │Analytics  │  │
│  │          │  │React Flow │  │  Viewer  │  │ Dashboard │  │
│  └────┬─────┘  └─────┬─────┘  └────┬─────┘  └─────┬─────┘  │
└───────┼──────────────┼──────────────┼──────────────┼────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                   ⚙️  Backend (FastAPI)                       │
│  ┌────────────┐  ┌───────────┐  ┌────────┐  ┌───────────┐  │
│  │  REST API  │  │ Execution │  │Profiler│  │Optimizer  │  │
│  │            │  │  Engine   │  │Service │  │Service    │  │
│  └────────────┘  └───────────┘  └────────┘  └─────┬─────┘  │
│                                                    │        │
│                                         ┌──────────▼──────┐ │
│                                         │  AI Service     │ │
│                                         │ (DeepSeek API)  │ │
│                                         └─────────────────┘ │
└──────────────────┬─────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                     🗄️  PostgreSQL 16                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │
│  │Workflows │  │   Tasks  │  │   Runs   │  │Suggestions  │  │
│  │  + DAGs  │  │          │  │+ Profiles│  │+ Optimiz.   │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| 🖥️ **Frontend** | Next.js 16 + Tailwind + React Flow + Recharts | Modern, fast, best-in-class DAG visualization |
| ⚙️ **Backend** | FastAPI + SQLAlchemy + asyncio | Async-native Python, seamless AI/ML integration |
| 🗄️ **Database** | PostgreSQL 16 | Mature, reliable, native JSON support |
| 🤖 **AI** | DeepSeek API (OpenAI-compatible SDK) | Superior reasoning for optimization tasks |
| 🚦 **Queue** | In-process asyncio (Redis-ready) | Zero overhead for MVP, drop-in Celery later |
| 🐳 **Infra** | Docker Compose | One-command full-stack deployment |

## 🚀 Quick Start

### 🐳 Docker (Recommended)

```bash
# Clone and launch everything
git clone https://github.com/NullLabTests/optiflow.git
cd optiflow
docker compose up --build
```

Then open **[http://localhost:3000](http://localhost:3000)** 🎉

### 🔧 Manual Setup

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # Edit DB URL + DeepSeek key
uvicorn app.main:app --reload --port 8000 &

# Frontend
cd ../frontend
npm install
npm run dev
```

| Service | URL |
|---------|-----|
| 🌐 **Frontend** | http://localhost:3000 |
| 📡 **API** | http://localhost:8000 |
| 📖 **Docs** | http://localhost:8000/docs |
| 📘 **ReDoc** | http://localhost:8000/redoc |

## 🎮 Usage

### Creating a Workflow

| Method | How |
|--------|-----|
| 🖱️ **Visual Editor** | Navigate to Workflows → New Workflow → Add Tasks → Drag edges between nodes |
| 💬 **Natural Language** | On Dashboard, type *"Fetch data from an API, transform it with Python, then simulate heavy processing"* → click **Create with AI** |

### The Optimization Loop

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌────────┐    ┌─────────┐
│  Build  │───▶│  Execute │───▶│  Profile  │───▶│Analyze │───▶│ Optimize│
│ Workflow│    │  DAG     │    │  Metrics  │    │  Bottl.│    │  +Apply │
└─────────┘    └──────────┘    └───────────┘    └────────┘    └────┬────┘
      ▲                                                            │
      └───────────────────────── Re-run ───────────────────────────┘
```

1. **Run** → Click **Execute** on any workflow
2. **Profile** → View per-task timing, bottlenecks, critical path
3. **Analyze** → Click **Analyze** for AI/rule-based optimization suggestions
4. **Apply** → One-click apply suggestions (parallelize, cache, restructure)
5. **Re-run** → Measure the improvement, rinse and repeat

## 📡 API Reference

All endpoints under `/api/v1/`. Auth via Bearer token.

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Sign in |
| `GET` | `/auth/me` | Current user |

### Workflows
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/workflows` | Create workflow |
| `GET` | `/workflows` | List all workflows |
| `GET` | `/workflows/{id}` | Get workflow + DAG |
| `PUT` | `/workflows/{id}` | Update workflow |
| `DELETE` | `/workflows/{id}` | Delete workflow |
| `POST` | `/workflows/from-nl` | Create from natural language |
| `POST` | `/workflows/{id}/execute` | Execute workflow |
| `GET` | `/workflows/{id}/runs` | List run history |

### Profiling & Optimization
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/runs/{id}/profile` | Profile report with bottlenecks |
| `POST` | `/workflows/{id}/analyze` | Generate optimization suggestions |
| `GET` | `/workflows/{id}/suggestions` | List all suggestions |
| `POST` | `/optimizations/apply` | Apply a suggestion |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/summary` | Aggregate stats |

## 🧪 Testing

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

```
✓ test_password_hashing
✓ test_jwt_tokens
✓ test_profile_report_generation
✓ test_profile_with_failures
✓ test_profile_parallelism_efficiency
✓ test_empty_run
══════════════════════════════════════
6 passed in 0.61s
```

## 📁 Project Structure

```
optiflow/
├── 🐳 docker-compose.yml
│
├── ⚙️ backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── core/         # Config, DB engine, auth
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   └── services/     # Business logic layer
│   │       ├── execution_service.py   # 🧠 DAG scheduler + task runner
│   │       ├── profiler_service.py    # 📊 Metrics + bottleneck detection
│   │       ├── optimization_service.py # 💡 Rule-based suggestions
│   │       ├── ai_service.py          # 🤖 DeepSeek integration
│   │       └── workflow_service.py    # 📋 CRUD operations
│   ├── tests/
│   └── Dockerfile
│
└── 🖥️ frontend/
    └── src/
        ├── app/           # Next.js 16 app router pages
        ├── components/    # React components
        └── lib/           # API client, utilities
```

## 🤖 AI Integration

OptiFlow leverages **DeepSeek** (via OpenAI-compatible SDK) for three capabilities:

<table>
<tr>
<th>Feature</th>
<th>Without API Key</th>
<th>With DeepSeek API Key</th>
</tr>
<tr>
<td>🧩 Natural Language → Workflow</td>
<td>Mock template (3-task pipeline)</td>
<td>AI generates optimal DAG from description</td>
</tr>
<tr>
<td>🔍 Optimization Analysis</td>
<td>Rule-based (parallelize, cache, structure)</td>
<td>Context-aware AI suggestions with code diffs</td>
</tr>
<tr>
<td>📝 Code Review</td>
<td>Static tips</td>
<td>Deep analysis with specific improvements</td>
</tr>
</table>

```bash
# In backend/.env
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_MODEL=deepseek-chat
```

## 📊 The Optimization Loop in Action

```
Before Optimization                    After Optimization
┌──────────────────┐                  ┌──────────────────┐
│ Task A → 1200ms  │                  │ Task A → 800ms   │
│ Task B → 1100ms  │    AI Analyzes  │ Task B → 800ms   │◀── Parallelized!
│ Task C → 1300ms  │ ──────────────▶ │ Task C → 900ms   │
│ Total:  3600ms   │    + Caching    │ Total:  2500ms   │
│ Bottleneck: A,B,C│                  │ 31% faster! 🎉   │
└──────────────────┘                  └──────────────────┘
```

## 📜 License

MIT License — see [LICENSE](LICENSE).

---

<div align="center">

**Built with** 🧠 **by NullLabTests**

⭐ Star this repo if you find it useful!  
🐛 [Report a Bug](https://github.com/NullLabTests/optiflow/issues) · 💡 [Request Feature](https://github.com/NullLabTests/optiflow/issues)

</div>
