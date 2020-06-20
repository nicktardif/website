from web_app import app
from web_app.models import Album, Image, Portfolio
from flask import render_template
from web_app.utilities.custom_roles_required import custom_roles_required

class AlbumView():
    @app.route('/albums/<int:album_id>')
    @custom_roles_required('admin')
    def get_album(album_id):
        album = Album.query.get(album_id)
        portfolios = Portfolio.query.all()
        return render_template('album.html', album=album, portfolios=portfolios)

    @app.route('/albums')
    @custom_roles_required('admin')
    def get_all_albums():
        albums = Album.query.all()
        return render_template('albums.html', albums=albums)

    @app.route('/albums/create')
    @custom_roles_required('admin')
    def create_album():
        images = Image.query.all()
        return render_template('create_album.html', images=images)
