from web_app import app
from web_app.models import Album, Image, Portfolio
from flask import render_template

class AlbumView():
    @app.route('/albums/<int:album_id>')
    def get_album(album_id):
        album = Album.query.get(album_id)
        portfolios = Portfolio.query.all()
        return render_template('album.html', album=album, portfolios=portfolios)

    @app.route('/albums')
    def get_all_albums():
        albums = Album.query.all()
        return render_template('albums.html', albums=albums)

    @app.route('/albums/create')
    def create_album():
        images = Image.query.all()
        return render_template('create_album.html', images=images)
