from flask import jsonify
from flask_api import status

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
            message = 'Did not supply {} in the JSON payload'.format(key)
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
