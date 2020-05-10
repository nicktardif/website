from web_app import db
from sqlalchemy.orm import relationship

image_keyword_association_table = db.Table(
        'image_keyword_association',
        db.Model.metadata,
        db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
        db.Column('keyword_id', db.Integer, db.ForeignKey('keyword.id')))

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

class Keyword(db.Model):
    __tablename__ = 'keyword'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    images = relationship(
            'Image',
            secondary=image_keyword_association_table,
            back_populates='keywords')

    def __init__(self, name):
        self.name = name

    def toJSON(self):
        return {
            'name': self.name
        }
