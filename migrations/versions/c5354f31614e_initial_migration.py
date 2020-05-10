"""Initial migration

Revision ID: c5354f31614e
Revises: 
Create Date: 2020-05-10 15:50:25.263182

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5354f31614e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('original_path', sa.String(length=250), nullable=False),
    sa.Column('downsampled_path', sa.String(length=250), nullable=True),
    sa.Column('downsampled_size_string', sa.String(length=250), nullable=True),
    sa.Column('thumbnail_path', sa.String(length=250), nullable=True),
    sa.Column('thumbnail_basename', sa.String(length=250), nullable=True),
    sa.Column('caption', sa.String(length=250), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('location', sa.String(length=250), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('keyword',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('image_keyword_association',
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.Column('keyword_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.ForeignKeyConstraint(['keyword_id'], ['keyword.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('image_keyword_association')
    op.drop_table('keyword')
    op.drop_table('image')
    # ### end Alembic commands ###
