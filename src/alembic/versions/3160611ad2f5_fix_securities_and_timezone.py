"""fix securities and timezone

Revision ID: 3160611ad2f5
Revises: 088c06118695
Create Date: 2024-04-02 21:08:23.717379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3160611ad2f5'
down_revision: Union[str, None] = '088c06118695'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('securities', 'uid')
    op.drop_column('securities', 'figi')
    op.alter_column('users', 'birthdate',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=False)
    op.create_primary_key('securities_pm', 'securities', ['ticker'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'birthdate',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=False)
    op.add_column('securities', sa.Column('figi', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('securities', sa.Column('uid', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint('securities_pm', 'securities', type_='primary')
    # ### end Alembic commands ###
