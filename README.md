# FastAPI Education

Backend API for an online education platform. The project uses a clean architecture style with separate domain, application, infrastructure and presentation layers.

## Features

- Public course catalogue and course structure endpoints.
- JWT authentication with student, author and admin roles.
- Admin CRUD for courses, modules, sections and lectures.
- Interactive questions with answer options and attempt tracking.
- Text tasks with exact, any-of and regex checking.
- Code tasks for Python and Java submissions.
- Asynchronous code-submission queue backed by Redis.
- Sandboxed code execution through Docker.
- Alembic migrations and async SQLAlchemy persistence.

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy async
- Alembic
- SQLite with `aiosqlite`
- Redis
- Docker
- pytest / pytest-asyncio

## Project Layout

```text
app/
  application/      Use cases, DTOs, service interfaces
  bootstrap/        Runtime builders for queue and worker wiring
  domain/           Business entities and domain exceptions
  infrastructure/   Database, queues, security and code execution adapters
  presentation/     FastAPI routes, schemas and exception handlers
migrations/         Alembic migrations
tests/              Unit, integration and e2e tests
docker/             Worker entrypoint scripts
```

## Configuration

Create `.env` from `.env.example` and set at least `JWT_SECRET_KEY`.

```env
APP_ENV=development
APP_TITLE=FastAPI Education
APP_DEBUG=true
API_PREFIX=/api
DATABASE_URL=sqlite+aiosqlite:///./fastapi_education.db
DATABASE_ECHO=false
JWT_SECRET_KEY=change-me-in-local-env
REDIS_URL=redis://localhost:6379/0
SUBMISSION_QUEUE_NAME=code-submissions
```

## Local Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API docs:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Docker Compose

```powershell
docker compose up --build
```

This starts:

- `api` on `http://localhost:8000`
- `redis` on `localhost:6379`
- `worker` for asynchronous code submissions

The worker runs Docker inside its container to execute submitted code. This requires privileged Docker support.

## Worker

Run the queue worker locally:

```powershell
python -m app.run_code_submission_worker
```

Process one submission manually:

```powershell
python submit.py <submission_id>
```

## Tests

```powershell
pytest -q
```

Docker-dependent tests are skipped automatically when Docker is unavailable.

## Main API Areas

- `GET /api/courses`
- `GET /api/courses/{course_id}`
- `GET /api/courses/{course_id}/structure`
- `GET /api/lectures/{lecture_id}`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/admin/courses`
- `POST /api/admin/sections/{section_id}/questions`
- `POST /api/admin/sections/{section_id}/tasks`
- `POST /api/admin/sections/{section_id}/code-tasks`
- `POST /api/learning/questions/{question_id}/attempts`
- `POST /api/learning/tasks/{task_id}/attempts`
- `POST /api/learning/code-tasks/{code_task_id}/submissions`
- `GET /api/learning/code-submissions/{submission_id}`

## Dependency Notes

`requirements.txt` currently contains unpinned direct dependencies. For reproducible builds, pin versions or generate a lock file before production deployment.
