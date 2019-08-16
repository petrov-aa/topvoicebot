"""add chat data

Revision ID: a3bd6cf10d35
Revises: d48a7e4e71bf
Create Date: 2019-08-17 01:05:52.925646

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3bd6cf10d35'
down_revision = 'd48a7e4e71bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat', sa.Column('data', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat', 'data')
    # ### end Alembic commands ###