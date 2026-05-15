from pydantic import BaseModel, Field


class MachineCreate(BaseModel):
    name: str
    total_cpu: int = Field(gt=0)
    total_memory: int = Field(gt=0)
    enabled: bool = True


class MachineRead(MachineCreate):
    id: int
