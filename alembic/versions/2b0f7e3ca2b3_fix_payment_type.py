"""fix payment type

Revision ID: 2b0f7e3ca2b3
Revises: 7b36dc63c9ce
Create Date: 2018-01-10 11:30:19.808112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b0f7e3ca2b3'
down_revision = '7b36dc63c9ce'
branch_labels = None
depends_on = None


def upgrade():
    # op.execute('SET AUTOCOMMIT = ON;')
    op.execute("ALTER TYPE payment_type ADD VALUE 'CASH';")
    op.execute("ALTER TYPE payment_type ADD VALUE 'CARD';")

    op.execute("UPDATE orders SET payment_type = 'CASH' WHERE payment_type = 'cash';")
    op.execute("UPDATE orders SET payment_type = 'CARD' WHERE payment_type = 'card';")

    op.execute("ALTER TYPE payment_type RENAME TO payment_type_old;")
    op.execute("CREATE TYPE payment_type AS ENUM('CASH', 'CARD');")
    op.execute("ALTER TABLE orders ALTER COLUMN payment_type TYPE payment_type USING payment_type::text::payment_type;")
    op.execute("DROP TYPE payment_type_old;")


def downgrade():
    op.execute("ALTER TYPE payment_type ADD VALUE 'cash';")
    op.execute("ALTER TYPE payment_type ADD VALUE 'card';")

    op.execute("UPDATE orders SET payment_type = 'CASH' WHERE payment_type = 'CASH';")
    op.execute("UPDATE orders SET payment_type = 'CARD' WHERE payment_type = 'CARD';")

    op.execute("ALTER TYPE payment_type RENAME TO payment_type_old;")
    op.execute("CREATE TYPE payment_type AS ENUM('cash', 'card');")
    op.execute("ALTER TABLE orders ALTER COLUMN payment_type TYPE payment_type USING payment_type::text::payment_type;")
    op.execute("DROP TYPE payment_type_old;")
