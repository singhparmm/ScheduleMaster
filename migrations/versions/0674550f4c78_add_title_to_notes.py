"""Add title to notes

Revision ID: 0674550f4c78
Revises: b1a40e4d71bd
Create Date: 2024-04-15 21:39:56.420849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0674550f4c78'
down_revision = 'b1a40e4d71bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('note', schema=None) as batch_op:
        batch_op.drop_column('title')

    # ### end Alembic commands ###