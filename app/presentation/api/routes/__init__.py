from fastapi import APIRouter

from app.infrastructure.config import get_settings
from app.presentation.api.routes.admin import router as admin_router
from app.presentation.api.routes.auth import router as auth_router
from app.presentation.api.routes.content import router as content_router
from app.presentation.api.routes.interactive_admin import router as interactive_admin_router
from app.presentation.api.routes.learning import router as learning_router
from app.presentation.api.routes.task_admin import router as task_admin_router

settings = get_settings()

router = APIRouter(prefix=settings.api.prefix)
router.include_router(content_router)
router.include_router(admin_router)
router.include_router(auth_router)

router.include_router(interactive_admin_router)

router.include_router(learning_router)


router.include_router(task_admin_router)