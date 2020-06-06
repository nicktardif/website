from base64 import b64encode
from flask import jsonify
from flask_api import status
from web_app import app, db
from web_app.models import Album, Portfolio
from web_app.tests.sample_test_case import SampleTestCase
import datetime
import os
import unittest

def populate_database(db):
    album = Album('test 1', [])
    album_2 = Album('test 2', [])

    portfolio = Portfolio('test portfolio', 1, [album, album_2])
    db.session.add(album)
    db.session.add(album_2)
    db.session.add(portfolio)
    db.session.commit()

    portfolio_two = Portfolio('smaller portfolio', 1, [album])
    db.session.add(portfolio)
    db.session.commit()

class GetPortfolioTest(SampleTestCase):
    def test_get_portfolio(self):
        populate_database(db)

        portfolio_id = 1
        portfolio = Portfolio.query.get(portfolio_id)

        response = self.client.get('/api/v1/portfolios/{}'.format(portfolio_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(portfolio).json)

    def test_get_portfolio_invalid_id(self):
        portfolio_id = 1
        response = self.client.get('/api/v1/portfolios/{}'.format(portfolio_id))
        expected_response = {'error': 'Portfolio with the ID {} does not exist in the database'.format(portfolio_id)}
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.json, expected_response)

class GetAllPortfoliosTest(SampleTestCase):
    def test_get_all_portfolios(self):
        populate_database(db)

        portfolios = Portfolio.query.all()

        response = self.client.get('/api/v1/portfolios')
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(portfolios).json)

    def test_get_all_portfolios_no_data(self):
        response = self.client.get('/api/v1/portfolios')
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

class CreatePortfolioTest(SampleTestCase):
    def test_create_portfolio_no_albums(self):
        album_ids = []
        data = {'name': 'test portfolio 1', 'primary_album_id': 1, 'album_ids': album_ids}
        response = self.client.post('/api/v1/portfolios', json=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        expected_portfolio_id = 1
        expected_response = Portfolio.query.get(expected_portfolio_id)

        self.assertEquals(response.json, jsonify(expected_response).json)
        self.assertEquals(len(expected_response.albums), 0)

    def test_create_portfolio_with_albums(self):
        populate_database(db)

        album_ids = [1, 2]
        data = {'name': 'test portfolio 1', 'primary_album_id': 1, 'album_ids': album_ids}
        response = self.client.post('/api/v1/portfolios', json=data)
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

        expected_portfolio_id = len(Portfolio.query.all())
        expected_response = Portfolio.query.get(expected_portfolio_id)

        self.assertEquals(response.json, jsonify(expected_response).json)
        self.assertEquals(len(expected_response.albums), 2)

    def test_create_portfolio_missing_name(self):
        data = {'primary_album_id': 1, 'image_ids': []}
        response = self.client.post('/api/v1/portfolios', json=data)

        expected_response = {'error': 'Did not supply name in the JSON payload'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

    def test_create_portfolio_missing_primary_album(self):
        data = {'name': 'my test', 'image_ids': []}
        response = self.client.post('/api/v1/portfolios', json=data)

        expected_response = {'error': 'Did not supply primary_album_id in the JSON payload'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

    def test_create_portfolio_no_json(self):
        response = self.client.post('/api/v1/portfolios')

        expected_response = {'error': 'Request did not include a JSON payload, try again'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

class UpdatePortfolioTest(SampleTestCase):
    def test_update_portfolio_name(self):
        populate_database(db)

        portfolio_id = 1
        new_name = 'new_name'
        data = {'name': new_name}
        expected_portfolio = Portfolio.query.get(portfolio_id)
        expected_portfolio.name = new_name

        response = self.client.patch('/api/v1/portfolios/{}'.format(portfolio_id), json=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(expected_portfolio).json)

        expected_portfolio.delete()

    def test_update_portfolio_albums(self):
        populate_database(db)

        portfolio_id = 1
        album_ids = [1, 2]
        data = {'album_ids': album_ids}
        expected_portfolio = Portfolio.query.get(portfolio_id)
        expected_portfolio.albums = [Album.query.get(id) for id in album_ids]

        response = self.client.patch('/api/v1/portfolios/{}'.format(portfolio_id), json=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(expected_portfolio).json)

        expected_portfolio.delete()

    def test_update_portfolio_primary_album(self):
        populate_database(db)

        portfolio_id = 1
        primary_album_id = 2
        data = {'primary_album_id': primary_album_id}
        expected_portfolio = Portfolio.query.get(portfolio_id)
        expected_portfolio.primary_album_id = primary_album_id

        response = self.client.patch('/api/v1/portfolios/{}'.format(portfolio_id), json=data)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(response.json, jsonify(expected_portfolio).json)

        expected_portfolio.delete()

    def test_update_portfolio_no_data(self):
        portfolio_id = 1
        response = self.client.patch('/api/v1/portfolios/{}'.format(portfolio_id))

        expected_response = {'error': 'Request did not include a JSON payload, try again'}
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(response.json, jsonify(expected_response).json)

    #######

    def test_portfolio_add_album(self):
        populate_database(db)

        portfolio_id = 2
        album_id = 2
        response = self.client.post('/api/v1/portfolios/{}/albums/{}'.format(portfolio_id, album_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        portfolio = Portfolio.query.get(portfolio_id)
        album = Album.query.get(album_id)
        self.assertEquals(album in portfolio.albums, True)

    def test_portfolio_add_album_already_in_portfolio(self):
        populate_database(db)

        portfolio_id = 2
        album_id = 1
        response = self.client.post('/api/v1/portfolios/{}/albums/{}'.format(portfolio_id, album_id))
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

        portfolio = Portfolio.query.get(portfolio_id)
        album = Album.query.get(album_id)
        self.assertEquals(album in portfolio.albums, True)

    def test_portfolio_add_album_does_not_exist(self):
        populate_database(db)

        portfolio_id = 1
        album_id = 10
        response = self.client.post('/api/v1/portfolios/{}/albums/{}'.format(portfolio_id, album_id))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_portfolio_remove_album(self):
        populate_database(db)

        portfolio_id = 2
        album_id = 1
        response = self.client.delete('/api/v1/portfolios/{}/albums/{}'.format(portfolio_id, album_id))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        portfolio = Portfolio.query.get(portfolio_id)
        album = Album.query.get(album_id)
        self.assertEquals(album in portfolio.albums, False)

    def test_portfolio_remove_album_not_in_portfolio(self):
        populate_database(db)

        portfolio_id = 2
        album_id = 2
        response = self.client.delete('/api/v1/portfolios/{}/albums/{}'.format(portfolio_id, album_id))
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_portfolio_remove_album_does_not_exist(self):
        populate_database(db)

        portfolio_id = 1
        album_id = 10
        response = self.client.delete('/api/v1/portfolios/{}/albums/{}'.format(portfolio_id, album_id))
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)


class DeletePortfolioTest(SampleTestCase):
    def test_delete_portfolio(self):
        populate_database(db)
        portfolio_id = 1

        portfolio = Portfolio.query.get(portfolio_id)
        response = self.client.delete('/api/v1/portfolios/{}'.format(portfolio_id))

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(Portfolio.query.get(portfolio_id), None)

    def test_delete_portfolio_invalid_id(self):
        portfolio_id = 1
        response = self.client.delete('/api/v1/portfolios/{}'.format(portfolio_id))

        expected_response = {'error': 'Portfolio with the ID {} does not exist in the database'.format(portfolio_id)}
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEquals(response.json, jsonify(expected_response).json)
