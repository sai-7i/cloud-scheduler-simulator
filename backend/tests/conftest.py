import os
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("APP_DB_PATH", str(BACKEND_DIR / "tests" / "test.db"))

from app.core.database import initialize_database  # noqa: E402
from app.core import store  # noqa: E402


initialize_database()


def pytest_runtest_setup() -> None:
    store.reset_database()
