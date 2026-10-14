"""feature_store table for Palier B dbt pipeline.

Revision ID: 20261011_0003_feature_store
Revises: 20261008_0002_assessment_history
Create Date: 2026-10-11 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20261011_0003_feature_store"
down_revision = "20261008_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feature_store",
        sa.Column("profile_id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("revenu_mensuel", sa.Float(), nullable=False),
        sa.Column("dettes_actuelles", sa.Float(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("anciennete_emploi", sa.Float(), nullable=False),
        sa.Column("nombre_credits_en_cours", sa.Integer(), nullable=False),
        sa.Column("historique_paiement", sa.Float(), nullable=False),
        sa.Column("dti_ratio", sa.Float(), nullable=False),
        sa.Column("score_regularite", sa.Float(), nullable=True),
        sa.Column("profile_updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_feature_store_user_id", "feature_store", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_feature_store_user_id", table_name="feature_store")
    op.drop_table("feature_store")
