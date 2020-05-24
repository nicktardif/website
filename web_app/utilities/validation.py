from flask import jsonify
from flask_api import status
from web_app.models import Album, Image, Portfolio

class Validation:
    def is_json_payload():
        return lambda r: Validation.__is_json_payload(r)

    def __is_json_payload(request):
        if not request.get_json():
            message = 'Request did not include a JSON payload, try again'
            return False, Validation.create_400_response(message)
        return True, None

    def required_json(key):
        return lambda r: Validation.__required_json(r, key)

    def __required_json(request, key):
        if not request.get_json().get(key):
            message = f'Did not supply {key} in the JSON payload'
            return False, Validation.create_400_response(message)
        return True, None

    def custom_validation(criteria_function, message_function, status_code):
        return lambda r: Validation.__custom_validation(criteria_function, message_function, status_code)

    def __custom_validation(criteria_function, message_function, status_code):
        if not criteria_function():
            return False, Validation.create_response(message_function(), status_code)
        return True, None

    def custom_json_validation(key, criteria_function, message_function):
        return lambda r: Validation.__custom_json_validation(r, key, criteria_function, message_function)

    def __custom_json_validation(request, key, criteria_function, message_function):
        value = request.get_json().get(key)
        if not criteria_function(value):
            message = message_function(value)
            return False, Validation.create_400_response(message)
        return True, None

    def create_400_response(message):
        return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST

    def create_response(message, status_code):
        return jsonify({'error': message}), status_code

    def image_exists(image_id):
        message = f'Image with the ID {image_id} does not exist in the database'
        return Validation.custom_validation(
            lambda: Image.query.get(image_id),
            lambda: message,
            status.HTTP_404_NOT_FOUND)

    def album_exists(album_id):
        message = f'Album with the ID {album_id} does not exist in the database'
        return Validation.custom_validation(
            lambda: Album.query.get(album_id),
            lambda: message,
            status.HTTP_404_NOT_FOUND)

    def portfolio_exists(portfolio_id):
        message = f'Portfolio with the ID {portfolio_id} does not exist in the database'
        return Validation.custom_validation(
            lambda: Portfolio.query.get(portfolio_id),
            lambda: message,
            status.HTTP_404_NOT_FOUND)
