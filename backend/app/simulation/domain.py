from dataclasses import dataclass


@dataclass
class Machine:
    id: int
    name: str
    total_cpu: int
    total_memory: int
    enabled: bool = True
    used_cpu: int = 0
    used_memory: int = 0

    @property
    def available_cpu(self) -> int:
        return self.total_cpu - self.used_cpu

    @property
    def available_memory(self) -> int:
        return self.total_memory - self.used_memory

    def can_fit(self, task: "Task") -> bool:
        return (
            self.enabled
            and self.available_cpu >= task.required_cpu
            and self.available_memory >= task.required_memory
        )


@dataclass
class Task:
    id: int
    name: str
    required_cpu: int
    required_memory: int
    duration: int
    submit_time: int
    priority: int = 0
    deadline: int | None = None
    start_time: int | None = None
    finish_time: int | None = None
    machine_id: int | None = None
    rejected: bool = False

    @property
    def is_finished(self) -> bool:
        return self.finish_time is not None
