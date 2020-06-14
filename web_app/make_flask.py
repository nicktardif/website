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

class TestingConfig(Config):
    DATA_DIR = '/tmp'

def set_config(config_type):
    if config_type in ['Production', '', None]:
        app.config.from_object(Config())
    elif config_type in ['Testing', 'testing']:
        app.config.from_object(TestingConfig())

    db_path = 'sqlite:///{}/{}'.format(app.config['DATA_DIR'], app.config['DB_NAME'])
    app.config['SQLALCHEMY_DATABASE_URI'] = db_path

set_config(os.environ.get('FLASK_CONFIG', ''))
