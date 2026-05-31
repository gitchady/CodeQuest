from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.infrastructure.config import get_settings
from app.infrastructure.monitoring import register_prometheus_metrics
from app.infrastructure.rate_limiting import register_rate_limiting
from app.presentation.api.handlers import register_exception_handlers
from app.presentation.api.routes import router as api_router
from app.presentation.api.routes.health import router as health_router


STATIC_DIR = Path(__file__).resolve().parent / 'presentation' / 'static'


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.api.title,
        debug=settings.api.debug,
        description=(
            "Online school API built with clean architecture. "
            "At the first stage, the application supports public content reading, "
            "JWT access authentication, opaque refresh sessions, role-based access control and administrative "
            "management of courses, modules, sections and lectures."
        ),
        version="1.0.0",
        openapi_tags=[
            {
                "name": "Content",
                "description": "Public endpoints for reading courses, course structure and lectures.",
            },
            {
                'name': 'Admin',
                'description': 'Management endpoints for authors and administrators who create and modify learning content.',
            },
            {
                'name': 'Auth',
                'description': 'Endpoints for registration, login, current user lookup and JWT token issuing.',
            },
            {
                'name': 'Learning',
                'description': 'Authenticated endpoints for question attempts, answer submission and learning results.',
            },
        ],
    )
    register_prometheus_metrics(app)
    register_rate_limiting(app, settings.rate_limit, settings.api.prefix)
    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(api_router)

    app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

    @app.get('/', include_in_schema=False)
    async def frontend() -> FileResponse:
        return FileResponse(STATIC_DIR / 'index.html')

    return app


app = create_app()
