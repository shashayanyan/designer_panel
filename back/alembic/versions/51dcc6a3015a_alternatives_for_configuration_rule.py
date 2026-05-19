"""alternatives for configuration_rule

Revision ID: 51dcc6a3015a
Revises: 9c00b9fef082
Create Date: 2026-05-04 15:12:49.725004

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "51dcc6a3015a"
down_revision: Union[str, Sequence[str], None] = "9c00b9fef082"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "configuration_rule",
        sa.Column("alternative_catalog_ref", sa.String(), nullable=True),
    )
    op.add_column(
        "configuration_rule",
        sa.Column("outdoor_alternative_catalog_ref", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("configuration_rule", "outdoor_alternative_catalog_ref")
    op.drop_column("configuration_rule", "alternative_catalog_ref")
