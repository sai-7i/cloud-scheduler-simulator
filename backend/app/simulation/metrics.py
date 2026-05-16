from collections.abc import Sequence

from app.simulation.domain import Machine, Task


def calculate_metrics(
    machines: list[Machine], tasks: list[Task], resource_history: list[dict]
) -> dict[str, float | int]:
    finished_tasks = [task for task in tasks if task.finish_time is not None]
    rejected_tasks = [task for task in tasks if task.rejected]
    total_tasks = len(tasks)

    cpu_samples = []
    memory_samples = []
    for tick in resource_history:
        for machine in tick["machines"]:
            cpu_samples.append(machine["cpu_utilization"])
            memory_samples.append(machine["memory_utilization"])

    waiting_times = [task.start_time - task.submit_time for task in finished_tasks if task.start_time is not None]
    turnaround_times = [
        task.finish_time - task.submit_time for task in finished_tasks if task.finish_time is not None
    ]
    deadline_misses = [
        task
        for task in finished_tasks
        if task.deadline is not None and task.finish_time is not None and task.finish_time > task.deadline
    ]
    tasks_with_deadline = [task for task in tasks if task.deadline is not None]

    final_cpu_utils = [
        machine.used_cpu / machine.total_cpu if machine.total_cpu else 0 for machine in machines
    ]
    average_final_cpu = sum(final_cpu_utils) / len(final_cpu_utils) if final_cpu_utils else 0
    load_balance_score = (
        sum((value - average_final_cpu) ** 2 for value in final_cpu_utils) / len(final_cpu_utils)
        if final_cpu_utils
        else 0
    )

    return {
        "average_cpu_utilization": _average(cpu_samples),
        "average_memory_utilization": _average(memory_samples),
        "average_waiting_time": _average(waiting_times),
        "max_waiting_time": max(waiting_times, default=0),
        "average_turnaround_time": _average(turnaround_times),
        "success_rate": len(finished_tasks) / total_tasks if total_tasks else 0,
        "rejection_rate": len(rejected_tasks) / total_tasks if total_tasks else 0,
        "deadline_miss_rate": len(deadline_misses) / len(tasks_with_deadline) if tasks_with_deadline else 0,
        "makespan": max((task.finish_time or 0 for task in finished_tasks), default=0),
        "load_balance_score": load_balance_score,
        "average_cpu_load_balance_score": _average_tick_variance(resource_history, "cpu_utilization"),
        "average_memory_load_balance_score": _average_tick_variance(resource_history, "memory_utilization"),
    }


def _average(values: Sequence[float | int]) -> float:
    return sum(values) / len(values) if values else 0


def _average_tick_variance(resource_history: list[dict], metric_name: str) -> float:
    variances = []
    for tick in resource_history:
        values = [machine[metric_name] for machine in tick["machines"]]
        if not values:
            continue
        average = sum(values) / len(values)
        variances.append(sum((value - average) ** 2 for value in values) / len(values))
    return _average(variances)
