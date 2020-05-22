"""toppings column changed again 6

Revision ID: f46cd13eb909
Revises: 8e8ae5fdda43
Create Date: 2020-05-22 13:07:22.777450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f46cd13eb909'
down_revision = '8e8ae5fdda43'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cart', sa.Column('is_topper_in_cart', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cart', 'is_topper_in_cart')
    # ### end Alembic commands ###
