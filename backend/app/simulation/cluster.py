from app.simulation.domain import Machine, Task


class Cluster:
    def __init__(self, machines: list[Machine]) -> None:
        self.machines = machines

    def allocate(self, machine: Machine, task: Task, current_time: int) -> None:
        machine.used_cpu += task.required_cpu
        machine.used_memory += task.required_memory
        task.machine_id = machine.id
        task.start_time = current_time
        task.finish_time = current_time + task.duration

    def release_finished(self, current_time: int, running_tasks: list[Task]) -> list[Task]:
        still_running = []
        for task in running_tasks:
            if task.finish_time is not None and task.finish_time <= current_time:
                machine = self.get_machine(task.machine_id)
                if machine is not None:
                    machine.used_cpu -= task.required_cpu
                    machine.used_memory -= task.required_memory
            else:
                still_running.append(task)
        return still_running

    def get_machine(self, machine_id: int | None) -> Machine | None:
        for machine in self.machines:
            if machine.id == machine_id:
                return machine
        return None
