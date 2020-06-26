"""empty message

Revision ID: f2c47ce0f95b
Revises: 63ac30e42644
Create Date: 2020-06-26 12:23:28.935606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2c47ce0f95b'
down_revision = '63ac30e42644'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ingredient', sa.Column('datastr', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ingredient', 'datastr')
    # ### end Alembic commands ###