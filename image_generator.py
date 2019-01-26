import os
import subprocess

def get_downscaled_file_name(image, output_dir, width, height):
    basename, extension = os.path.splitext(os.path.basename(image))
    full_name = '{}_{}x{}{}'.format(basename, width, height, extension)
    downscaled_file = os.path.join(output_dir, full_name)
    return downscaled_file

def create_thumbnail_file(image, output_dir, scaled_width, scaled_height, square_size):
    downscaled_file = get_downscaled_file_name(image, output_dir, square_size, square_size)
    convert_cmd = "convert -resize {}x{}^ -extent {}x{} -gravity Center \( \"{}\" -strip -resize {}x{} \) \"{}\"".format(
            square_size, square_size,
            square_size, square_size,
            image,
            scaled_width, scaled_height,
            downscaled_file)

    subprocess.check_output(convert_cmd, shell=True)
    return downscaled_file

def create_hires_file(image, output_dir, width, height):
    downscaled_file = get_downscaled_file_name(image, output_dir, width, height)
    convert_cmd = "convert -strip -interlace Plane -quality 85% \"{}\" -resize {}x{} \"{}\"".format(
            image,
            width, height,
            downscaled_file)

    subprocess.check_output(convert_cmd, shell=True)
    return downscaled_file

def calculate_dimensions(image, request_dimension, is_max):
    # TODO: Find a Python library to get the width and height
    width = int(subprocess.check_output("identify -format '%w' \"{}\"".format(image), shell=True))
    height = int(subprocess.check_output("identify -format '%h' \"{}\"".format(image), shell=True))
    print('width is {}'.format(width))
    print('height is {}'.format(height))

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

class ImageGenerator:
    def __init__(self):
        pass

    def create_hires(self, image_path, max_dimension, destination_dir):
        width, height = calculate_dimensions(image_path, max_dimension, True)
        downscaled_file = create_hires_file(image_path, destination_dir, width, height)
        print('Downscaled image dimensions: {}x{}, location: {}'.format(width, height, downscaled_file))
        return downscaled_file

    def create_thumbnail(self, image_path, min_dimension, destination_dir):
        width, height = calculate_dimensions(image_path, min_dimension, False)
        thumbnail_file = create_thumbnail_file(image_path, destination_dir, width, height, min_dimension)
        print('Thumbnail image dimensions: {}x{}, location: {}'.format(width, height, thumbnail_file))
        return thumbnail_file
