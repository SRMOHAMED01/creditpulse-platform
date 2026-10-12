"""Add status field for event-driven credit applications (Palier C).

Revision ID: 20261012_0004_status_field
Revises: 20261011_0003_feature_store
Create Date: 2026-10-12
"""

import sqlalchemy as sa
from alembic import op

revision = "20261012_0004_status_field"
down_revision = "20261011_0003_feature_store"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("credit_applications", sa.Column("status", sa.String(), nullable=False, server_default="completed"))
    op.add_column("credit_applications", sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True))
    # Allow nullable score/probability/decision for pending async requests
    op.alter_column("credit_applications", "score", existing_type=sa.Integer(), nullable=True)
    op.alter_column("credit_applications", "probability_default", existing_type=sa.Float(), nullable=True)
    op.alter_column("credit_applications", "decision", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    op.drop_column("credit_applications", "scored_at")
    op.drop_column("credit_applications", "status")
    op.alter_column("credit_applications", "decision", existing_type=sa.String(), nullable=False)
    op.alter_column("credit_applications", "probability_default", existing_type=sa.Float(), nullable=False)
    op.alter_column("credit_applications", "score", existing_type=sa.Integer(), nullable=False)
