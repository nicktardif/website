"""Add derived image types, thumbnail and downsampled

Revision ID: 154512454d6d
Revises: ff8508e0b2df
Create Date: 2020-06-13 14:10:37.188596

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '154512454d6d'
down_revision = 'ff8508e0b2df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('downsampled_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=250), nullable=False),
    sa.Column('original_image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['original_image_id'], ['image.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('thumbnail_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=250), nullable=False),
    sa.Column('original_image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['original_image_id'], ['image.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('downsampled_image_association',
    sa.Column('downsampled_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['downsampled_id'], ['downsampled_image.id'], ),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], )
    )
    op.create_table('thumbnail_image_association',
    sa.Column('thumbnail_id', sa.Integer(), nullable=True),
    sa.Column('image_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['image.id'], ),
    sa.ForeignKeyConstraint(['thumbnail_id'], ['thumbnail_image.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('thumbnail_image_association')
    op.drop_table('downsampled_image_association')
    op.drop_table('thumbnail_image')
    op.drop_table('downsampled_image')
    # ### end Alembic commands ###