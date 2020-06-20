from web_app.make_flask import app
from web_app.make_database import db

from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password
from web_app.utilities import CustomJSONEncoder
from web_app.views import AlbumView, AuthorizationView, BuildView, ImageView, PortfolioView, AlbumApiView, ImageApiView, PortfolioApiView
from web_app.models import User, Role

migrate = Migrate(app, db)
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
security._state.unauthorized_handler(AuthorizationView.unauthorized)
app.json_encoder = CustomJSONEncoder

# Create a user to test with
#@app.before_first_request
#def create_user():
#    db.create_all()
#    user = user_datastore.create_user(email='nicktardif@gmail.com', password=encrypt_password('some_password'))
#    role = user_datastore.create_role(name='admin', description='Admin access')
#    user_datastore.add_role_to_user(user, role)
#    db.session.commit()
