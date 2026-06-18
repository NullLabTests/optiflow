"""Core unit tests for OptiFlow backend."""
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.services.profiler_service import ProfileReport


class MockTaskExecution:
    def __init__(self, task_id="t1", status="completed", duration_ms=100,
                 cpu_time_ms=50, memory_bytes=1024, attempt_number=1):
        self.id = "te-1"
        self.task_id = task_id
        self.status = type("Status", (), {"value": status})()
        self.duration_ms = duration_ms
        self.cpu_time_ms = cpu_time_ms
        self.memory_bytes = memory_bytes
        self.input_size_bytes = 0
        self.output_size_bytes = 0
        self.attempt_number = attempt_number


class MockWorkflowRun:
    def __init__(self, task_executions=None):
        self.id = "run-1"
        self.workflow_id = "wf-1"
        self.task_executions = task_executions if task_executions is not None else [
            MockTaskExecution(task_id="t1", duration_ms=100),
            MockTaskExecution(task_id="t2", duration_ms=200),
            MockTaskExecution(task_id="t3", duration_ms=300),
        ]
        self.total_duration_ms = 500
        self.status = type("Status", (), {"value": "completed"})()


def test_password_hashing():
    pw = "test_password_123"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("wrong_password", hashed)


def test_jwt_tokens():
    data = {"sub": "user-1", "role": "admin"}
    token = create_access_token(data)
    assert token is not None
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-1"
    assert decoded["role"] == "admin"


def test_profile_report_generation():
    run = MockWorkflowRun()
    report = ProfileReport(run)
    data = report.to_dict()

    assert data["run_id"] == "run-1"
    assert data["workflow_id"] == "wf-1"
    assert data["task_count"] == 3
    assert data["completed_count"] == 3
    assert data["total_duration_ms"] == 500
    assert data["avg_task_duration_ms"] == 200
    assert data["max_task_duration_ms"] == 300
    assert data["min_task_duration_ms"] == 100
    assert len(data["bottlenecks"]) == 0  # 300ms is not > 2x avg (200ms)


def test_profile_with_failures():
    execs = [
        MockTaskExecution(task_id="t1", duration_ms=100),
        MockTaskExecution(task_id="t2", status="failed", duration_ms=None),
    ]
    run = MockWorkflowRun(task_executions=execs)
    report = ProfileReport(run)
    data = report.to_dict()
    assert data["task_count"] == 2
    assert data["completed_count"] == 1
    assert data["failed_count"] == 1
    assert data["bottlenecks"] == []


def test_profile_parallelism_efficiency():
    run = MockWorkflowRun()
    report = ProfileReport(run)
    # total task time = 600, task_count = 3, total_duration = 500
    # ideal = 600/3 = 200, actual_avg = 500/3 ≈ 166.7
    # efficiency = 200 / 166.7 ≈ 1.2, capped at 1.0
    assert 0 < report.parallelism_efficiency <= 1.0


def test_empty_run():
    run = MockWorkflowRun(task_executions=[])
    report = ProfileReport(run)
    data = report.to_dict()
    assert data["task_count"] == 0
    assert data["avg_task_duration_ms"] == 0
    assert data["max_task_duration_ms"] == 0
