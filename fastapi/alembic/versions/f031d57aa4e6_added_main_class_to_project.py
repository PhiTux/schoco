"""added main_class to project

Revision ID: f031d57aa4e6
Revises: 48e0ab5941fc
Create Date: 2023-09-30 17:30:06.131495

"""
from typing import Sequence, Union
import sqlmodel

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f031d57aa4e6'
down_revision: Union[str, None] = '48e0ab5941fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('main_class', sqlmodel.sql.sqltypes.AutoString(
    ), nullable=False, server_default='Schoco.java/'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'main_class')
    # ### end Alembic commands ###