from fastapi import APIRouter, HTTPException

from app.core import store
from app.schemas.simulation import SimulationRunRequest
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
    return store.save_simulation(result, payload.max_time)


@router.get("/latest")
def get_latest_simulation() -> dict:
    simulation = store.get_latest_simulation()
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation


@router.get("/{simulation_id}")
def get_simulation(simulation_id: int) -> dict:
    simulation = store.get_simulation(simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {
        "id": simulation["id"],
        "algorithm": simulation["algorithm"],
        "max_time": simulation["max_time"],
    }


@router.get("/{simulation_id}/results")
def get_results(simulation_id: int) -> dict:
    simulation = store.get_simulation(simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return {
        "timeline": simulation["timeline"],
        "resource_history": simulation["resource_history"],
    }


@router.get("/{simulation_id}/metrics")
def get_metrics(simulation_id: int) -> dict:
    simulation = store.get_simulation(simulation_id)
    if simulation is None:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation["metrics"]
