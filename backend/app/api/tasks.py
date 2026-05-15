from fastapi import APIRouter, HTTPException

from app.core.sample_data import load_sample_records
from app.core import store
from app.schemas.task import TaskCreate, TaskRead


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks() -> list[TaskRead]:
    return store.list_tasks()


@router.post("", response_model=TaskRead)
def create_task(payload: TaskCreate) -> TaskRead:
    return store.create_task(payload)


@router.put("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskCreate) -> TaskRead:
    task = store.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/generate", response_model=list[TaskRead])
def generate_tasks() -> list[TaskRead]:
    samples = [
        TaskCreate(name="task-1", required_cpu=2, required_memory=4, duration=5, submit_time=0),
        TaskCreate(name="task-2", required_cpu=3, required_memory=6, duration=8, submit_time=1),
        TaskCreate(name="task-3", required_cpu=1, required_memory=2, duration=3, submit_time=2),
    ]
    return [store.create_task(task) for task in samples]


@router.post("/import-sample", response_model=list[TaskRead])
def import_sample_tasks(dataset: str = "default") -> list[TaskRead]:
    samples = load_sample_records("tasks", dataset)
    return [store.create_task(TaskCreate(**task)) for task in samples]


@router.delete("/{task_id}")
def delete_task(task_id: int) -> dict[str, bool]:
    if not store.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}
