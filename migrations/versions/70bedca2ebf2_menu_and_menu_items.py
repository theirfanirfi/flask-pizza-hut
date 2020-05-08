"""menu and menu items

Revision ID: 70bedca2ebf2
Revises: 36a96879dc1b
Create Date: 2020-05-07 19:36:59.028556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70bedca2ebf2'
down_revision = '36a96879dc1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('menu_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('small_size', sa.String(length=20), nullable=True),
    sa.Column('large_size', sa.String(length=20), nullable=True),
    sa.Column('menu_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['menu_id'], ['menu_items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('menu',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('menu')
    op.drop_table('menu_items')
    # ### end Alembic commands ###