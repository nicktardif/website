from base64 import b64encode
from flask import jsonify
from flask_api import status
from web_app import app, db
from web_app.models import Image, Keyword
from web_app.tests.sample_test_case import SampleTestCase
from web_app.utilities.file_helper import get_full_path
import datetime
import os
import unittest

def populate_database(db):
    sample_keyword = Keyword('landscape')
    db.session.add(sample_keyword)

    sample_image = Image('yolo.jpg', '', '', '', '', 'yolo', datetime.datetime.utcnow(), 'Westeros', [sample_keyword])
    if not os.path.exists(get_full_path('yolo.jpg')):
        os.mknod(get_full_path('yolo.jpg'))
    db.session.add(sample_image)
    db.session.commit()

def image_to_base64(full_image_path):
    with open(full_image_path, 'rb') as f:
        return b64encode(f.read())

class GetImageTest(SampleTestCase):
    def test_get_image(self):
        populate_database(db)

        image_id = 1
        image = Image.query.get(image_id)

        response = self.client.get('/api/v1/images/{}'.format(image_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(image).json)

    def test_get_image_invalid_id(self):
        image_id = 1
        response = self.client.get('/api/v1/images/{}'.format(image_id))
        expected_response = {'error': 'Image with ID {} not found in the database'.format(image_id)}
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.json, expected_response)

class GetAllImagesTest(SampleTestCase):
    def test_get_all_images(self):
        populate_database(db)

        images = Image.query.all()

        response = self.client.get('/api/v1/images')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(images).json)

    def test_get_all_images_no_data(self):
        response = self.client.get('/api/v1/images')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

class CreateImageTest(SampleTestCase):
    def test_create_image(self):
        data = {'image_name': 'test.jpg', 'image_data': image_to_base64('/tmp/images/test.jpg')}
        response = self.client.post('/api/v1/images', data=data)
        print(response.json)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        expected_image_id = 1
        expected_response = Image.query.get(expected_image_id)

        self.assertEquals(response.json, jsonify(expected_response).json)
        print(response.json)

    def test_create_image_missing_name(self):
        data = {'image_data': 'test.jpg'}
        response = self.client.post('/api/v1/images', data=data)

        expected_response = {'error': 'Did not supply image_name in the data field'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)
        # TODO: Need to check for the caption, location, date, and keyword values

    def test_create_image_missing_data(self):
        data = {'image_name': 'test.jpg'}
        response = self.client.post('/api/v1/images', data=data)

        expected_response = {'error': 'Did not supply image_data in the data field'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

    def test_create_image_no_data_field(self):
        response = self.client.post('/api/v1/images')

        expected_response = {'error': 'Request did not include a data form, try again'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

#class UpdateLocationTest(SampleTestCase):
#    def test_update_location(self):
#        populate_database(db)
#
#        location_id = 1
#        data = {'name': 'Sunspear'}
#        response = self.client.patch('/api/v1/locations/{}'.format(location_id), data=data)
#
#        location = Location.query.get(location_id)
#
#        self.assertEquals(response.status_code, status.HTTP_200_OK)
#        self.assertEquals(response.json, jsonify(location).json)
#
#    def test_update_location_invalid_id(self):
#        location_id = 1
#        data = {'name': 'Sunspear'}
#        response = self.client.patch('/api/v1/locations/{}'.format(location_id), data=data)
#
#        expected_response = {'error': 'Location with the ID {} does not exist in the database'.format(location_id)}
#        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
#        self.assertEquals(response.json, jsonify(expected_response).json)
#
#    def test_update_location_no_name(self):
#        location_id = 1
#        data = {'library': 'Oldtown'}
#        response = self.client.patch('/api/v1/locations/{}'.format(location_id), data=data)
#
#        expected_response = {'error': 'Did not supply name in the data field'}
#        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
#        self.assertEquals(response.json, jsonify(expected_response).json)
#
#    def test_update_location_no_data(self):
#        location_id = 1
#        response = self.client.patch('/api/v1/locations/{}'.format(location_id))
#
#        expected_response = {'error': 'Request did not include a data form, try again'}
#        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
#        self.assertEquals(response.json, jsonify(expected_response).json)

class DeleteLocationTest(SampleTestCase):
    def test_delete_image(self):
        populate_database(db)
        image_id = 1

        image = Image.query.get(image_id)
        original_image_full_path = get_full_path(image.original_path)
        response = self.client.delete('/api/v1/images/{}'.format(image_id))

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Image.query.get(image_id), None)
        self.assertEquals(os.path.exists(original_image_full_path), False)

    def test_delete_image_invalid_id(self):
        image_id = 1
        response = self.client.delete('/api/v1/images/{}'.format(image_id))

        expected_response = {'error': 'Image with the ID {} does not exist in the database'.format(image_id)}
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.json, jsonify(expected_response).json)
