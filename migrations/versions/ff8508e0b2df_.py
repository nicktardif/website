"""Add link to album and portfolios

Revision ID: ff8508e0b2df
Revises: cda5a0c96b92
Create Date: 2020-05-23 12:30:49.880581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff8508e0b2df'
down_revision = 'cda5a0c96b92'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('portfolio_album_association',
    sa.Column('album_id', sa.Integer(), nullable=True),
    sa.Column('portfolio_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolio.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('portfolio_album_association')
    # ### end Alembic commands ###
