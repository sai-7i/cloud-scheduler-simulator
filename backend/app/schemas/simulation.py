from pydantic import BaseModel, Field


class SimulationRunRequest(BaseModel):
    algorithm: str = "first_fit"
    max_time: int = Field(default=100, gt=0)


class SimulationCompareRequest(BaseModel):
    algorithms: list[str] = Field(
        default_factory=lambda: [
            "first_fit",
            "best_fit",
            "worst_fit",
            "round_robin",
            "least_loaded",
            "cfs_like",
        ],
        min_length=1,
    )
    max_time: int = Field(default=100, gt=0)
