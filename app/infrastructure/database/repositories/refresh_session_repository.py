from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.interfaces.repositories.refresh_session_repository import (
    RefreshSessionRepository,
)
from app.domain.entities.refresh_session import RefreshSession
from app.infrastructure.database.mappers.refresh_session_mapper import (
    RefreshSessionMapper,
)
from app.infrastructure.database.models.refresh_session_model import RefreshSessionModel


class SqlAlchemyRefreshSessionRepository(RefreshSessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_token_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshSession | None:
        stmt = (
            select(RefreshSessionModel)
            .where(RefreshSessionModel.token_hash == token_hash)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return None if model is None else RefreshSessionMapper.to_domain(model)

    async def add(self, refresh_session: RefreshSession) -> None:
        model = RefreshSessionMapper.to_model(refresh_session)
        self.session.add(model)
        await self.session.flush()

    async def save(self, refresh_session: RefreshSession) -> None:
        model = await self.session.get(RefreshSessionModel, str(refresh_session.id))
        if model is None:
            await self.add(refresh_session)
            return
        RefreshSessionMapper.update_model(model, refresh_session)
        await self.session.flush()
