from uuid import UUID

from app.domain.entities.refresh_session import RefreshSession
from app.infrastructure.database.models.refresh_session_model import RefreshSessionModel


class RefreshSessionMapper:
    @staticmethod
    def to_domain(model: RefreshSessionModel) -> RefreshSession:
        return RefreshSession(
            id=UUID(model.id),
            user_id=UUID(model.user_id),
            jti=UUID(model.jti),
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            revoked_at=model.revoked_at,
        )

    @staticmethod
    def to_model(entity: RefreshSession) -> RefreshSessionModel:
        return RefreshSessionModel(
            id=str(entity.id),
            user_id=str(entity.user_id),
            jti=str(entity.jti),
            token_hash=entity.token_hash,
            expires_at=entity.expires_at,
            created_at=entity.created_at,
            revoked_at=entity.revoked_at,
        )

    @staticmethod
    def update_model(model: RefreshSessionModel, entity: RefreshSession) -> None:
        model.revoked_at = entity.revoked_at
