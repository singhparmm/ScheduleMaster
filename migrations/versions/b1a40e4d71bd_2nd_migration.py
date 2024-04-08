"""2nd Migration

Revision ID: b1a40e4d71bd
Revises: 71fbcccda7ab
Create Date: 2024-04-07 22:45:08.923469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1a40e4d71bd'
down_revision = '71fbcccda7ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hour', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.drop_column('hour')

    # ### end Alembic commands ###
