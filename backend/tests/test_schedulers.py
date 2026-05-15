from app.schedulers.basic import get_scheduler
from app.simulation.domain import Machine, Task


def make_task(required_cpu: int = 2, required_memory: int = 4) -> Task:
    return Task(
        id=1,
        name="task-1",
        required_cpu=required_cpu,
        required_memory=required_memory,
        duration=3,
        submit_time=0,
    )


def test_first_fit_uses_first_machine_that_can_fit() -> None:
    machines = [
        Machine(id=1, name="small", total_cpu=1, total_memory=8),
        Machine(id=2, name="medium", total_cpu=4, total_memory=8),
        Machine(id=3, name="large", total_cpu=8, total_memory=16),
    ]

    selected = get_scheduler("first_fit").select_machine(make_task(), machines)

    assert selected == machines[1]


def test_best_fit_uses_tightest_cpu_fit() -> None:
    machines = [
        Machine(id=1, name="large", total_cpu=8, total_memory=16),
        Machine(id=2, name="medium", total_cpu=4, total_memory=8),
    ]

    selected = get_scheduler("best_fit").select_machine(make_task(), machines)

    assert selected == machines[1]


def test_worst_fit_uses_largest_remaining_cpu_fit() -> None:
    machines = [
        Machine(id=1, name="medium", total_cpu=4, total_memory=8),
        Machine(id=2, name="large", total_cpu=8, total_memory=16),
    ]

    selected = get_scheduler("worst_fit").select_machine(make_task(), machines)

    assert selected == machines[1]


def test_round_robin_advances_after_successful_allocation() -> None:
    machines = [
        Machine(id=1, name="a", total_cpu=4, total_memory=8),
        Machine(id=2, name="b", total_cpu=4, total_memory=8),
    ]
    scheduler = get_scheduler("round_robin")

    first = scheduler.select_machine(make_task(), machines)
    second = scheduler.select_machine(make_task(), machines)

    assert first == machines[0]
    assert second == machines[1]


def test_cfs_like_prefers_lower_estimated_virtual_runtime() -> None:
    scheduler = get_scheduler("cfs_like")
    waiting = [
        Task(
            id=1,
            name="long-low-priority",
            required_cpu=2,
            required_memory=4,
            duration=6,
            submit_time=0,
            priority=0,
        ),
        Task(
            id=2,
            name="short-high-priority",
            required_cpu=2,
            required_memory=4,
            duration=2,
            submit_time=0,
            priority=3,
        ),
    ]

    ordered = scheduler.order_waiting_tasks(waiting, current_time=0)

    assert [task.id for task in ordered] == [2, 1]


def test_least_loaded_prefers_machine_with_lower_cpu_and_memory_utilization() -> None:
    machines = [
        Machine(id=1, name="busy", total_cpu=4, total_memory=8, used_cpu=3, used_memory=6),
        Machine(id=2, name="light", total_cpu=4, total_memory=8, used_cpu=1, used_memory=2),
    ]

    selected = get_scheduler("least_loaded").select_machine(make_task(), machines)

    assert selected == machines[1]


def test_unknown_scheduler_raises_value_error() -> None:
    try:
        get_scheduler("missing")
    except ValueError as exc:
        assert "Unsupported scheduler" in str(exc)
    else:
        raise AssertionError("expected ValueError")
