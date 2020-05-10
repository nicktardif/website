from web_app.models import Image, Keyword
from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, Image):
                return obj.toJSON()
            if isinstance(obj, Keyword):
                return obj.toJSON()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
