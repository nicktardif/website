from web_app import app, db
from flask_api import status
from web_app.models import Image
from web_app.utilities import Validator, Validation
from flask import jsonify, request
import datetime

def image_name_exists_in_database(image_name):
    return True if Image.query.filter_by(original_path=image_name).first() else False

def image_exists(image_id):
    return Validation.custom_validation(
        lambda: Image.query.get(image_id),
        lambda: 'Image with the ID {} does not exist in the database'.format(image_id),
        status.HTTP_404_NOT_FOUND)

class ImageView():
    @app.route('/api/v1/images/<int:image_id>')
    def get_image(image_id):
        """Get a specified Image from the database
        ---
        definitions:
            Image:
                type: object
                properties:
                    id:
                        type: integer
                        example: 3
                    original_path:
                        type: string
                        example: image.jpg
                    downsampled_path:
                        type: string
                        example: downsampled_1920x1080.jpg
                    downsampled_size_string:
                        type: string
                        example: 1920x1080
                    thumbnail_path:
                        type: string
                        example: thumbnail.jpg
                    thumbnail_basename:
                        type: string
                        example: thumbnail
                    caption:
                        type: string
                        example: "Look at that cat."
                    date:
                        type: date
                    location:
                        type: string
                        example: Seattle
            ErrorResponse:
                type: object
                properties:
                    error:
                        type: string
                        example: Description of error is here
        tags:
         - images
        parameters:
            - in: query
              description: Image ID to retrieve
              name: image_id
              required: true
              type: integer
        responses:
            200:
                description: Returns the image with the specified ID
                schema:
                    $ref: "#/definitions/Image"
            404:
                description: No image was found with the input ID
                schema:
                    $ref: "#/definitions/ErrorResponse"
        """
        image = Image.query.get(image_id)
        if image:
            return jsonify(image), status.HTTP_200_OK
        else:
            message = 'Image with ID {} not found in the database'.format(image_id)
            return jsonify({'error': message}), status.HTTP_404_NOT_FOUND

    @app.route('/api/v1/images')
    def get_all_images():
        """Get all images from the database
        ---
        tags:
         - images
        responses:
            200:
                description: Returns all the images
                schema:
                    type: array
                    items:
                        $ref: "#/definitions/Image"
            204:
                description: No images were in the database
        """
        images = Image.query.all()
        if images:
            return jsonify(images), status.HTTP_200_OK
        else:
            return '', status.HTTP_204_NO_CONTENT

    @app.route('/api/v1/images', methods=['POST'])
    def create_image():
        """Add a new Image to the database
        ---
        tags:
         - images
        parameters:
          - in: body
            name: image_name
            type: string
            description: Filename of the image. Should be unique in the database.
            required: true
          - in: body
            name: image_data
            type: string
            description: base64 encoded JPG image, with optional metadata
            required: true
        responses:
            201:
                description: Location was created successfully
                schema:
                    $ref: "#/definitions/Image"
            400:
                description: Request was not formatted correctly
                schema:
                    $ref: "#/definitions/ErrorResponse"
        """
        # TODO: Check some kind of user authorization
        unique_image_validation = Validation.custom_json_validation('image_name',
                lambda v: not image_name_exists_in_database(v),
                lambda v: 'Image with the name {} already exists in the database'.format(v)
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
        """Updates a image in the database
        ---
        tags:
         - images
        parameters:
          - in: query
            name: image_id
            type: integer
            description: ID of the image to update
            required: true
          - in: body
            name: caption
            type: string
            description: Caption for the image
            required: false
          - in: body
            name: date
            type: date
            description: Date for the image, in UTC
            required: false
          - in: body
            name: location
            type: string
            description: Location for the image
            required: false
        responses:
            200:
                description: Image was updated successfully
                schema:
                    $ref: "#/definitions/Image"
            400:
                description: Request was not formatted correctly
                schema:
                    $ref: "#/definitions/ErrorResponse"
            404:
                description: Did not find a image with the specified ID
                schema:
                    $ref: "#/definitions/ErrorResponse"
        """
        validator = Validator([
            Validation.is_json_payload(),
            image_exists(image_id)
        ])
        if not validator.validate(request):
            return validator.get_error_response()

        caption = request.get_json().get('caption')
        if caption:
            Image.update_caption(image_id, caption)

        location = request.get_json().get('location')
        if location:
            Image.update_location(image_id, location)

        date = request.get_json().get('date')
        if date:
            Image.update_date(image_id, datetime.datetime.fromisoformat(date))

        keywords = request.get_json().get('keywords')
        if keywords:
            Image.update_keywords(image_id, keywords)

        image = Image.query.get(image_id)
        return jsonify(image), status.HTTP_200_OK

    @app.route('/api/v1/images/<int:image_id>', methods=['DELETE'])
    def delete_image(image_id):
        """Delete a Image to the database
        ---
        tags:
         - images
        parameters:
          - in: query
            name: image_id
            type: integer
            required: true
        responses:
            200:
                description: Image deleted successfully
            404:
                description: Image with the specified ID does not exist in the database
                schema:
                    $ref: "#/definitions/ErrorResponse"
        """
        validator = Validator([image_exists(image_id)])
        if not validator.validate(request):
            return validator.get_error_response()

        image = Image.query.get(image_id)
        if image:
            image.delete()
            return '', status.HTTP_200_OK
