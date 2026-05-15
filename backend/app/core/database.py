import os
import sqlite3
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_database_path() -> Path:
    configured_path = os.getenv("APP_DB_PATH")
    if configured_path:
        return Path(configured_path)
    return get_project_root() / "data" / "simulator.db"


def get_connection() -> sqlite3.Connection:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS machines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                total_cpu INTEGER NOT NULL,
                total_memory INTEGER NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                required_cpu INTEGER NOT NULL,
                required_memory INTEGER NOT NULL,
                duration INTEGER NOT NULL,
                submit_time INTEGER NOT NULL,
                priority INTEGER NOT NULL DEFAULT 0,
                deadline INTEGER NULL
            );

            CREATE TABLE IF NOT EXISTS simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                algorithm TEXT NOT NULL,
                max_time INTEGER NOT NULL,
                timeline_json TEXT NOT NULL,
                resource_history_json TEXT NOT NULL,
                metrics_json TEXT NOT NULL
            );
            """
        )
