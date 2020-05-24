from base64 import b64encode
from flask import jsonify
from flask_api import status
from web_app import app, db
from web_app.models import Album, Keyword, Image
from web_app.tests.sample_test_case import SampleTestCase
import datetime
import os
import unittest

def populate_database(db):
    sample_keyword = Keyword('landscape')
    db.session.add(sample_keyword)

    sample_image = Image('yolo.jpg', '', '', '', '', 'yolo', datetime.datetime.utcnow(), 'Westeros', [sample_keyword])
    sample_image_2 = Image('yolo-2.jpg', '', '', '', '', 'yolo', datetime.datetime.utcnow(), 'Easteros', [sample_keyword])
    album = Album('test 1', [])
    album_2 = Album('test 2', [sample_image, sample_image_2])
    db.session.add(sample_image)
    db.session.add(sample_image_2)
    db.session.add(album)
    db.session.add(album_2)
    db.session.commit()

class GetAlbumTest(SampleTestCase):
    def test_get_album(self):
        populate_database(db)

        album_id = 1
        album = Album.query.get(album_id)

        response = self.client.get('/api/v1/albums/{}'.format(album_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(album).json)

    def test_get_album_invalid_id(self):
        album_id = 1
        response = self.client.get('/api/v1/albums/{}'.format(album_id))
        expected_response = {'error': 'Album with the ID {} does not exist in the database'.format(album_id)}
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.json, expected_response)

class GetAllAlbumsTest(SampleTestCase):
    def test_get_all_albums(self):
        populate_database(db)

        albums = Album.query.all()

        response = self.client.get('/api/v1/albums')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(albums).json)

    def test_get_all_albums_no_data(self):
        response = self.client.get('/api/v1/albums')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

class CreateAlbumTest(SampleTestCase):
    def test_create_album_no_images(self):
        image_ids = []
        data = {'name': 'test album 1', 'image_ids': image_ids}
        response = self.client.post('/api/v1/albums', json=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        expected_album_id = 1
        expected_response = Album.query.get(expected_album_id)

        self.assertEquals(response.json, jsonify(expected_response).json)
        self.assertEquals(len(expected_response.images), 0)

    def test_create_album_with_images(self):
        populate_database(db)

        image_ids = [1, 2]
        data = {'name': 'test album 1', 'image_ids': image_ids}
        response = self.client.post('/api/v1/albums', json=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        expected_album_id = len(Album.query.all())
        expected_response = Album.query.get(expected_album_id)

        self.assertEquals(response.json, jsonify(expected_response).json)
        self.assertEquals(len(expected_response.images), 2)

    def test_create_album_missing_name(self):
        data = {'image_ids': []}
        response = self.client.post('/api/v1/albums', json=data)

        expected_response = {'error': 'Did not supply name in the JSON payload'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

    def test_create_album_no_json(self):
        response = self.client.post('/api/v1/albums')

        expected_response = {'error': 'Request did not include a JSON payload, try again'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

class UpdateAlbumTest(SampleTestCase):
    def test_update_album_caption(self):
        populate_database(db)

        album_id = 1
        new_name = 'new_name'
        data = {'name': new_name}
        expected_album = Album.query.get(album_id)
        expected_album.name = new_name

        response = self.client.patch('/api/v1/albums/{}'.format(album_id), json=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(expected_album).json)

        expected_album.delete()

    def test_update_album_location(self):
        populate_database(db)

        album_id = 1
        image_ids = [1, 2]
        data = {'image_ids': image_ids}
        expected_album = Album.query.get(album_id)
        expected_album.images = [Image.query.get(id) for id in image_ids]

        response = self.client.patch('/api/v1/albums/{}'.format(album_id), json=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(expected_album).json)

        expected_album.delete()

    def test_update_album_no_data(self):
        album_id = 1
        response = self.client.patch('/api/v1/albums/{}'.format(album_id))

        expected_response = {'error': 'Request did not include a JSON payload, try again'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

class DeleteAlbumTest(SampleTestCase):
    def test_delete_album(self):
        populate_database(db)
        album_id = 1

        album = Album.query.get(album_id)
        response = self.client.delete('/api/v1/albums/{}'.format(album_id))

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Album.query.get(album_id), None)

    def test_delete_album_invalid_id(self):
        album_id = 1
        response = self.client.delete('/api/v1/albums/{}'.format(album_id))

        expected_response = {'error': 'Album with the ID {} does not exist in the database'.format(album_id)}
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.json, jsonify(expected_response).json)
