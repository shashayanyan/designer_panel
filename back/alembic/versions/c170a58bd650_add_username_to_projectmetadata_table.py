"""Add username to ProjectMetadata table

Revision ID: c170a58bd650
Revises: b79635c9f2fc
Create Date: 2026-05-27 15:08:06.111925

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c170a58bd650"
down_revision: Union[str, Sequence[str], None] = "b79635c9f2fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("project_metadata", sa.Column("username", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_project_metadata_username_user",
        "project_metadata",
        "users",
        ["username"],
        ["username"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_project_metadata_username_user", "project_metadata", type_="foreignkey"
    )
    op.drop_column("project_metadata", "username")
