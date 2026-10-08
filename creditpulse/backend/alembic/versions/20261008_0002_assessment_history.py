"""Store assessment inputs, explanations, and artifact versions.

Existing rows keep null metadata because their original inputs are unknown.
"""
from alembic import op
import sqlalchemy as sa

revision = "20261008_0002"
down_revision = "20260921_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("credit_applications", sa.Column("input_snapshot", sa.JSON(), nullable=True))
    op.add_column("credit_applications", sa.Column("explanation", sa.JSON(), nullable=True))
    op.add_column("credit_applications", sa.Column("model_version", sa.String(64), nullable=True))
    op.create_index("ix_credit_applications_user_created", "credit_applications", ["user_id", "created_at", "id"])


def downgrade():
    op.drop_index("ix_credit_applications_user_created", table_name="credit_applications")
    op.drop_column("credit_applications", "model_version")
    op.drop_column("credit_applications", "explanation")
    op.drop_column("credit_applications", "input_snapshot")
