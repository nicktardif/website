from web_app import app, db
from flask_api import status
from web_app.models import Album, Image
from web_app.utilities import Validator, Validation
from flask import jsonify, request

class AlbumApiView():
    @app.route('/api/v1/albums/<int:album_id>')
    def api_get_album(album_id):
        validator = Validator([Validation.album_exists(album_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        return jsonify(Album.query.get(album_id)), status.HTTP_200_OK

    @app.route('/api/v1/albums')
    def api_get_all_albums():
        albums = Album.query.all()
        if albums:
            return jsonify(albums), status.HTTP_200_OK
        else:
            return '', status.HTTP_204_NO_CONTENT

    @app.route('/api/v1/albums', methods=['POST'])
    def api_create_album():
        validator = Validator([
            Validation.is_json_payload(),
            Validation.required_json('name')
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        image_ids = request.get_json().get('image_ids', [])
        images = [Image.query.get(id) for id in image_ids]
        new_album = Album(request.get_json().get('name'), images)
        db.session.add(new_album)
        db.session.commit()

        return jsonify(new_album), status.HTTP_201_CREATED

    @app.route('/api/v1/albums/<int:album_id>', methods=['PATCH'])
    def api_update_album(album_id):
        validator = Validator([
            Validation.is_json_payload(),
            Validation.album_exists(album_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        album = Album.query.get(album_id)
        name = request.get_json().get('name')
        if name:
            album.update_name(name)

        image_ids = request.get_json().get('image_ids', [])
        images = [Image.query.get(id) for id in image_ids]
        if images:
            album.update_images(images)

        return jsonify(album), status.HTTP_200_OK

    @app.route('/api/v1/albums/<int:album_id>', methods=['DELETE'])
    def api_delete_album(album_id):
        validator = Validator([Validation.album_exists(album_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        album = Album.query.get(album_id).delete()
        return '', status.HTTP_200_OK
