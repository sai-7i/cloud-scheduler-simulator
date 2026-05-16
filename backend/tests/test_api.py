from fastapi.testclient import TestClient

from app.main import app


def test_update_machine_persists_changes() -> None:
    client = TestClient(app)

    created = client.post(
        "/api/machines",
        json={"name": "node-a", "total_cpu": 4, "total_memory": 8192, "enabled": True},
    )
    assert created.status_code == 200
    machine_id = created.json()["id"]

    updated = client.put(
        f"/api/machines/{machine_id}",
        json={"name": "node-a-updated", "total_cpu": 6, "total_memory": 12288, "enabled": False},
    )
    assert updated.status_code == 200
    assert updated.json() == {
        "id": machine_id,
        "name": "node-a-updated",
        "total_cpu": 6,
        "total_memory": 12288,
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
            "required_memory": 4096,
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
            "required_memory": 6144,
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
        "required_memory": 6144,
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
        json={"name": "missing", "total_cpu": 4, "total_memory": 8192, "enabled": True},
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
            "required_memory": 2048,
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
            {"name": "node-a", "total_cpu": 4, "total_memory": 8192, "enabled": True},
            {"name": "node-b", "total_cpu": 6, "total_memory": 12288, "enabled": True},
        ],
    )
    assert response.status_code == 200

    generated = client.post("/api/tasks/generate")
    assert generated.status_code == 200
    generated_tasks = generated.json()
    assert [task["required_memory"] for task in generated_tasks] == [4096, 6144, 2048]

    simulation = client.post(
        "/api/simulations/run",
        json={"algorithm": "first_fit", "max_time": 20},
    )
    assert simulation.status_code == 200

    metrics = simulation.json()["metrics"]
    assert metrics["success_rate"] == 1
    assert metrics["rejection_rate"] == 0


def test_run_simulation_returns_result_without_saving_history_id() -> None:
    client = TestClient(app)

    client.post(
        "/api/machines/batch",
        json=[
            {"name": "node-a", "total_cpu": 4, "total_memory": 8192, "enabled": True},
            {"name": "node-b", "total_cpu": 6, "total_memory": 12288, "enabled": True},
        ],
    )
    client.post("/api/tasks/generate")

    response = client.post(
        "/api/simulations/run",
        json={"algorithm": "first_fit", "max_time": 20},
    )

    assert response.status_code == 200
    assert response.json()["algorithm"] == "first_fit"
    assert "id" not in response.json()
    assert "timeline" in response.json()
    assert "resource_history" in response.json()
    assert "metrics" in response.json()


def test_compare_simulations_returns_results() -> None:
    client = TestClient(app)

    client.post(
        "/api/machines/batch",
        json=[
            {"name": "node-a", "total_cpu": 4, "total_memory": 8192, "enabled": True},
            {"name": "node-b", "total_cpu": 6, "total_memory": 12288, "enabled": True},
        ],
    )
    client.post("/api/tasks/generate")

    response = client.post(
        "/api/simulations/compare",
        json={"algorithms": ["first_fit", "least_loaded"], "max_time": 20},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["max_time"] == 20
    assert body["algorithms"] == ["first_fit", "least_loaded"]
    assert [result["algorithm"] for result in body["results"]] == ["first_fit", "least_loaded"]
    assert all(result["metrics"]["success_rate"] == 1 for result in body["results"])


def test_compare_simulations_rejects_unknown_algorithm() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/simulations/compare",
        json={"algorithms": ["missing"], "max_time": 20},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported scheduler: missing"


def test_import_sample_machines_creates_records() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/machines",
        json={"name": "old-node", "total_cpu": 1, "total_memory": 1024, "enabled": True},
    )
    assert created.status_code == 200

    response = client.post("/api/machines/import-sample")

    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]["name"] == "cpu-heavy-node"
    assert "old-node" not in [machine["name"] for machine in response.json()]


def test_import_sample_tasks_creates_records() -> None:
    client = TestClient(app)
    created = client.post(
        "/api/tasks",
        json={
            "name": "old-task",
            "required_cpu": 1,
            "required_memory": 1024,
            "duration": 1,
            "submit_time": 0,
        },
    )
    assert created.status_code == 200

    response = client.post("/api/tasks/import-sample")

    assert response.status_code == 200
    assert len(response.json()) == 8
    assert response.json()[0]["name"] == "cpu-batch-large"
    assert "old-task" not in [task["name"] for task in response.json()]


def test_delete_all_machines_removes_records() -> None:
    client = TestClient(app)
    client.post("/api/machines/import-sample")

    response = client.delete("/api/machines")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": 4}
    assert client.get("/api/machines").json() == []


def test_delete_all_tasks_removes_records() -> None:
    client = TestClient(app)
    client.post("/api/tasks/import-sample")

    response = client.delete("/api/tasks")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": 8}
    assert client.get("/api/tasks").json() == []


def test_import_balanced_machine_dataset_creates_balanced_records() -> None:
    client = TestClient(app)

    response = client.post("/api/machines/import-sample?dataset=balanced")

    assert response.status_code == 200
    assert [machine["name"] for machine in response.json()] == [
        "balanced-a",
        "balanced-b",
        "balanced-c",
        "balanced-d",
    ]


def test_import_stress_task_dataset_creates_stress_records() -> None:
    client = TestClient(app)

    response = client.post("/api/tasks/import-sample?dataset=stress")

    assert response.status_code == 200
    assert [task["name"] for task in response.json()] == [
        "stress-cpu-blocker",
        "stress-memory-blocker",
        "stress-balanced-blocker",
        "stress-urgent-small-1",
        "stress-urgent-small-2",
        "stress-cpu-late",
        "stress-memory-late",
        "stress-oversized-rejected",
    ]


def test_import_all_named_sample_datasets() -> None:
    client = TestClient(app)
    datasets = ["default", "balanced", "stress", "fragmented", "priority", "deadline", "burst"]

    for dataset in datasets:
        machines = client.post(f"/api/machines/import-sample?dataset={dataset}")
        tasks = client.post(f"/api/tasks/import-sample?dataset={dataset}")

        assert machines.status_code == 200
        assert tasks.status_code == 200
        assert len(machines.json()) > 0
        assert len(tasks.json()) > 0


def test_import_missing_sample_dataset_returns_404() -> None:
    client = TestClient(app)

    response = client.post("/api/machines/import-sample?dataset=missing")

    assert response.status_code == 404
    assert response.json()["detail"] == "Sample dataset not found: missing"
