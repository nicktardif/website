from web_app import app
from flask_security import roles_required
from functools import wraps

def custom_roles_required(roles):
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            if app.config['TESTING']:
                return f(*args, **kwargs)
            else:
                return roles_required(roles)(f)(*args, **kwargs)
        return wrapped_f
    return wrap
