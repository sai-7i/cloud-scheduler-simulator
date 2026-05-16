from app.core.sample_data import load_sample_records
from app.simulation.domain import Machine, Task
from app.simulation.engine import run_simulation


ALGORITHMS = ["first_fit", "best_fit", "worst_fit", "round_robin", "least_loaded", "cfs_like"]


def test_priority_dataset_favors_cfs_like_for_waiting_and_deadlines() -> None:
    results = _run_dataset("priority")

    assert _best_algorithms(results, "average_waiting_time", min) == ["cfs_like"]
    assert _best_algorithms(results, "deadline_miss_rate", min) == ["cfs_like"]


def test_balanced_dataset_favors_distribution_algorithms_for_load_balance() -> None:
    results = _run_dataset("balanced")

    assert _best_algorithms(results, "average_cpu_load_balance_score", min) == [
        "worst_fit",
        "round_robin",
        "least_loaded",
    ]


def test_sample_datasets_do_not_all_favor_first_fit() -> None:
    dataset_metric_winners = {
        "balanced": _best_algorithms(_run_dataset("balanced"), "average_cpu_load_balance_score", min),
        "fragmented": _best_algorithms(_run_dataset("fragmented"), "average_cpu_load_balance_score", min),
        "priority": _best_algorithms(_run_dataset("priority"), "average_waiting_time", min),
    }

    assert any("first_fit" not in winners for winners in dataset_metric_winners.values())


def _run_dataset(dataset: str) -> dict[str, dict]:
    machines_data = load_sample_records("machines", dataset)
    tasks_data = load_sample_records("tasks", dataset)
    results = {}
    for algorithm in ALGORITHMS:
        machines = [Machine(id=index + 1, **record) for index, record in enumerate(machines_data)]
        tasks = [Task(id=index + 1, **record) for index, record in enumerate(tasks_data)]
        results[algorithm] = run_simulation(machines, tasks, algorithm, max_time=20)["metrics"]
    return results


def _best_algorithms(results: dict[str, dict], metric_name: str, selector) -> list[str]:
    best_value = selector(metrics[metric_name] for metrics in results.values())
    return [algorithm for algorithm, metrics in results.items() if metrics[metric_name] == best_value]
