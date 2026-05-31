# FastAPI Education

Backend API for an online education platform. The project uses a clean architecture style with separate domain, application, infrastructure and presentation layers.

## Features

- Public course catalogue and course structure endpoints.
- JWT authentication with student, author and admin roles.
- Opaque refresh-token sessions with server-side hash storage, `jti` tracking and strict JWT access-token validation.
- API rate limiting for abuse protection.
- Admin CRUD for courses, modules, sections and lectures.
- Interactive questions with answer options and attempt tracking.
- Text tasks with exact, any-of and regex checking.
- Code tasks for Python and Java submissions.
- Asynchronous code-submission processing with Celery, RabbitMQ and Redis result storage.
- Sandboxed code execution through Docker.
- Prometheus metrics and Grafana dashboards.
- Liveness/readiness endpoints and an embedded mini frontend.
- Alembic migrations and async SQLAlchemy persistence.

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy async
- Alembic
- PostgreSQL with `asyncpg`
- SQLite fallback with `aiosqlite`
- Celery
- RabbitMQ
- Redis as Celery result backend
- Prometheus / Grafana
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
DATABASE_URL=postgresql+asyncpg://perminof:perminof@localhost:5432/perminof
# SQLite fallback:
# DATABASE_URL=sqlite+aiosqlite:///./fastapi_education.db
# Docker Compose SQLite fallback:
# COMPOSE_DATABASE_URL=sqlite+aiosqlite:////data/fastapi_education.db
DATABASE_ECHO=false
JWT_SECRET_KEY=change-me-in-local-env
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=43200
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=redis://localhost:6379/1
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

`DATABASE_URL` is the database switch. Use PostgreSQL for the normal runtime. Use the SQLite URL above when PostgreSQL is not available locally.

Docker Compose uses PostgreSQL service DNS by default. Use `COMPOSE_DATABASE_URL` only when you want to override the database URL inside containers.

## Local Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

API docs:

- Student/admin frontend: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Docker Compose

```powershell
docker compose up --build
```

This starts:

- `api` on `http://localhost:8000`
- `postgres` on `localhost:5432`
- `rabbitmq` on `localhost:5672`, management UI on `http://localhost:15672`
- `redis` on `localhost:6379` as Celery result backend
- `worker` as a Celery worker for asynchronous code submissions
- `prometheus` on `http://localhost:9090`
- `grafana` on `http://localhost:3000`

The worker runs Docker inside its container to execute submitted code. This requires privileged Docker support.

For a production-style compose render, copy `.env.production.example` to
`.env.production`, replace all `replace-me` values, then run:

```powershell
docker compose --env-file .env.production -f docker-compose.prod.yml up --build
```

The API image runs `alembic upgrade head` on startup by default. Set
`RUN_MIGRATIONS=0` only when migrations are handled by a separate release step.

## Worker

Run the Celery worker locally:

```powershell
celery -A app.infrastructure.celery_app:celery_app worker --loglevel=info
```

Process one submission manually:

```powershell
python submit.py <submission_id>
```

## Metrics

Prometheus scrapes the API at `/metrics`. Grafana can use Prometheus at
`http://prometheus:9090` inside Docker Compose.

## Health Checks

- `GET /health` returns liveness metadata.
- `GET /ready` checks database access and required broker/result-backend configuration.

## Account Security

Login returns a JWT access token and an opaque refresh token. Use
`POST /api/auth/refresh` with the refresh token to rotate both tokens. Access
JWTs include a token type and `jti` claim. Refresh tokens are random strings,
stored only as hashes in `refresh_sessions`, tracked by server-side `jti`, and
revoked on rotation so an old refresh token cannot be reused.

## Mini Frontend

FastAPI serves a student workspace and author/admin studio at `/`. The workspace
can list courses, open course structure, view lectures/questions/tasks/code
tasks, sign in, and submit learning work. The studio can create courses,
modules, sections and lectures through the existing admin API.

## Rate Limiting

API requests under `/api` are limited per client IP. Configure it with
`RATE_LIMIT_ENABLED`, `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`.

## Tests

```powershell
python -m pip install -r requirements-dev.txt
pytest -q
```

Docker-dependent tests are skipped automatically when Docker is unavailable.

## CI

GitHub Actions runs dependency installation, Docker Compose config rendering,
`ruff`, `mypy`, `pytest`, a PostgreSQL integration-test pass, and `pip-audit`.

## Main API Areas

- `GET /api/courses`
- `GET /api/courses/{course_id}`
- `GET /api/courses/{course_id}/structure`
- `GET /api/lectures/{lecture_id}`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
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

Runtime dependencies are pinned in `requirements.txt`. Development and CI tools
are pinned in `requirements-dev.txt`.
