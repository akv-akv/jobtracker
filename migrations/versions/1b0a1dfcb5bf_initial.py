"""Initial

Revision ID: 1b0a1dfcb5bf
Revises: 652dd23e8763
Create Date: 2024-12-25 11:03:12.554839

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1b0a1dfcb5bf"
down_revision: Union[str, None] = "652dd23e8763"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("resume_main_info", "version")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "resume_main_info",
        sa.Column("version", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    # ### end Alembic commands ###