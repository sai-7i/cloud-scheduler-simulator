from fastapi.testclient import TestClient

from app.main import app


def test_update_machine_persists_changes() -> None:
    client = TestClient(app)

    created = client.post(
        "/api/machines",
        json={"name": "node-a", "total_cpu": 4, "total_memory": 8, "enabled": True},
    )
    assert created.status_code == 200
    machine_id = created.json()["id"]

    updated = client.put(
        f"/api/machines/{machine_id}",
        json={"name": "node-a-updated", "total_cpu": 6, "total_memory": 12, "enabled": False},
    )
    assert updated.status_code == 200
    assert updated.json() == {
        "id": machine_id,
        "name": "node-a-updated",
        "total_cpu": 6,
        "total_memory": 12,
        "enabled": False,
    }

    listed = client.get("/api/machines")
    assert listed.status_code == 200
    assert listed.json() == [updated.json()]


def test_update_task_persists_changes() -> None:
    client = TestClient(app)

    created = client.post(
        "/api/tasks",
        json={
            "name": "task-a",
            "required_cpu": 2,
            "required_memory": 4,
            "duration": 5,
            "submit_time": 0,
            "priority": 0,
            "deadline": 10,
        },
    )
    assert created.status_code == 200
    task_id = created.json()["id"]

    updated = client.put(
        f"/api/tasks/{task_id}",
        json={
            "name": "task-a-updated",
            "required_cpu": 3,
            "required_memory": 6,
            "duration": 7,
            "submit_time": 1,
            "priority": 2,
            "deadline": 20,
        },
    )
    assert updated.status_code == 200
    assert updated.json() == {
        "id": task_id,
        "name": "task-a-updated",
        "required_cpu": 3,
        "required_memory": 6,
        "duration": 7,
        "submit_time": 1,
        "priority": 2,
        "deadline": 20,
    }

    listed = client.get("/api/tasks")
    assert listed.status_code == 200
    assert listed.json() == [updated.json()]


def test_update_missing_machine_returns_404() -> None:
    client = TestClient(app)

    response = client.put(
        "/api/machines/999",
        json={"name": "missing", "total_cpu": 4, "total_memory": 8, "enabled": True},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Machine not found"


def test_update_missing_task_returns_404() -> None:
    client = TestClient(app)

    response = client.put(
        "/api/tasks/999",
        json={
            "name": "missing",
            "required_cpu": 1,
            "required_memory": 2,
            "duration": 3,
            "submit_time": 0,
            "priority": 0,
            "deadline": None,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_generated_tasks_work_with_demo_sized_machines() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/machines/batch",
        json=[
            {"name": "node-a", "total_cpu": 4, "total_memory": 8, "enabled": True},
            {"name": "node-b", "total_cpu": 6, "total_memory": 12, "enabled": True},
        ],
    )
    assert response.status_code == 200

    generated = client.post("/api/tasks/generate")
    assert generated.status_code == 200
    generated_tasks = generated.json()
    assert [task["required_memory"] for task in generated_tasks] == [4, 6, 2]

    simulation = client.post(
        "/api/simulations/run",
        json={"algorithm": "first_fit", "max_time": 20},
    )
    assert simulation.status_code == 200

    metrics = simulation.json()["metrics"]
    assert metrics["success_rate"] == 1
    assert metrics["rejection_rate"] == 0


def test_get_latest_simulation_returns_newest_result() -> None:
    client = TestClient(app)

    client.post(
        "/api/machines/batch",
        json=[
            {"name": "node-a", "total_cpu": 4, "total_memory": 8, "enabled": True},
            {"name": "node-b", "total_cpu": 6, "total_memory": 12, "enabled": True},
        ],
    )
    client.post("/api/tasks/generate")

    first = client.post(
        "/api/simulations/run",
        json={"algorithm": "first_fit", "max_time": 20},
    )
    second = client.post(
        "/api/simulations/run",
        json={"algorithm": "round_robin", "max_time": 30},
    )

    assert first.status_code == 200
    assert second.status_code == 200

    latest = client.get("/api/simulations/latest")
    assert latest.status_code == 200
    assert latest.json()["id"] == second.json()["id"]
    assert latest.json()["algorithm"] == "round_robin"
    assert latest.json()["max_time"] == 30
    assert "metrics" in latest.json()
    assert "timeline" in latest.json()
    assert "resource_history" in latest.json()


def test_get_latest_simulation_returns_404_when_empty() -> None:
    client = TestClient(app)

    response = client.get("/api/simulations/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == "Simulation not found"


def test_import_sample_machines_creates_records() -> None:
    client = TestClient(app)

    response = client.post("/api/machines/import-sample")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[0]["name"] == "node-a"


def test_import_sample_tasks_creates_records() -> None:
    client = TestClient(app)

    response = client.post("/api/tasks/import-sample")

    assert response.status_code == 200
    assert len(response.json()) == 5
    assert response.json()[0]["name"] == "task-1"


def test_import_balanced_machine_dataset_creates_balanced_records() -> None:
    client = TestClient(app)

    response = client.post("/api/machines/import-sample?dataset=balanced")

    assert response.status_code == 200
    assert [machine["name"] for machine in response.json()] == ["balanced-a", "balanced-b", "balanced-c"]


def test_import_stress_task_dataset_creates_stress_records() -> None:
    client = TestClient(app)

    response = client.post("/api/tasks/import-sample?dataset=stress")

    assert response.status_code == 200
    assert [task["name"] for task in response.json()] == [
        "stress-task-1",
        "stress-task-2",
        "stress-task-3",
        "stress-task-4",
        "stress-task-5",
    ]


def test_import_missing_sample_dataset_returns_404() -> None:
    client = TestClient(app)

    response = client.post("/api/machines/import-sample?dataset=missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sample dataset not found: missing"
