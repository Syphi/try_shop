"""delete ENUM payment_type, create new ENUM, alter table orders

Revision ID: aedc2e3c1fb1
Revises: 7b36dc63c9ce
Create Date: 2018-01-09 17:02:53.204901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'aedc2e3c1fb1'
down_revision = 'f588fe06ce4f'
branch_labels = None
depends_on = None
metadata = sa.MetaData()


def upgrade():
    # new_payment_type = sa.dialects.postgresql.ENUM('CASH', 'CARD', name='new_payment_type')
    # op.alter_column('orders', 'payment_type', type_=sa.Enum('CASH', 'CARD', name='new_payment_type'),
    #                 postgresql_using='payment_type::new_payment_type')
    # op.execute('CREATE TYPE new_payment_type AS ENUM ("CASH", "CARD")')

    new_payment_type = sa.Enum('CASH', 'CARD', name='new_payment_type', metadata=metadata)
    new_payment_type.create(op.get_bind())

    op.execute('ALTER TABLE orders ALTER COLUMN payment_type '
               'TYPE new_payment_type USING (payment_type::text::new_payment_type);')

    # op.execute('ALTER TABLE orders ALTER COLUMN payment_type SET DATA TYPE new_payment_type US')

    payment_type = sa.Enum('cash', 'card', name='payment_type', metadata=metadata)
    payment_type.drop(op.get_bind())



def downgrade():
    new_payment_type = sa.dialects.postgresql.ENUM('CASH', 'CARD', name='payment_type')
    new_payment_type.drop(op.get_bind())

    payment_type = sa.Enum('cash', 'card', name='payment_type', metadata=metadata)
    payment_type.create(op.get_bind())

    op.alter_column('orders', 'payment_type', type_=sa.Enum('cash', 'card', name='payment_type'),
                    postgresql_using='payment_type::payment_type')
