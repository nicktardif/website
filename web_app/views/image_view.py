from web_app import app, db
from flask_api import status
from web_app.models import Image
from flask import jsonify, request

class ImageView():
#    @app.route('/api/v1/locations/<int:location_id>')
#    def get_location(location_id):
#        """Get a specified Location from the database
#        ---
#        definitions:
#            Location:
#                type: object
#                properties:
#                    id:
#                        type: integer
#                        example: 3
#                    name:
#                        type: string
#                        example: Dragonstone
#            ErrorResponse:
#                type: object
#                properties:
#                    error:
#                        type: string
#                        example: Description of error is here
#        tags:
#         - locations
#        parameters:
#            - in: query
#              description: Location ID to retrieve
#              name: location_id
#              required: true
#              type: integer
#        responses:
#            200:
#                description: Returns the location with the specified ID
#                schema:
#                    $ref: "#/definitions/Location"
#            404:
#                description: No location was found with the input ID
#                schema:
#                    $ref: "#/definitions/ErrorResponse"
#        """
#        location = Location.query.get(location_id)
#        if location:
#            return jsonify(location), status.HTTP_200_OK
#        else:
#            message = 'Location with ID {} not found in the database'.format(location_id)
#            return jsonify({'error': message}), status.HTTP_404_NOT_FOUND

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

#    @app.route('/api/v1/locations', methods=['POST'])
#    def create_location():
#        """Add a new Location to the database
#        ---
#        tags:
#         - locations
#        parameters:
#          - in: body
#            name: name
#            type: string
#            description: Name of the Location
#            required: true
#        responses:
#            201:
#                description: Location was created successfully
#                schema:
#                    $ref: "#/definitions/Location"
#            400:
#                description: Request was not formatted correctly
#                schema:
#                    $ref: "#/definitions/ErrorResponse"
#        """
#        if request.form:
#            if 'name' not in request.form:
#                message = 'Did not supply name in the data field'
#                return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST
#            name = request.form.get('name')
#
#            new_location = Location(name)
#            db.session.add(new_location)
#            db.session.commit()
#
#            return jsonify(new_location), status.HTTP_201_CREATED
#        else:
#            message = 'Request did not include a data form, try again'
#            return jsonify({'error': message}), status.HTTP_400_BAD_REQUEST
#
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
#
#    @app.route('/api/v1/locations/<int:location_id>', methods=['DELETE'])
#    def delete_location(location_id):
#        """Delete a Location to the database
#        ---
#        tags:
#         - locations
#        parameters:
#          - in: query
#            name: location_id
#            type: integer
#            required: true
#        responses:
#            200:
#                description: Location deleted successfully
#            404:
#                description: Location with the specified ID does not exist in the database
#                schema:
#                    $ref: "#/definitions/ErrorResponse"
#        """
#        location = Location.query.get(location_id)
#
#        if location:
#            db.session.delete(location)
#            db.session.commit()
#            return '', status.HTTP_200_OK
#        else:
#            message = 'Location with the ID {} does not exist in the database'.format(location_id)
#            return jsonify({'error': message}), status.HTTP_404_NOT_FOUND
