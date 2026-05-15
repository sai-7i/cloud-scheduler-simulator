from app.schedulers.basic import get_scheduler
from app.simulation.cluster import Cluster
from app.simulation.domain import Machine, Task
from app.simulation.metrics import calculate_metrics


def run_simulation(
    machines: list[Machine], tasks: list[Task], algorithm: str, max_time: int
) -> dict:
    scheduler = get_scheduler(algorithm)
    cluster = Cluster(machines)
    waiting: list[Task] = []
    running: list[Task] = []
    pending = sorted(tasks, key=lambda task: (task.submit_time, task.id))
    timeline = []
    resource_history = []

    for current_time in range(max_time + 1):
        running = cluster.release_finished(current_time, running)

        while pending and pending[0].submit_time <= current_time:
            waiting.append(pending.pop(0))

        ordered_waiting = scheduler.order_waiting_tasks(waiting, current_time)
        remaining_waiting = []
        for task in ordered_waiting:
            machine = scheduler.select_machine(task, cluster.machines)
            if machine is None:
                remaining_waiting.append(task)
                continue
            cluster.allocate(machine, task, current_time)
            scheduler.on_task_scheduled(task, current_time)
            running.append(task)
            timeline.append(
                {
                    "task_id": task.id,
                    "task_name": task.name,
                    "machine_id": machine.id,
                    "machine_name": machine.name,
                    "start_time": task.start_time,
                    "finish_time": task.finish_time,
                }
            )
        waiting = remaining_waiting

        resource_history.append(_snapshot(current_time, cluster.machines))

        if not pending and not waiting and not running:
            break

    for task in waiting + pending:
        task.rejected = True

    return {
        "algorithm": algorithm,
        "timeline": timeline,
        "resource_history": resource_history,
        "metrics": calculate_metrics(cluster.machines, tasks, resource_history),
    }


def _snapshot(current_time: int, machines: list[Machine]) -> dict:
    return {
        "time": current_time,
        "machines": [
            {
                "machine_id": machine.id,
                "machine_name": machine.name,
                "used_cpu": machine.used_cpu,
                "used_memory": machine.used_memory,
                "cpu_utilization": machine.used_cpu / machine.total_cpu,
                "memory_utilization": machine.used_memory / machine.total_memory,
            }
            for machine in machines
        ],
    }
