from fastapi import APIRouter, HTTPException

from app.core.sample_data import load_sample_records
from app.core import store
from app.schemas.machine import MachineCreate, MachineRead


router = APIRouter(prefix="/api/machines", tags=["machines"])


@router.get("", response_model=list[MachineRead])
def list_machines() -> list[MachineRead]:
    return store.list_machines()


@router.post("", response_model=MachineRead)
def create_machine(payload: MachineCreate) -> MachineRead:
    return store.create_machine(payload)


@router.put("/{machine_id}", response_model=MachineRead)
def update_machine(machine_id: int, payload: MachineCreate) -> MachineRead:
    machine = store.update_machine(machine_id, payload)
    if machine is None:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine


@router.post("/batch", response_model=list[MachineRead])
def create_machines(payload: list[MachineCreate]) -> list[MachineRead]:
    return [store.create_machine(machine) for machine in payload]


@router.post("/import-sample", response_model=list[MachineRead])
def import_sample_machines(dataset: str = "default") -> list[MachineRead]:
    samples = load_sample_records("machines", dataset)
    return [store.create_machine(MachineCreate(**machine)) for machine in samples]


@router.delete("/{machine_id}")
def delete_machine(machine_id: int) -> dict[str, bool]:
    if not store.delete_machine(machine_id):
        raise HTTPException(status_code=404, detail="Machine not found")
    return {"deleted": True}
