"""refresh sessions

Revision ID: 6ec0f0e060b2
Revises: a156638bab87
Create Date: 2026-05-31 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6ec0f0e060b2'
down_revision: Union[str, Sequence[str], None] = 'a156638bab87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'refresh_sessions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('jti', sa.String(length=36), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_refresh_sessions_expires_at'),
        'refresh_sessions',
        ['expires_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_refresh_sessions_jti'),
        'refresh_sessions',
        ['jti'],
        unique=True,
    )
    op.create_index(
        op.f('ix_refresh_sessions_token_hash'),
        'refresh_sessions',
        ['token_hash'],
        unique=True,
    )
    op.create_index(
        op.f('ix_refresh_sessions_user_id'),
        'refresh_sessions',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_refresh_sessions_user_id'), table_name='refresh_sessions')
    op.drop_index(op.f('ix_refresh_sessions_token_hash'), table_name='refresh_sessions')
    op.drop_index(op.f('ix_refresh_sessions_jti'), table_name='refresh_sessions')
    op.drop_index(op.f('ix_refresh_sessions_expires_at'), table_name='refresh_sessions')
    op.drop_table('refresh_sessions')
