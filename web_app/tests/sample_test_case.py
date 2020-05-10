from flask_testing import TestCase
from web_app import app, db

class SampleTestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        db.create_all() # Setup the testing database schema

    def tearDown(self):
        db.session.remove() # Delete the database after the test
        db.drop_all()
