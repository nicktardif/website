from sqlalchemy.orm import relationship
from web_app import db
from web_app.models import Image
from web_app.models.associations import portfolio_album_association_table, album_image_association_table

class Album(db.Model):
    __tablename__ = 'album'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    images = relationship(
            'Image',
            secondary = album_image_association_table,
            back_populates = 'albums')
    portfolios = relationship(
            'Portfolio',
            secondary = portfolio_album_association_table,
            back_populates = 'albums')

    def __init__(self, name, images):
        self.name = name
        self.images = images

    def update_name(self, name):
        self.name = name
        db.session.commit()

    def update_images(self, images):
        self.images = images
        db.session.commit()

    def add_image(self, image):
        self.images.append(image)
        db.session.commit()

    def remove_image(self, image):
        self.images.remove(image)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'images': self.images
        }
