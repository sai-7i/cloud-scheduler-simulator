import json
from pathlib import Path

from fastapi import HTTPException

from app.core.database import get_project_root


DATASET_FILES = {
    "machines": {
        "default": "sample_machines.json",
        "balanced": "sample_machines_balanced.json",
        "stress": "sample_machines_stress.json",
    },
    "tasks": {
        "default": "sample_tasks.json",
        "balanced": "sample_tasks_balanced.json",
        "stress": "sample_tasks_stress.json",
    },
}


def load_sample_records(kind: str, dataset: str) -> list[dict]:
    try:
        filename = DATASET_FILES[kind][dataset]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Sample dataset not found: {dataset}") from exc

    sample_path = get_project_root() / "data" / filename
    return json.loads(sample_path.read_text(encoding="utf-8"))
