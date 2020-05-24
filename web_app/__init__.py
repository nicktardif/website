from web_app.make_flask import app
from web_app.make_database import db

from flask_migrate import Migrate
from web_app.utilities import CustomJSONEncoder
from web_app.views import ImageView, AlbumApiView, ImageApiView, PortfolioApiView

migrate = Migrate(app, db)
app.json_encoder = CustomJSONEncoder
