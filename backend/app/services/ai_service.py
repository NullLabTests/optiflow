import json
from openai import OpenAI, AsyncOpenAI
from app.core.config import settings


_client = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        if settings.deepseek_api_key:
            _client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url="https://api.deepseek.com/v1",
            )
        else:
            _client = None
    return _client


async def generate_workflow_from_nl(prompt: str) -> dict:
    client = _get_client()
    if not client:
        return _mock_workflow_from_nl(prompt)

    system_prompt = """You are an expert workflow designer. Given a natural language description, 
generate a JSON workflow definition. The output must be valid JSON with this structure:
{
  "name": "workflow name",
  "description": "brief description",
  "tasks": [
    {
      "id": "task-1",
      "name": "Task Name",
      "task_type": "python|http|simulate|file",
      "config": { ... task-specific config ... },
      "position_x": 100,
      "position_y": 100
    }
  ],
  "edges": [
    { "source_task_id": "task-1", "target_task_id": "task-2" }
  ]
}
For python tasks, include a "code" field in config.
For simulate tasks, include "simulate_duration_ms" and "complexity".
For http tasks, include "url", "method".
Position tasks in a sensible left-to-right, top-to-bottom layout."""

    try:
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content
        return json.loads(text)
    except Exception:
        return _mock_workflow_from_nl(prompt)


async def analyze_and_optimize(workflow_json: dict, run_data: dict | None = None) -> list[dict]:
    client = _get_client()
    if not client:
        return _mock_optimization_suggestions()

    system_prompt = """You are an expert workflow optimization AI. Analyze the given workflow DAG and 
execution data, and suggest specific optimizations. Return a JSON array of suggestions:
[
  {
    "suggestion_type": "parallelize|cache|algorithm_swap|code_improvement|restructure|remove_redundancy|resource_allocation",
    "title": "Short title",
    "description": "Detailed explanation",
    "target_task_id": "task-id or null",
    "estimated_improvement_pct": 25.0,
    "proposed_changes": { ... any structured change data ... }
  }
]
Be specific and actionable. Only suggest optimizations that would genuinely help."""

    prompt = f"Workflow: {json.dumps(workflow_json, indent=2)}\n"
    if run_data:
        prompt += f"Execution Data: {json.dumps(run_data, indent=2)}\n"
    prompt += "\nSuggest concrete optimizations."

    try:
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content
        result = json.loads(text)
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            suggestions = result.get("suggestions", result.get("optimizations", []))
            if suggestions:
                return suggestions
            return [result]
        return _mock_optimization_suggestions()
    except Exception:
        return _mock_optimization_suggestions()


async def suggest_code_improvements(code: str, error: str | None = None) -> str:
    client = _get_client()
    if not client:
        return "# Add error handling and logging\n# Consider breaking this into smaller functions"

    system_prompt = "You are an expert Python code reviewer. Suggest improvements for the given task code."
    user_prompt = f"Code:\n{code}\n"
    if error:
        user_prompt += f"Error:\n{error}\n"
    user_prompt += "\nSuggest specific improvements."

    try:
        resp = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content
    except Exception:
        return "# Add error handling and logging"


def _mock_workflow_from_nl(prompt: str) -> dict:
    return {
        "name": "Data Processing Pipeline",
        "description": f"Auto-generated from: {prompt[:50]}",
        "tasks": [
            {
                "id": "task-1",
                "name": "Fetch Data",
                "task_type": "http",
                "config": {"url": "https://api.example.com/data", "method": "GET"},
                "position_x": 50,
                "position_y": 100,
            },
            {
                "id": "task-2",
                "name": "Transform Data",
                "task_type": "python",
                "config": {"code": "result = 'transformed: ' + str(input_data)"},
                "position_x": 350,
                "position_y": 100,
            },
            {
                "id": "task-3",
                "name": "Simulate Processing",
                "task_type": "simulate",
                "config": {"simulate_duration_ms": 500, "complexity": "medium"},
                "position_x": 650,
                "position_y": 100,
            },
        ],
        "edges": [
            {"source_task_id": "task-1", "target_task_id": "task-2"},
            {"source_task_id": "task-2", "target_task_id": "task-3"},
        ],
    }


def _mock_optimization_suggestions() -> list[dict]:
    return [
        {
            "suggestion_type": "cache",
            "title": "Cache HTTP results",
            "description": "Task 'Fetch Data' is an HTTP GET which is idempotent and could be cached.",
            "target_task_id": "task-1",
            "estimated_improvement_pct": 40.0,
            "proposed_changes": {"recommendation": "add_caching", "task_name": "Fetch Data"},
        },
        {
            "suggestion_type": "parallelize",
            "title": "Run independent tasks in parallel",
            "description": "Multiple tasks have no dependencies on each other and can run concurrently.",
            "estimated_improvement_pct": 25.0,
            "proposed_changes": {"recommendation": "restructure_dependencies"},
        },
    ]
