"""alter_orders_table

Revision ID: 3eabc4a2c182
Revises: aa0044f1d417
Create Date: 2018-02-07 14:22:33.571823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eabc4a2c182'
down_revision = 'aa0044f1d417'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('orders', 'sum_price', type_=sa.Numeric(asdecimal=False), nullable=False)


def downgrade():
    op.alter_column('orders', 'sum_price', type_=sa.Numeric, nullable=False)
