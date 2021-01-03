from base64 import b64decode
from sqlalchemy.orm import relationship
import datetime
import os
import pyexiv2

from web_app import app, db
from web_app.models import Keyword
from web_app.models.associations import album_image_association_table, image_keyword_association_table, thumbnail_image_association_table, downsampled_image_association_table
from web_app.classes import ImageGenerator
from web_app.utilities.file_helper import get_full_path

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    original_path = db.Column(db.String(250), nullable=False)
    caption = db.Column(db.String(250), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(250), nullable=True)

    keywords = relationship(
            'Keyword',
            secondary = image_keyword_association_table,
            back_populates = 'images')

    albums = relationship(
            'Album',
            secondary = album_image_association_table,
            back_populates = 'images')

    thumbnail_image = relationship(
            'ThumbnailImage',
            uselist = False,
            back_populates = 'original_image')

    downsampled_image = relationship(
            'DownsampledImage',
            uselist = False,
            back_populates = 'original_image')

    def __init__(self, original_path, caption, date, location, keywords):
        self.original_path = original_path
        self.caption = caption
        self.date = date
        self.location = location
        self.keywords = keywords

    def update_caption(self, caption):
        self.caption = caption
        db.session.commit()

    def update_date(self, date):
        self.date = date
        db.session.commit()

    def update_location(self, location):
        self.location = location
        db.session.commit()

    def generate_thumbnail(self, thumbnail_size):
        self.thumbnail_image = ImageGenerator.create_thumbnail(self, thumbnail_size)
        db.session.commit()

    def generate_downsampled(self, downsampled_size):
        self.downsampled_image = ImageGenerator.create_downsampled(self, downsampled_size)
        db.session.commit()

    def update_keywords(self, keywords):
        self.keywords = keywords
        db.session.commit()

    def delete(self):
        full_image_path = '{}/{}'.format(app.config['DATA_DIR'], self.original_path)
        os.remove(full_image_path)
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {
            'original_path': self.original_path,
            'caption': self.caption,
            'date': self.date,
            'location': self.location,
            'keywords': self.keywords
        }

    def fromNameAndData(image_name, image_data):
        full_image_path = '{}/{}'.format(app.config['DATA_DIR'], image_name)
        Image.__save_to_disk(full_image_path, image_data)
        original_path = image_name

        metadata = pyexiv2.Image(full_image_path)
        caption = Image.__get_caption(metadata)
        date = Image.__get_date(metadata)
        location = Image.__get_location(metadata)
        keywords = Image.__get_keywords(metadata)
        return Image(original_path, caption, date, location, keywords)

    def __save_to_disk(full_image_path, data):
        with open(full_image_path, 'wb') as fh:
            fh.write(b64decode(data))

    def __get_caption(metadata):
        return metadata.read_exif().get('Exif.Image.ImageDescription')

    def __get_date(metadata):
        date_format = '%Y:%m:%d %H:%M:%S'
        datetime_original_metadata = metadata.read_exif().get('Exif.Photo.DateTimeOriginal')
        date = None
        if datetime_original_metadata:
            date = datetime.datetime.strptime(datetime_original_metadata, date_format)
        else:
            datetime_metadata = metadata.read_exif().get('Exif.Image.DateTime')
            date = datetime.datetime.strptime(datetime_metadata, date_format)
        if not date:
            raise TypeError('Did not find a datetime for', self.original_path)
        return date

    def __get_location(metadata):
        return metadata.read_iptc().get('Iptc.Application2.SubLocation')

    def __get_keywords(metadata):
        return [Keyword(x) for x in metadata.read_iptc().get('Iptc.Application2.Keywords', [])]
