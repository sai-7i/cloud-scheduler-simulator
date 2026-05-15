from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import machines, simulations, tasks
from app.core.database import initialize_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Cloud Resource Scheduling Simulator", lifespan=lifespan)

app.include_router(machines.router)
app.include_router(tasks.router)
app.include_router(simulations.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
