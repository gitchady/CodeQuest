from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID


@dataclass(slots=True)
class RefreshSession:
    id: UUID
    user_id: UUID
    jti: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime
    revoked_at: datetime | None = None

    def is_active(self, now: datetime) -> bool:
        expires_at = self._as_aware(self.expires_at)
        return self.revoked_at is None and expires_at > self._as_aware(now)

    def revoke(self, now: datetime) -> None:
        self.revoked_at = self._as_aware(now)

    def _as_aware(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
