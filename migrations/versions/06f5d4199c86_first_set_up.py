"""first set up

Revision ID: 06f5d4199c86
Revises: 
Create Date: 2020-06-24 12:44:36.382647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06f5d4199c86'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mealand_day')
    op.drop_table('meal_day')
    op.add_column('limit', sa.Column('day', sa.Integer(), nullable=False))
    op.add_column('limit', sa.Column('meal', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('limit', 'meal')
    op.drop_column('limit', 'day')
    op.create_table('meal_day',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('day', sa.INTEGER(), nullable=False),
    sa.Column('meal', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mealand_day',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('day', sa.INTEGER(), nullable=False),
    sa.Column('meal', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###