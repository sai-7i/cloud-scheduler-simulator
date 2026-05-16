from app.simulation.domain import Machine, Task
from app.simulation.metrics import calculate_metrics


def test_calculate_metrics_for_finished_and_rejected_tasks() -> None:
    machines = [
        Machine(id=1, name="node-a", total_cpu=4, total_memory=8192),
        Machine(id=2, name="node-b", total_cpu=4, total_memory=8192),
    ]
    tasks = [
        Task(
            id=1,
            name="finished",
            required_cpu=2,
            required_memory=4096,
            duration=3,
            submit_time=1,
            start_time=2,
            finish_time=5,
            machine_id=1,
        ),
        Task(
            id=2,
            name="rejected",
            required_cpu=8,
            required_memory=16384,
            duration=2,
            submit_time=0,
            rejected=True,
        ),
    ]
    resource_history = [
        {
            "time": 0,
            "machines": [
                {"cpu_utilization": 0.5, "memory_utilization": 0.25},
                {"cpu_utilization": 0.0, "memory_utilization": 0.0},
            ],
        },
        {
            "time": 1,
            "machines": [
                {"cpu_utilization": 0.5, "memory_utilization": 0.25},
                {"cpu_utilization": 0.5, "memory_utilization": 0.25},
            ],
        },
    ]

    metrics = calculate_metrics(machines, tasks, resource_history)

    assert metrics["average_cpu_utilization"] == 0.375
    assert metrics["average_memory_utilization"] == 0.1875
    assert metrics["average_waiting_time"] == 1
    assert metrics["max_waiting_time"] == 1
    assert metrics["average_turnaround_time"] == 4
    assert metrics["success_rate"] == 0.5
    assert metrics["rejection_rate"] == 0.5
    assert metrics["deadline_miss_rate"] == 0
    assert metrics["makespan"] == 5
    assert metrics["load_balance_score"] == 0
    assert metrics["average_cpu_load_balance_score"] == 0.03125
    assert metrics["average_memory_load_balance_score"] == 0.0078125
