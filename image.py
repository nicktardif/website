from image_generator import ImageGenerator
import json
import os
import pyexiv2

class Image:
    def __init__(self, original_path):
        self.original_path = original_path

        self.downsampled_path = None
        self.downsampled_size_string = None # Needed in the Jinja template

        self.thumbnail_path = None
        self.thumbnail_basename = None # Needed in the Jinja template

        self.__caption = None
        self.__date = None
        self.__location = None
        self.__keywords = None

    def create_downsampled_image(self, destination_dir, max_dimension):
        self.downsampled_path = ImageGenerator().create_hires(self.original_path, max_dimension, destination_dir)
        no_extension = os.path.splitext(self.downsampled_path)[0]
        underscore_split = no_extension.split('_')
        self.downsampled_size_string = underscore_split[len(underscore_split) - 1]

    def create_thumbnail_image(self, destination_dir, min_dimension):
        self.thumbnail_path = ImageGenerator().create_thumbnail(self.original_path, min_dimension, destination_dir)
        self.thumbnail_basename = os.path.splitext(os.path.basename(self.thumbnail_path))[0]

    def get_caption(self):
        if self.__caption == None:
            self.__parse_metadata()
        return self.__caption

    def get_date(self):
        if self.__date == None:
            self.__parse_metadata()
        return self.__date

    def get_location(self):
        if self.__location == None:
            self.__parse_metadata()
        return self.__location

    def get_keywords(self):
        if self.__keywords == None:
            self.__parse_metadata()
        return self.__keywords

    # ---- Private functions

    def __parse_metadata(self):
        print('parsing metadata for image {}'.format(self.original_path))

        # Read the metadata from the image
        data = pyexiv2.metadata.ImageMetadata(self.original_path)
        data.read()

        # Parse out the keywords
        keywords = []
        if 'Iptc.Application2.Keywords' in data:
            keywords = data['Iptc.Application2.Keywords'].value
        self.__keywords = keywords

        # Parse out the caption
        caption = ''
        if 'Exif.Image.ImageDescription' in data:
            caption = data['Exif.Image.ImageDescription'].value
        self.__caption = caption

        # Parse out the location
        location = ''
        if 'Iptc.Application2.SubLocation' in data:
            location = data['Iptc.Application2.SubLocation'].value[0]
        self.__location = location

        # Parse out the date
        date = data['Exif.Photo.DateTimeOriginal'].value
        self.__date = date
