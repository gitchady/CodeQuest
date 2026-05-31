from abc import ABC, abstractmethod

from app.domain.entities.refresh_session import RefreshSession


class RefreshSessionRepository(ABC):
    @abstractmethod
    async def get_by_token_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshSession | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, refresh_session: RefreshSession) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save(self, refresh_session: RefreshSession) -> None:
        raise NotImplementedError
