from abc import ABC, abstractmethod

from app.simulation.domain import Machine, Task


class Scheduler(ABC):
    def order_waiting_tasks(self, waiting: list[Task], current_time: int) -> list[Task]:
        return waiting

    @abstractmethod
    def select_machine(self, task: Task, machines: list[Machine]) -> Machine | None:
        pass

    def on_task_scheduled(self, task: Task, current_time: int) -> None:
        return None
