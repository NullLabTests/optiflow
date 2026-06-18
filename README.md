# OptiFlow — Intelligent Workflow Orchestrator & Self-Optimizing System

[![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-00a393?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

OptiFlow is a full-stack web application that lets you define complex, multi-step workflows as directed acyclic graphs (DAGs). It executes them reliably with parallelism, retries, and error handling, profiles performance, detects bottlenecks, and uses AI to suggest and apply optimizations.

![Dashboard](https://img.shields.io/badge/status-MVP-yellow)

## Features

- **Workflow Definition** — Create workflows via UI (React Flow DAG editor) or natural language (AI generates the DAG)
- **Task Types** — Python code execution, HTTP calls, file operations, and built-in simulators for easy profiling demos
- **Execution Engine** — Dependency-aware scheduling with parallel execution, retries, timeouts, and logging
- **Dashboard** — List workflows, run history, execution timelines, and analytics
- **Profiling** — Per-task timing, success rates, resource estimates, bottleneck detection, critical path analysis
- **Self-Optimization** — AI-powered analysis of runs that suggests parallelization, caching, code improvements, and restructuring. Apply suggestions with one click
- **AI Assistant** — Natural language workflow creation, code improvement suggestions, and optimization analysis via DeepSeek API
- **Analytics** — Success rates, average durations, optimization impact tracking

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────┐
│  Frontend   │────▶│   Backend    │────▶│ Database  │
│  Next.js    │     │   FastAPI    │     │ Postgres  │
│  React Flow │     │  asyncio     │     │           │
│  Recharts   │     │  SQLAlchemy  │     │           │
└─────────────┘     └──────┬───────┘     └───────────┘
                           │
                    ┌──────┴───────┐
                    │  AI Service   │
                    │ (DeepSeek API)│
                    └──────────────┘
```

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 16 (React) + Tailwind + React Flow + Recharts | Modern, fast, great DAG visualization |
| **Backend** | FastAPI + SQLAlchemy + asyncio | Async-native Python, excellent for AI integration |
| **Database** | PostgreSQL 16 | Reliable, mature, JSON support |
| **AI** | DeepSeek API via OpenAI SDK | Strong reasoning for optimization tasks |
| **Queue** | In-process asyncio (lightweight) | Avoids Celery overhead for MVP; Redis available for scaling |

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 22+
- PostgreSQL 16+
- Docker (optional, for containerized setup)

### Local Development

```bash
# 1. Clone and set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your database URL and DeepSeek API key

# 3. Run database migrations
alembic upgrade head

# 4. Start backend
uvicorn app.main:app --reload --port 8000

# 5. In another terminal, start frontend
cd frontend
npm install
npm run dev
```

### Docker Compose (Full Stack)

```bash
docker compose up --build
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage

### Creating a Workflow

1. **Via UI**: Go to Workflows → New Workflow → name it → Add Task buttons → drag edges between nodes in the DAG editor
2. **Via Natural Language**: On the Dashboard, type "Fetch data from an API, transform it, then save to a file" and click "Create with AI"

### Running and Profiling

1. Open a workflow and click **Execute**
2. The system runs tasks respecting dependencies, in parallel where safe
3. After completion, click **Analyze** to get optimization suggestions
4. View detailed profiles on the Run detail page

### Optimization Loop

1. **Run** → **Profile** → **Analyze** → **Apply** → **Re-run** to measure improvement
2. The system tracks all suggestions and their application status
3. AI generates specific, actionable recommendations with estimated improvement percentages

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/auth/me` | Current user info |
| POST | `/api/v1/workflows` | Create workflow |
| GET | `/api/v1/workflows` | List workflows |
| GET | `/api/v1/workflows/{id}` | Get workflow with DAG |
| PUT | `/api/v1/workflows/{id}` | Update workflow |
| DELETE | `/api/v1/workflows/{id}` | Delete workflow |
| POST | `/api/v1/workflows/from-nl` | Create from natural language |
| POST | `/api/v1/workflows/{id}/execute` | Execute workflow |
| GET | `/api/v1/workflows/{id}/runs` | List runs |
| GET | `/api/v1/runs/{id}` | Run details |
| GET | `/api/v1/runs/{id}/profile` | Profile report |
| POST | `/api/v1/workflows/{id}/analyze` | Generate suggestions |
| GET | `/api/v1/workflows/{id}/suggestions` | List suggestions |
| POST | `/api/v1/optimizations/apply` | Apply suggestion |
| GET | `/api/v1/analytics/summary` | Analytics summary |

## Testing

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

## Project Structure

```
optiflow/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/           # Next.js app router pages
│       ├── components/    # React components
│       └── lib/           # API client, utils
├── docker-compose.yml
└── README.md
```

## AI Integration

OptiFlow uses the DeepSeek API for:
- **Workflow generation**: Natural language → structured DAG
- **Optimization analysis**: Suggests parallelization, caching, code improvements
- **Code review**: Suggests improvements to task Python code

Set `DEEPSEEK_API_KEY` and `DEEPSEEK_MODEL` in `.env` to enable AI features. Without a key, the system falls back to rule-based mock suggestions.

## License

MIT License — see [LICENSE](LICENSE).
