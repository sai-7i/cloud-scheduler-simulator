from app.simulation.domain import Machine, Task
from app.simulation.engine import run_simulation


def test_run_simulation_allocates_waiting_task_after_resources_release() -> None:
    machines = [Machine(id=1, name="node-a", total_cpu=4, total_memory=8192)]
    tasks = [
        Task(id=1, name="first", required_cpu=4, required_memory=8192, duration=2, submit_time=0),
        Task(id=2, name="second", required_cpu=4, required_memory=8192, duration=2, submit_time=0),
    ]

    result = run_simulation(machines, tasks, algorithm="first_fit", max_time=10)

    assert result["timeline"] == [
        {
            "task_id": 1,
            "task_name": "first",
            "machine_id": 1,
            "machine_name": "node-a",
            "start_time": 0,
            "finish_time": 2,
        },
        {
            "task_id": 2,
            "task_name": "second",
            "machine_id": 1,
            "machine_name": "node-a",
            "start_time": 2,
            "finish_time": 4,
        },
    ]
    assert result["metrics"]["success_rate"] == 1
    assert result["metrics"]["rejection_rate"] == 0
    assert result["metrics"]["makespan"] == 4


def test_run_simulation_rejects_tasks_left_after_max_time() -> None:
    machines = [Machine(id=1, name="node-a", total_cpu=2, total_memory=4096)]
    tasks = [Task(id=1, name="too-large", required_cpu=4, required_memory=8192, duration=1, submit_time=0)]

    result = run_simulation(machines, tasks, algorithm="first_fit", max_time=1)

    assert result["timeline"] == []
    assert tasks[0].rejected is True
    assert result["metrics"]["success_rate"] == 0
    assert result["metrics"]["rejection_rate"] == 1


def test_cfs_like_runs_lower_virtual_runtime_task_first() -> None:
    machines = [Machine(id=1, name="node-a", total_cpu=4, total_memory=8192)]
    tasks = [
        Task(
            id=1,
            name="long-low-priority",
            required_cpu=4,
            required_memory=8192,
            duration=6,
            submit_time=0,
            priority=0,
        ),
        Task(
            id=2,
            name="short-high-priority",
            required_cpu=4,
            required_memory=8192,
            duration=2,
            submit_time=0,
            priority=3,
        ),
    ]

    result = run_simulation(machines, tasks, algorithm="cfs_like", max_time=10)

    assert [item["task_id"] for item in result["timeline"]] == [2, 1]
    assert result["timeline"][0]["start_time"] == 0
    assert result["timeline"][0]["finish_time"] == 2
    assert result["timeline"][1]["start_time"] == 2
    assert result["timeline"][1]["finish_time"] == 8


def test_least_loaded_uses_lower_load_machine_when_multiple_can_fit() -> None:
    machines = [
        Machine(id=1, name="busy", total_cpu=4, total_memory=8192, used_cpu=2, used_memory=4096),
        Machine(id=2, name="light", total_cpu=4, total_memory=8192),
    ]
    tasks = [Task(id=1, name="task-1", required_cpu=2, required_memory=4096, duration=2, submit_time=0)]

    result = run_simulation(machines, tasks, algorithm="least_loaded", max_time=5)

    assert result["timeline"] == [
        {
            "task_id": 1,
            "task_name": "task-1",
            "machine_id": 2,
            "machine_name": "light",
            "start_time": 0,
            "finish_time": 2,
        }
    ]
