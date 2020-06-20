from flask import redirect, url_for
from web_app import app

class AuthorizationView():
    def unauthorized():
        return redirect(url_for('security.login'))
