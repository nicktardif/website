from web_app import app, db
from flask_api import status
from web_app.models import Image
from flask import jsonify, request
import datetime

def image_exists_in_database(image_name):
    return True if Image.query.filter_by(original_path=image_name).first() else False

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
        # TODO: Check some kind of authorization
        if request.form:
            if 'image_name' not in request.form:
                message = 'Did not supply image_name in the data field'
                return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST
            if 'image_data' not in request.form:
                message = 'Did not supply image_data in the data field'
                return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST

            image_name = request.form.get('image_name')
            if image_exists_in_database(image_name):
                message = 'Image with the name {} already exists in the database'.format(image_name)
                return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST

            image_data = request.form.get('image_data')

            new_image = Image.fromNameAndData(image_name, image_data)
            db.session.add(new_image)
            db.session.commit()

            return jsonify(new_image), status.HTTP_201_CREATED
        else:
            message = 'Request did not include a data form, try again'
            return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST

#    @app.route('/api/v1/locations/<int:location_id>', methods=['PATCH'])
#    def update_location(location_id):
#        """Updates a location in the database
#        ---
#        tags:
#         - locations
#        parameters:
#          - in: query
#            name: location_id
#            type: integer
#            description: ID of the location to update
#            required: true
#          - in: body
#            name: name
#            type: string
#            description: Name of the Location
#            required: true
#        responses:
#            200:
#                description: Location was updated successfully
#                schema:
#                    $ref: "#/definitions/Location"
#            400:
#                description: Request was not formatted correctly
#                schema:
#                    $ref: "#/definitions/ErrorResponse"
#            404:
#                description: Did not find a location with the specified ID
#                schema:
#                    $ref: "#/definitions/ErrorResponse"
#        """
#        if request.form:
#            if 'name' not in request.form:
#                message = 'Did not supply name in the data field'
#                return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST
#            name = request.form.get('name')
#
#            location = Location.query.get(location_id)
#            if location:
#                location.name = name
#                db.session.commit()
#                return jsonify(location), status.HTTP_200_OK
#            else:
#                message = 'Location with the ID {} does not exist in the database'.format(location_id)
#                return jsonify({'error': message}), status.HTTP_404_NOT_FOUND
#        else:
#            message = 'Request did not include a data form, try again'
#            return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST

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
        image = Image.query.get(image_id)
        if image:
            image.delete()
            return '', status.HTTP_200_OK
        else:
            message = 'Image with the ID {} does not exist in the database'.format(image_id)
            return jsonify({'error': message}), status.HTTP_404_NOT_FOUND
