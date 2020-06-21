from os.path import join
from web_app import app

def get_full_path(relative_path):
    return join(app.config['DATA_DIR'], relative_path)
