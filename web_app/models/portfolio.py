from sqlalchemy.orm import relationship
from web_app import db
from web_app.models import Album
from web_app.models.associations import portfolio_album_association_table

class Portfolio(db.Model):
    __tablename__ = 'portfolio'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    primary_album_id = db.Column(db.Integer, nullable=False)
    albums = relationship(
            'Album',
            secondary = portfolio_album_association_table,
            back_populates = 'portfolios')

    def __init__(self, name, primary_album_id, albums):
        self.name = name
        self.primary_album_id = primary_album_id
        self.albums = albums

    def update_name(self, name):
        self.name = name
        db.session.commit()

    def update_primary_album(self, primary_album_id):
        self.primary_album_id = primary_album_id
        db.session.commit()

    def update_albums(self, albums):
        self.albums = albums
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def toJSON(self):
        return {
            'name': self.name,
            'primary_album_id': self.primary_album_id,
            'albums': self.albums
        }
