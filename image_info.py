import json

class ImageInfo:
    def __init__(self, full_image_path, thumbnail_image_path, caption, date, location, tags):
        self.full_image_path = full_image_path
        self.thumbnail_image_path = thumbnail_image_path
        self.caption = caption
        self.date = date
        self.location = location
        self.tags = tags

    def toJSON(self):
        valid_json_dictionary = {
            'caption': self.caption,
            'date': str(self.date),
            'full_image_path': self.full_image_path,
            'location': self.location,
            'tags': self.tags,
            'thumbnail_path': self.thumbnail_image_path
        }
        return valid_json_dictionary
