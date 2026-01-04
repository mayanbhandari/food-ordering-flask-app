"""Add profile_image column to User

Revision ID: a3c2588a39b4
Revises: deeb1c110f00
Create Date: 2025-09-13 22:40:09.023434
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a3c2588a39b4'
down_revision = 'deeb1c110f00'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_image', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('profile_image')