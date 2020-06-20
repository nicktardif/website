from web_app import app, db
from flask_api import status
from web_app.models import Album, Image
from web_app.utilities import Validator, Validation
from flask import jsonify, request
from web_app.utilities.custom_roles_required import custom_roles_required

class AlbumApiView():
    @app.route('/api/v1/albums/<int:album_id>')
    @custom_roles_required('admin')
    def api_get_album(album_id):
        validator = Validator([Validation.album_exists(album_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        return jsonify(Album.query.get(album_id)), status.HTTP_200_OK

    @app.route('/api/v1/albums')
    @custom_roles_required('admin')
    def api_get_all_albums():
        albums = Album.query.all()
        if albums:
            return jsonify(albums), status.HTTP_200_OK
        else:
            return '', status.HTTP_204_NO_CONTENT

    @app.route('/api/v1/albums', methods=['POST'])
    @custom_roles_required('admin')
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
    @custom_roles_required('admin')
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

    @app.route('/api/v1/albums/<int:album_id>/images/<int:image_id>', methods=['POST'])
    @custom_roles_required('admin')
    def api_album_add_image(album_id, image_id):
        validator = Validator([
            Validation.album_exists(album_id),
            Validation.image_exists(image_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        album = Album.query.get(album_id)
        image = Image.query.get(image_id)
        if image in album.images:
            return '', status.HTTP_400_BAD_REQUEST
        else:
            album.add_image(image)
            return '', status.HTTP_200_OK

    @app.route('/api/v1/albums/<int:album_id>/images/<int:image_id>', methods=['DELETE'])
    @custom_roles_required('admin')
    def api_album_remove_image(album_id, image_id):
        validator = Validator([
            Validation.album_exists(album_id),
            Validation.image_exists(image_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        album = Album.query.get(album_id)
        image = Image.query.get(image_id)
        if image in album.images:
            album.remove_image(image)
            return '', status.HTTP_200_OK
        else:
            return '', status.HTTP_400_BAD_REQUEST

    @app.route('/api/v1/albums/<int:album_id>', methods=['DELETE'])
    @custom_roles_required('admin')
    def api_delete_album(album_id):
        validator = Validator([Validation.album_exists(album_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        album = Album.query.get(album_id).delete()
        return '', status.HTTP_200_OK
