from pydantic import BaseModel, Field


class SimulationRunRequest(BaseModel):
    algorithm: str = "first_fit"
    max_time: int = Field(default=100, gt=0)
