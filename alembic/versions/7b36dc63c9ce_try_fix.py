"""delete ENUM payment_type, create new ENUM, alter table orders

Revision ID: aedc2e3c1fb1
Revises: 7b36dc63c9ce
Create Date: 2018-01-09 17:02:53.204901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7b36dc63c9ce'
down_revision = 'aedc2e3c1fb1'
branch_labels = None
depends_on = None
metadata = sa.MetaData()


def upgrade():
    pass


def downgrade():
    pass
