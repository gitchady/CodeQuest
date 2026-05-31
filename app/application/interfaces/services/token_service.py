from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class TokenService(ABC):
    @abstractmethod
    def create_access_token(self, user_id: UUID, role: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_user_id(self, token: str) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def hash_refresh_token(self, token: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_refresh_token_expires_at(self) -> datetime:
        raise NotImplementedError
