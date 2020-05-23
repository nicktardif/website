from sqlalchemy.orm import relationship
from web_app import db
from web_app.models import Image

class Album(db.Model):
    __tablename__ = 'album'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    images = relationship('Image')

    def __init__(self, name, images):
        self.name = name
        self.images = images

    def update_name(self, name):
        self.name = name
        db.session.commit()

    def add_image(self, image_id):
        image = Image.query.get(image_id)
        success = False
        if image:
            self.images.append(image)
            success = True
        return success

    def remove_image(self, image_id):
        image = Image.query.get(image_id)
        success = False
        if image in self.images:
            self.images.remove(image)
            success = True
        return success

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {
            'name': self.name,
            'images': self.images
        }
