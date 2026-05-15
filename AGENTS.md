# AGENTS.md

## Project Goal
- Build a small cloud data-center resource scheduling simulator for teaching/demo use.
- The simulator should let users configure physical machines, submit virtual tasks, choose scheduling algorithms, run a discrete-time simulation, and view results in a Vue UI.
- Keep the first version compact: CPU and memory only; no disk, network bandwidth, live migration, host failure, auto-scaling, multi-tenant fairness, genetic algorithms, or reinforcement learning.

## Confirmed Stack
- Backend: Python + FastAPI.
- API server: Uvicorn, normally started with `uvicorn app.main:app --reload` from `backend/`.
- Database: SQLite with Python `sqlite3` and raw SQL.
- Validation/schema layer: Pydantic.
- Frontend: Vue 3.
- Charts: ECharts.
- HTTP client: Axios.
- Local dev uses two services: backend on `http://127.0.0.1:8000`, frontend on `http://127.0.0.1:5173`.

## Repository Layout
- `backend/app/main.py`: FastAPI application entrypoint; must expose `app = FastAPI()`.
- `backend/app/api/`: API routers for machines, tasks, and simulations.
- `backend/app/core/`: backend settings and shared infrastructure.
- `backend/app/models/`: reserved for future persistence-related models or SQL notes if needed.
- `backend/app/schemas/`: Pydantic request/response schemas.
- `backend/app/schedulers/`: scheduling algorithm implementations.
- `backend/app/simulation/`: discrete-time simulation engine, cluster state, and metrics.
- `backend/tests/`: backend tests.
- `frontend/src/api/`: Axios API wrappers.
- `frontend/src/components/`: reusable UI/chart components.
- `frontend/src/views/`: page-level Vue views.
- `frontend/src/router/`: Vue router setup.
- `docs/`: design notes, API docs, algorithm docs, and user guide.
- `data/`: local SQLite database and sample datasets; do not commit generated database files unless explicitly requested.
- `scripts/`: helper scripts for local setup or sample data generation.

## MVP Scope
- Physical machine fields: name, total CPU, total memory, enabled/status.
- Task fields: name, required CPU, required memory, duration, submit time, optional priority, optional deadline.
- Simulation input: machine list, task list, selected scheduling algorithm, maximum simulation time.
- Simulation output: task placement/execution timeline, per-machine resource usage over time, final metrics.
- Required metrics: average CPU utilization, average memory utilization, average waiting time, average turnaround time, success rate, rejection rate, makespan, load-balance score.
- Load-balance score can be based on variance of machine CPU utilization; lower variance means better balance.

## Scheduling Algorithms
- Implement these first: `first_fit`, `best_fit`, `worst_fit`, `round_robin`.
- Add Linux-inspired algorithms after the MVP works: `least_loaded`, `cfs_like`.
- Optional later algorithms: `priority`, `sjf`, `edf`, `balanced`, `quota_aware`.
- Prefer separating queue selection from machine placement if the design grows: queue policies choose tasks; placement policies choose machines.

## API Targets
- `GET /api/machines`
- `POST /api/machines`
- `DELETE /api/machines/{id}`
- `POST /api/machines/batch`
- `GET /api/tasks`
- `POST /api/tasks`
- `DELETE /api/tasks/{id}`
- `POST /api/tasks/generate`
- `POST /api/simulations/run`
- `GET /api/simulations/{id}`
- `GET /api/simulations/{id}/results`
- `GET /api/simulations/{id}/metrics`

## Development Order
1. Create minimal backend package structure and `app.main:app`.
2. Implement pure Python simulation core before connecting the API, database, or frontend.
3. Add domain objects for physical machines, tasks, cluster state, allocation, and release.
4. Implement `first_fit`, `best_fit`, `worst_fit`, and `round_robin` against fixed in-memory test data.
5. Implement metric calculation and verify with small deterministic examples.
6. Add FastAPI routers and schemas for machines, tasks, and simulation runs.
7. Add SQLite persistence for configurations and simulation results.
8. Create Vue pages for machine configuration, task configuration, simulation run, and result analysis.
9. Add ECharts visualizations for CPU/memory utilization, task timeline/Gantt view, and metric cards.
10. Add documentation for setup, API usage, algorithms, and demo workflow.

## Collaboration Notes
- Keep changes small and directly tied to the current step; avoid implementing advanced algorithms before the MVP works end-to-end.
- Do not add backward-compatibility layers unless persisted data or external API consumers already exist.
- If docs and executable config disagree, trust executable config and update docs.
- Do not assume generated SQLite files are source files; keep sample data scripts or seed JSON separate from local runtime databases.
- When adding commands to README or docs, verify them against the actual project files.
- User-facing frontend UI text should default to Simplified Chinese unless a task explicitly requires another language.

## Coding Guidelines
- Think before coding: state assumptions when the request is ambiguous, surface tradeoffs, and ask instead of silently guessing.
- Prefer the simplest correct implementation; do not add speculative features, abstractions, configurability, or broad error handling that the current task does not need.
- Make surgical changes only; avoid unrelated refactors, formatting churn, or cleanup outside the requested work.
- Match the existing style of nearby files once code exists, even if a different style would also work.
- Remove imports, variables, or helpers made unused by your own changes, but do not delete pre-existing dead code unless asked.
- For multi-step work, define success criteria and verify them with focused checks such as a single test, backend import check, frontend build, or documented command.
- If a change grows large, pause and simplify before continuing; every changed line should trace directly to the user's request.

## UI Language
- Default all user-facing frontend labels, buttons, status text, empty states, and help text to Simplified Chinese.
- Keep internal code identifiers, filenames, route paths, and API field names in English unless there is a strong reason to change them.

## Documentation To Create
- `README.md`: project overview, stack, setup, run commands, and demo flow.
- `docs/architecture.md`: backend/frontend/simulation architecture and data flow.
- `docs/api.md`: endpoint list with request/response examples.
- `docs/algorithms.md`: scheduling algorithm definitions and expected behavior.
- `docs/tasks.md`: current implementation checklist and future extensions.

## Pending Tasks
- Add root `README.md`.
- Add backend dependency file, likely `backend/requirements.txt` or `backend/pyproject.toml`.
- Add minimal FastAPI app entrypoint at `backend/app/main.py`.
- Add backend modules for database, models, schemas, routers, schedulers, simulation engine, and metrics.
- Add backend tests for scheduler behavior and metric calculation.
- Add frontend Vite/Vue project files and install dependencies.
- Add Vue router, API wrappers, pages, reusable tables, metric cards, and charts.
- Add sample machine/task data for demos.
- Add documentation files listed above.
