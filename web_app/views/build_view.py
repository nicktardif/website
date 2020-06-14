from web_app import app
from werkzeug.utils import secure_filename
from flask import send_from_directory

class BuildView():
    @app.route('/')
    def build_default_album():
        return send_from_directory(app.config['BUILD_DIR'], 'default.html')

    @app.route('/<path:filename>')
    def build(filename):
        return send_from_directory(app.config['BUILD_DIR'], secure_filename(filename))

    @app.route('/css/<path:filename>')
    def build_css(filename):
        return send_from_directory(app.config['BUILD_CSS_DIR'], secure_filename(filename))

    @app.route('/js/<path:filename>')
    def build_js(filename):
        return send_from_directory(app.config['BUILD_JS_DIR'], secure_filename(filename))

    @app.route('/sprites/<path:filename>')
    def build_sprites(filename):
        return send_from_directory(app.config['BUILD_SPRITES_DIR'], filename)
