from app.models.execution import WorkflowRun, TaskExecution, RunStatus


class ProfileReport:
    def __init__(self, run: WorkflowRun):
        self.run = run
        self.total_duration_ms = run.total_duration_ms or 0
        self.task_count = len(run.task_executions)
        self.completed_count = sum(1 for t in run.task_executions if t.status.value == "completed")
        self.failed_count = sum(1 for t in run.task_executions if t.status.value == "failed")

        durations = [t.duration_ms for t in run.task_executions if t.duration_ms is not None]
        self.avg_task_duration_ms = sum(durations) / len(durations) if durations else 0
        self.max_task_duration_ms = max(durations) if durations else 0
        self.min_task_duration_ms = min(durations) if durations else 0
        self.median_task_duration_ms = sorted(durations)[len(durations) // 2] if durations else 0

        self.total_cpu_time_ms = sum(t.cpu_time_ms or 0 for t in run.task_executions)
        self.total_memory_bytes = sum(t.memory_bytes or 0 for t in run.task_executions)
        self.parallelism_efficiency = self._calc_parallelism_efficiency()

        self.slowest_tasks = sorted(
            [(t, t.duration_ms or 0) for t in run.task_executions if t.duration_ms],
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        self.bottlenecks = self._detect_bottlenecks()

    def _calc_parallelism_efficiency(self) -> float:
        if self.total_duration_ms == 0:
            return 0.0
        total_task_time = sum(t.duration_ms or 0 for t in self.run.task_executions)
        if total_task_time == 0:
            return 0.0
        ideal = total_task_time / self.task_count if self.task_count > 0 else total_task_time
        return min(1.0, ideal / (self.total_duration_ms / max(1, self.task_count)) if self.total_duration_ms > 0 else 0.0)

    def _detect_bottlenecks(self) -> list[dict]:
        bottlenecks = []
        for te, dur in self.slowest_tasks:
            if dur > self.avg_task_duration_ms * 2:
                bottlenecks.append({
                    "task_execution_id": te.id,
                    "task_id": te.task_id,
                    "duration_ms": dur,
                    "reason": f"{dur:.0f}ms is {dur/max(self.avg_task_duration_ms, 1):.1f}x the average",
                })
        return bottlenecks

    def to_dict(self) -> dict:
        return {
            "run_id": self.run.id,
            "workflow_id": self.run.workflow_id,
            "total_duration_ms": self.total_duration_ms,
            "task_count": self.task_count,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "avg_task_duration_ms": self.avg_task_duration_ms,
            "max_task_duration_ms": self.max_task_duration_ms,
            "min_task_duration_ms": self.min_task_duration_ms,
            "median_task_duration_ms": self.median_task_duration_ms,
            "total_cpu_time_ms": self.total_cpu_time_ms,
            "total_memory_bytes": self.total_memory_bytes,
            "parallelism_efficiency": self.parallelism_efficiency,
            "bottlenecks": self.bottlenecks,
            "slowest_tasks": [
                {"task_execution_id": te.id, "task_id": te.task_id, "duration_ms": dur}
                for te, dur in self.slowest_tasks
            ],
        }


def generate_report(run: WorkflowRun) -> ProfileReport:
    return ProfileReport(run)
