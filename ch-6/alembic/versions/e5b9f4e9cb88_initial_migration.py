"""Initial migration

Revision ID: e5b9f4e9cb88
Revises: 
Create Date: 2025-02-09 21:34:10.610629

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5b9f4e9cb88'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sponsors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('sponsorships',
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('sponsor_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['sponsor_id'], ['sponsors.id'], ),
    sa.PrimaryKeyConstraint('event_id', 'sponsor_id')
    )
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('show', sa.String(), nullable=True),
    sa.Column('user', sa.String(), nullable=True),
    sa.Column('sold', sa.Boolean(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ticket_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_id', sa.Integer(), nullable=False),
    sa.Column('seat', sa.String(), nullable=True),
    sa.Column('ticket_type', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ticket_details')
    op.drop_table('tickets')
    op.drop_table('sponsorships')
    op.drop_table('sponsors')
    op.drop_table('events')
    # ### end Alembic commands ###
