from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    name: str
    required_cpu: int = Field(gt=0)
    required_memory: int = Field(gt=0)
    duration: int = Field(gt=0)
    submit_time: int = Field(ge=0)
    priority: int = 0
    deadline: int | None = None


class TaskRead(TaskCreate):
    id: int
