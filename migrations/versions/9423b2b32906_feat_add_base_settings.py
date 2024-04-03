"""feat: add base settings

Revision ID: 9423b2b32906
Revises: 91a3a789d1c0
Create Date: 2024-03-30 20:16:42.571716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9423b2b32906'
down_revision: Union[str, None] = '91a3a789d1c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.DDL(
            "INSERT INTO settings(key, value) VALUES ('check_is_enable', 'disable');"
        )
    )


def downgrade() -> None:
    op.execute(sa.DDL("DELETE FROM settings WHERE key = 'check_is_enable'"))
