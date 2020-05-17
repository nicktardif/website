from base64 import b64decode
from sqlalchemy.orm import relationship
import os
import pyexiv2

from web_app import app, db
from web_app.models import Keyword
from web_app.models.associations import image_keyword_association_table
from web_app.utilities.file_helper import get_full_path

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    original_path = db.Column(db.String(250), nullable=False)
    downsampled_path = db.Column(db.String(250), nullable=True)
    downsampled_size_string = db.Column(db.String(250), nullable=True)
    thumbnail_path = db.Column(db.String(250), nullable=True)
    thumbnail_basename = db.Column(db.String(250), nullable=True)
    caption = db.Column(db.String(250), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(250), nullable=False)

    keywords = relationship(
            'Keyword',
            secondary=image_keyword_association_table,
            back_populates='images')

    def __init__(self, original_path, downsampled_path, downsampled_size_string, thumbnail_path, thumbnail_basename, caption, date, location, keywords):
        self.original_path = original_path
        self.downsampled_path = downsampled_path
        self.downsampled_size_string = downsampled_size_string
        self.thumbnail_path = thumbnail_path
        self.thumbnail_basename = thumbnail_basename
        self.caption = caption
        self.date = date
        self.location = location
        self.keywords = keywords

    def delete(self):
        full_image_path = '{}/{}'.format(app.config['DATA_DIR'], self.original_path)
        os.remove(full_image_path)
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {
            'original_path': self.original_path,
            'downsampled_path': self.downsampled_path,
            'downsampled_size_string': self.downsampled_size_string,
            'thumbnail_path': self.thumbnail_path,
            'thumbnail_basename': self.thumbnail_basename,
            'caption': self.caption,
            'date': self.date,
            'location': self.location,
            'keywords': self.keywords
        }

    def fromNameAndData(image_name, image_data):
        full_image_path = '{}/{}'.format(app.config['DATA_DIR'], image_name)
        Image.__save_to_disk(full_image_path, image_data)

        original_path = image_name
        downsampled_path = ''
        downsampled_size_string = ''
        thumbnail_path = ''
        thumbnail_basename = ''

        metadata = Image.__get_metadata(full_image_path)
        caption = Image.__get_caption(metadata)
        date = Image.__get_date(metadata)
        location = Image.__get_location(metadata)
        keywords = Image.__get_keywords(metadata)
        return Image(original_path, downsampled_path, downsampled_size_string, thumbnail_path, thumbnail_basename, caption, date, location, keywords)

    def __save_to_disk(full_image_path, data):
        with open(full_image_path, 'wb') as fh:
            fh.write(b64decode(data))

    def __get_metadata(full_image_path):
        data = pyexiv2.metadata.ImageMetadata(full_image_path)
        data.read()
        return data

    def __get_caption(metadata):
        return Image.__get_metadata_value(metadata, 'Exif.Image.ImageDescription', lambda x: x.value)

    def __get_date(metadata):
        date = Image.__get_metadata_value(metadata, 'Exif.Image.DateTime', lambda x: x.value)
        if not date:
            date = Image.__get_metadata_value(metadata, 'Exif.Photo.DateTimeOriginal', lambda x: x.value)
        if not date:
            raise TypeError('Did not find a datetime for', self.original_path)
        return date

    def __get_location(metadata):
        return Image.__get_metadata_value(metadata, 'Iptc.Application2.SubLocation', lambda x: x.value[0])

    def __get_keywords(metadata):
        return [Keyword(x) for x in Image.__get_metadata_value(metadata, 'Iptc.Application2.Keywords', lambda x: x.value)]

    def __get_metadata_value(metadata, key, value_function):
        metadata_key = metadata.get(key)
        return value_function(metadata_key) if metadata_key else ''
