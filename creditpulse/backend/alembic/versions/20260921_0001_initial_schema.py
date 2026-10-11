"""Create users, financial profiles, and credit applications.

Revision ID: 20260921_0001
Revises:
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260921_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_table(
        "financial_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("revenu_mensuel", sa.Float(), nullable=False),
        sa.Column("dettes_actuelles", sa.Float(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("anciennete_emploi", sa.Float(), nullable=False),
        sa.Column("nombre_credits_en_cours", sa.Integer(), nullable=False),
        sa.Column("historique_paiement", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_financial_profiles_id"), "financial_profiles", ["id"], unique=False)
    op.create_table(
        "credit_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("requested_amount", sa.Float(), nullable=False),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("probability_default", sa.Float(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_credit_applications_id"), "credit_applications", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_credit_applications_id"), table_name="credit_applications")
    op.drop_table("credit_applications")
    op.drop_index(op.f("ix_financial_profiles_id"), table_name="financial_profiles")
    op.drop_table("financial_profiles")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
