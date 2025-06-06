"""Add: Job and Application table

Revision ID: aa6311849230
Revises: a5276826502c
Create Date: 2025-04-18 17:40:05.977313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'aa6311849230'
down_revision: Union[str, None] = 'a5276826502c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jobs',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('location', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('salary', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('employer_uid', sa.UUID(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['employer_uid'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('uid')
    )
    op.create_table('applications',
    sa.Column('uid', sa.UUID(), nullable=False),
    sa.Column('job_uid', sa.UUID(), nullable=False),
    sa.Column('user_uid', sa.UUID(), nullable=False),
    sa.Column('cover_letter', sa.Text(), nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['job_uid'], ['jobs.uid'], ),
    sa.ForeignKeyConstraint(['user_uid'], ['users.uid'], ),
    sa.PrimaryKeyConstraint('uid'),
    sa.UniqueConstraint('job_uid', 'user_uid', name='uq_job_seeker')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('applications')
    op.drop_table('jobs')
    # ### end Alembic commands ###
