from sqlalchemy.orm import relationship
from web_app import db
from web_app.models import Album

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    primary_album_id = db.Column(db.Integer, nullable=False)
    albums = relationship('Album')

    def __init__(self, name, primary_album_id, albums):
        self.name = name
        self.primary_album_id
        self.albums = albums

    def update_name(self, name):
        self.name = name
        db.session.commit()

    def add_album(self, album_id):
        album = Album.query.get(album_id)
        success = False
        if album:
            self.albums.append(album)
            success = True
        return success

    def remove_album(self, album_id):
        album = Album.query.get(album_id)
        success = False
        if album in self.albums:
            self.albums.remove(album)
            success = True
        return success

    def update_primary_album_id(self, primary_album_id):
        self.primary_album_id = primary_album_id

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {
            'name': self.name,
            'primary_album_id': self.primary_album_id,
            'albums': self.albums
        }
