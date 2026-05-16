from app.core.database import get_connection
from app.schemas.machine import MachineCreate, MachineRead
from app.schemas.task import TaskCreate, TaskRead


def list_machines() -> list[MachineRead]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, total_cpu, total_memory, enabled FROM machines ORDER BY id"
        ).fetchall()
    return [
        MachineRead(
            id=row["id"],
            name=row["name"],
            total_cpu=row["total_cpu"],
            total_memory=row["total_memory"],
            enabled=bool(row["enabled"]),
        )
        for row in rows
    ]


def create_machine(payload: MachineCreate) -> MachineRead:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO machines (name, total_cpu, total_memory, enabled)
            VALUES (?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.total_cpu,
                payload.total_memory,
                int(payload.enabled),
            ),
        )
        machine_id = cursor.lastrowid
        assert machine_id is not None
    return MachineRead(id=machine_id, **payload.model_dump())


def update_machine(machine_id: int, payload: MachineCreate) -> MachineRead | None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE machines
            SET name = ?, total_cpu = ?, total_memory = ?, enabled = ?
            WHERE id = ?
            """,
            (
                payload.name,
                payload.total_cpu,
                payload.total_memory,
                int(payload.enabled),
                machine_id,
            ),
        )
    if cursor.rowcount == 0:
        return None
    return MachineRead(id=machine_id, **payload.model_dump())


def delete_machine(machine_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM machines WHERE id = ?", (machine_id,))
    return cursor.rowcount > 0


def delete_all_machines() -> int:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM machines")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'machines'")
    return cursor.rowcount


def list_tasks() -> list[TaskRead]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, required_cpu, required_memory, duration, submit_time, priority, deadline
            FROM tasks
            ORDER BY id
            """
        ).fetchall()
    return [
        TaskRead(
            id=row["id"],
            name=row["name"],
            required_cpu=row["required_cpu"],
            required_memory=row["required_memory"],
            duration=row["duration"],
            submit_time=row["submit_time"],
            priority=row["priority"],
            deadline=row["deadline"],
        )
        for row in rows
    ]


def create_task(payload: TaskCreate) -> TaskRead:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (
                name,
                required_cpu,
                required_memory,
                duration,
                submit_time,
                priority,
                deadline
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                payload.required_cpu,
                payload.required_memory,
                payload.duration,
                payload.submit_time,
                payload.priority,
                payload.deadline,
            ),
        )
        task_id = cursor.lastrowid
        assert task_id is not None
    return TaskRead(id=task_id, **payload.model_dump())


def update_task(task_id: int, payload: TaskCreate) -> TaskRead | None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET name = ?, required_cpu = ?, required_memory = ?, duration = ?, submit_time = ?, priority = ?, deadline = ?
            WHERE id = ?
            """,
            (
                payload.name,
                payload.required_cpu,
                payload.required_memory,
                payload.duration,
                payload.submit_time,
                payload.priority,
                payload.deadline,
                task_id,
            ),
        )
    if cursor.rowcount == 0:
        return None
    return TaskRead(id=task_id, **payload.model_dump())


def delete_task(task_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cursor.rowcount > 0


def delete_all_tasks() -> int:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM tasks")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'tasks'")
    return cursor.rowcount


def reset_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            DELETE FROM tasks;
            DELETE FROM machines;
            DELETE FROM sqlite_sequence WHERE name IN ('machines', 'tasks');
            """
        )
