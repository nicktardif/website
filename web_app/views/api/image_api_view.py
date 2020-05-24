from web_app import app, db
from flask_api import status
from web_app.models import Image
from web_app.utilities import Validator, Validation
from flask import jsonify, request
import datetime

def image_name_exists_in_database(image_name):
    return True if Image.query.filter_by(original_path=image_name).first() else False

class ImageApiView():
    @app.route('/api/v1/images/<int:image_id>')
    def get_image(image_id):
        validator = Validator([Validation.image_exists(image_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        return jsonify(Image.query.get(image_id)), status.HTTP_200_OK

    @app.route('/api/v1/images')
    def get_all_images():
        images = Image.query.all()
        if images:
            return jsonify(images), status.HTTP_200_OK
        else:
            return '', status.HTTP_204_NO_CONTENT

    @app.route('/api/v1/images', methods=['POST'])
    def create_image():
        # TODO: Check some kind of user authorization
        unique_image_validation = Validation.custom_json_validation('image_name',
                lambda v: not image_name_exists_in_database(v),
                lambda v: f'Image with the name {v} already exists in the database'
        )

        validator = Validator([
            Validation.is_json_payload(),
            Validation.required_json('image_name'),
            Validation.required_json('image_data'),
            unique_image_validation
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        new_image = Image.fromNameAndData(
                request.get_json().get('image_name'),
                bytes(request.get_json().get('image_data')))
        db.session.add(new_image)
        db.session.commit()

        return jsonify(new_image), status.HTTP_201_CREATED

    @app.route('/api/v1/images/<int:image_id>', methods=['PATCH'])
    def update_image(image_id):
        validator = Validator([
            Validation.is_json_payload(),
            Validation.image_exists(image_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        image = Image.query.get(image_id)
        caption = request.get_json().get('caption')
        if caption:
            image.update_caption(caption)

        location = request.get_json().get('location')
        if location:
            image.update_location(location)

        date = request.get_json().get('date')
        if date:
            image.update_date(datetime.datetime.fromisoformat(date))

        keyword_strings = request.get_json().get('keywords')
        if keyword_strings:
            keywords = [Keyword(s) for s in keyword_strings]
            image.update_keywords(keywords)

        return jsonify(image), status.HTTP_200_OK

    @app.route('/api/v1/images/<int:image_id>', methods=['DELETE'])
    def delete_image(image_id):
        validator = Validator([Validation.image_exists(image_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        Image.query.get(image_id).delete()
        return '', status.HTTP_200_OK
