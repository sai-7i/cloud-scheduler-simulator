from app.schedulers.base import Scheduler
from app.simulation.domain import Machine, Task


class FirstFitScheduler(Scheduler):
    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        for machine in machines:
            if machine.can_fit(task):
                return machine
        return None


class BestFitScheduler(Scheduler):
    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        candidates = [machine for machine in machines if machine.can_fit(task)]
        if not candidates:
            return None
        return min(candidates, key=lambda machine: machine.available_cpu - task.required_cpu)


class WorstFitScheduler(Scheduler):
    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        candidates = [machine for machine in machines if machine.can_fit(task)]
        if not candidates:
            return None
        return max(candidates, key=lambda machine: machine.available_cpu - task.required_cpu)


class RoundRobinScheduler(Scheduler):
    def __init__(self) -> None:
        self.next_index = 0

    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        if not machines:
            return None
        for offset in range(len(machines)):
            index = (self.next_index + offset) % len(machines)
            machine = machines[index]
            if machine.can_fit(task):
                self.next_index = (index + 1) % len(machines)
                return machine
        return None


class LeastLoadedScheduler(Scheduler):
    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        candidates = [machine for machine in machines if machine.can_fit(task)]
        if not candidates:
            return None
        return min(candidates, key=self._load_key)

    def _load_key(self, machine: Machine) -> tuple[float, float, int]:
        return (
            machine.used_cpu / machine.total_cpu,
            machine.used_memory / machine.total_memory,
            machine.id,
        )


class CFSLikeScheduler(Scheduler):
    def __init__(self) -> None:
        self.virtual_runtime: dict[int, float] = {}

    def order_waiting_tasks(self, waiting: list[Task], current_time: int) -> list[Task]:
        return sorted(
            waiting,
            key=lambda task: (
                self.virtual_runtime.get(task.id, self._estimated_virtual_runtime(task)),
                task.submit_time,
                task.id,
            ),
        )

    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        for machine in machines:
            if machine.can_fit(task):
                return machine
        return None

    def on_task_scheduled(self, task: Task, current_time: int) -> None:
        base_runtime = self.virtual_runtime.get(task.id, 0.0)
        self.virtual_runtime[task.id] = base_runtime + self._estimated_virtual_runtime(task)

    def _estimated_virtual_runtime(self, task: Task) -> float:
        weight = max(task.priority + 1, 1)
        return task.duration / weight


def get_scheduler(name: str) -> Scheduler:
    schedulers = {
        "first_fit": FirstFitScheduler,
        "best_fit": BestFitScheduler,
        "worst_fit": WorstFitScheduler,
        "round_robin": RoundRobinScheduler,
        "least_loaded": LeastLoadedScheduler,
        "cfs_like": CFSLikeScheduler,
    }
    try:
        return schedulers[name]()
    except KeyError as exc:
        raise ValueError(f"Unsupported scheduler: {name}") from exc
