from PIL import Image as PilImage
from sqlalchemy.orm import relationship
from web_app import app, db
from web_app.models.associations import album_image_association_table, image_keyword_association_table, thumbnail_image_association_table, downsampled_image_association_table
from web_app.utilities.file_helper import get_full_path

class DownsampledImage(db.Model):
    __tablename__ = 'downsampled_image'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(250), nullable=False)
    original_image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    dimensions = db.Column(db.String(25), nullable=True)
    original_image = relationship(
            'Image',
            back_populates = 'downsampled_image')

    def __init__(self, image_name, original_image):
        self.path = image_name
        self.original_image = original_image

        width, height = PilImage.open(get_full_path(image_name)).size
        self.dimensions = '{}x{}'.format(width, height)
