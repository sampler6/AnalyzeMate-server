"""add timeframe to historic candles

Revision ID: 8ac292250d57
Revises: 5de3e9cda0d1
Create Date: 2024-04-10 00:19:45.304757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ac292250d57'
down_revision: Union[str, None] = '5de3e9cda0d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('historic_candle', sa.Column('timeframe', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('historic_candle', 'timeframe')
    # ### end Alembic commands ###
