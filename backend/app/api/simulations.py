from fastapi import APIRouter, HTTPException

from app.core import store
from app.schemas.simulation import SimulationCompareRequest, SimulationRunRequest
from app.simulation.domain import Machine, Task
from app.simulation.engine import run_simulation


router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.post("/run")
def run(payload: SimulationRunRequest) -> dict:
    try:
        result = run_simulation(
            machines=[Machine(**machine.model_dump()) for machine in store.list_machines()],
            tasks=[Task(**task.model_dump()) for task in store.list_tasks()],
            algorithm=payload.algorithm,
            max_time=payload.max_time,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


@router.post("/compare")
def compare(payload: SimulationCompareRequest) -> dict:
    machine_records = store.list_machines()
    task_records = store.list_tasks()
    results = []

    try:
        for algorithm in payload.algorithms:
            result = run_simulation(
                machines=[Machine(**machine.model_dump()) for machine in machine_records],
                tasks=[Task(**task.model_dump()) for task in task_records],
                algorithm=algorithm,
                max_time=payload.max_time,
            )
            results.append(result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "max_time": payload.max_time,
        "algorithms": payload.algorithms,
        "results": results,
    }

