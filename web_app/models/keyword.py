from sqlalchemy.orm import relationship
from web_app import db
from web_app.models.associations import image_keyword_association_table

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
