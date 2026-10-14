"""Add status field for event-driven credit applications (Palier C).

Revision ID: 20261012_0004_status_field
Revises: 20261011_0003_feature_store
Create Date: 2026-10-12
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "20261012_0004_status_field"
down_revision = "20261011_0003_feature_store"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # SQLite cannot drop NOT NULL in-place; use batch mode for column changes.
    # New columns can be added directly.
    columns = {col["name"] for col in inspector.get_columns("credit_applications")}

    if "status" not in columns:
        op.add_column("credit_applications", sa.Column("status", sa.String(), nullable=False, server_default="completed"))
    if "scored_at" not in columns:
        op.add_column("credit_applications", sa.Column("scored_at", sa.DateTime(timezone=True), nullable=True))

    # Null out existing rows so the nullable alter succeeds
    with op.batch_alter_table("credit_applications", schema=None) as batch:
        batch.alter_column("score", existing_type=sa.Integer(), nullable=True)
        batch.alter_column("probability_default", existing_type=sa.Float(), nullable=True)
        batch.alter_column("decision", existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("credit_applications", schema=None) as batch:
        batch.drop_column("scored_at")
        batch.drop_column("status")
        batch.alter_column("decision", existing_type=sa.String(), nullable=False)
        batch.alter_column("probability_default", existing_type=sa.Float(), nullable=False)
        batch.alter_column("score", existing_type=sa.Integer(), nullable=False)
