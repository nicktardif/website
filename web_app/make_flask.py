from flask import Flask
import os
app = Flask(__name__)

class Config():
    DATA_DIR = os.path.join(os.getcwd(), 'web_app', 'static')
    BUILD_DIR = os.path.join(os.getcwd(), 'web_app', 'build')
    BUILD_CSS_DIR = os.path.join(BUILD_DIR, 'css')
    BUILD_JS_DIR = os.path.join(BUILD_DIR, 'js')
    BUILD_SPRITES_DIR = os.path.join(BUILD_DIR, 'sprites')
    DB_NAME = 'app.db'
    API_VERSION = '1.0.0'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '' # load from environment in production
    SECURITY_UNAUTHORIZED_VIEW = '/login'

class TestingConfig(Config):
    DATA_DIR = '/tmp'
    SECRET_KEY = '6720b06e79bb4e1085d29b998293744b'
    LOGIN_DISABLED = True
    TESTING = True

def set_config(config_type):
    if config_type in ['Production', '', None]:
        app.config.from_object(Config())
    elif config_type in ['Testing', 'testing']:
        app.config.from_object(TestingConfig())

    db_path = 'sqlite:///{}/{}'.format(app.config['DATA_DIR'], app.config['DB_NAME'])
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path

    # Prefer environment key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app.config['SECRET_KEY'])
    app.config['SECURITY_PASSWORD_SALT'] = app.config['SECRET_KEY']

set_config(os.environ.get('FLASK_CONFIG', ''))
