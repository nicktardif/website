from web_app.utilities.file_helper import get_full_path
import os
import subprocess
from web_app.models import DownsampledImage, ThumbnailImage

class ImageGenerator:
    def create_thumbnail(image, min_dimension):
        image_full_path = get_full_path(image.original_path)
        width, height = ImageGenerator.calculate_dimensions(image_full_path, min_dimension, False)
        thumbnail_full_path = ImageGenerator.create_thumbnail_file(image_full_path, width, height, min_dimension)
        print('Thumbnail: {}x{}, Destination: {}'.format(width, height, thumbnail_full_path))

        thumbnail = ThumbnailImage(thumbnail_full_path, image)
        return thumbnail

    def create_downsampled(image, max_dimension):
        image_full_path = get_full_path(image.original_path)
        width, height = ImageGenerator.calculate_dimensions(image_full_path, max_dimension, True)
        downsampled_file = ImageGenerator.create_downsampled_file(image_full_path, width, height)
        print('Downsampled: {}x{}, Destination: {}'.format(width, height, downsampled_file))

        downsampled_image = DownsampledImage(downsampled_file, image)
        return downsampled_image

    def calculate_dimensions(image_full_path, request_dimension, is_max):
        # TODO: Find a Python library to get the width and height
        width = int(subprocess.check_output("identify -format '%w' \"{}\"".format(image_full_path), shell=True))
        height = int(subprocess.check_output("identify -format '%h' \"{}\"".format(image_full_path), shell=True))

        aspect_ratio = float(width) / float(height)
        max_dimension = max(width, height)
        min_dimension = min(width, height)

        new_width = width
        new_height = height
        scale_ratio = 1.0

        if(is_max): # Reduce max dimension to request_dimension
            if(max_dimension > request_dimension):
                scale_ratio = float(request_dimension) / float(max_dimension)
        else: # Reduce min dimension to request_dimension
            if(min_dimension > request_dimension):
                scale_ratio = float(request_dimension) / float(min_dimension)

        if(aspect_ratio > 1.0): # Landscape
            new_width = int(max_dimension * scale_ratio)
            new_height = int(min_dimension * scale_ratio)
        else: # Square or portrait
            new_width = int(min_dimension * scale_ratio)
            new_height = int(max_dimension * scale_ratio)

        return new_width, new_height

    def create_thumbnail_file(image_full_path, scaled_width, scaled_height, square_size):
        downscaled_full_path = ImageGenerator.get_downscaled_file_name(image_full_path, square_size, square_size)
        convert_cmd = "convert -resize {}x{}^ -extent {}x{} -gravity Center \( \"{}\" -strip -resize {}x{} \) \"{}\"".format(
                square_size, square_size,
                square_size, square_size,
                image_full_path,
                scaled_width, scaled_height,
                downscaled_full_path)

        subprocess.check_output(convert_cmd, shell=True)
        return downscaled_full_path

    def create_downsampled_file(image_full_path, width, height):
        downscaled_full_path = ImageGenerator.get_downscaled_file_name(image_full_path, width, height)
        convert_cmd = "convert -strip -interlace Plane -quality 85% \"{}\" -resize {}x{} \"{}\"".format(
                image_full_path,
                width, height,
                downscaled_full_path)

        subprocess.check_output(convert_cmd, shell=True)
        return downscaled_full_path

    def get_downscaled_file_name(image_full_path, width, height):
        basename, extension = os.path.splitext(os.path.basename(image_full_path))
        full_name = '{}_{}x{}{}'.format(basename, width, height, extension)
        return get_full_path(full_name)
