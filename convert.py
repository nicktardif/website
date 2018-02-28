import argparse, glob, json, os, subprocess
import pyexiv2

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_root_dir', help='Input dir with JPG images', dest='input_root_dir', required=True)
    parser.add_argument('--output_root_dir', help='Output dir', dest='output_root_dir', required=True)
    args = parser.parse_args()
    return args

def calculate_dimensions(image, request_dimension, is_max):
    # TODO: Find a Python library to get the width and height
    width = int(subprocess.check_output("identify -format '%w' {}".format(image), shell=True))
    height = int(subprocess.check_output("identify -format '%h' {}".format(image), shell=True))
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

def get_downscaled_file_name(image, output_dir, width, height):
    _, extension = os.path.splitext(image)
    basename = os.path.splitext(os.path.basename(image))[0]
    full_name = '{}_{}x{}{}'.format(basename, width, height, extension)
    downscaled_file = os.path.join(output_dir, full_name)
    return downscaled_file

def create_thumbnail_file(image, output_dir, scaled_width, scaled_height, square_size):
    downscaled_file = get_downscaled_file_name(image, output_dir, square_size, square_size)
    subprocess.check_output("convert -resize {}x{}^ -extent {}x{} -gravity Center \( {} -strip -resize {}x{} \) {}".format(square_size, square_size, square_size, square_size, image, scaled_width, scaled_height, downscaled_file), shell=True)
    return downscaled_file

def create_hires_file(image, output_dir, width, height):
    downscaled_file = get_downscaled_file_name(image, output_dir, width, height)
    subprocess.check_output("convert -strip -interlace Plane -quality 85% {} -resize {}x{} {}".format(image, width, height, downscaled_file), shell=True)
    return downscaled_file

def get_metadata(image):
    metadata = { }

    # Read the metadata from the image
    data = pyexiv2.metadata.ImageMetadata(image)
    data.read()

    # Parse out the keywords
    keywords = []
    if 'Iptc.Application2.Keywords' in data:
        keywords = data['Iptc.Application2.Keywords'].value
    metadata['keywords'] = keywords

    # Parse out the caption
    caption = ''
    if 'Exif.Image.ImageDescription' in data:
        caption = data['Exif.Image.ImageDescription'].value
    metadata['caption'] = caption

    # Parse out the location
    location = ''
    if 'Iptc.Application2.SubLocation' in data:
        location = data['Iptc.Application2.SubLocation'].value[0]
    metadata['location'] = location

    # Parse out the date
    date = data['Exif.Photo.DateTimeOriginal'].value
    metadata['date'] = date

    return metadata

def main():
    args = parse_arguments()
    input_root_dir = args.input_root_dir
    output_root_dir = args.output_root_dir

    full_dir = os.path.join(output_root_dir, 'full')
    os.makedirs(full_dir, exist_ok=True)
    thumbnail_dir = os.path.join(output_root_dir)
    os.makedirs(thumbnail_dir, exist_ok=True)

    images = glob.glob('{}/*.jpg'.format(input_root_dir))
    images.extend(glob.glob('{}/*.JPG'.format(input_root_dir)))

    print(images)
    json_data = {}

    for image in images:
        metadata = get_metadata(image)

        # Make downscaled but still large resolution image
        max_dimension = 2400
        downscaled_width, downscaled_height = calculate_dimensions(image, max_dimension, True)
        downscaled_file = create_hires_file(image, full_dir, downscaled_width, downscaled_height)
        downscaled_file_relative_path = os.path.relpath(downscaled_file, output_root_dir)

        # Make thumbnail image
        min_dimension = 400
        thumbnail_width, thumbnail_height = calculate_dimensions(image, min_dimension, False)
        thumbnail_file = create_thumbnail_file(image, thumbnail_dir, thumbnail_width, thumbnail_height, min_dimension)
        thumbnail_file_relative_path = os.path.relpath(thumbnail_file, output_root_dir)

        print('Downscaled image dimensions: {}x{}'.format(downscaled_width, downscaled_height))
        print('Thumbnail image dimensions: {}x{}'.format(thumbnail_width, thumbnail_height))
        print('downscaled file is: {}, thumbnail file is: {}'.format(downscaled_file, thumbnail_file))

        new_data = {
            'caption': metadata['caption'],
            'date': str(metadata['date']),
            'full_image_path': downscaled_file_relative_path,
            'location': metadata['location'],
            'tags': metadata['keywords'],
            'thumbnail_path': thumbnail_file_relative_path
        }
        image_filename = os.path.basename(image)
        json_data[image_filename] = new_data

    # Print out all the data
    print(json.dumps(json_data, sort_keys=True, indent=4, separators=(',', ': ')))

    # Write out the file
    output_json = os.path.join(output_root_dir, 'images.json')
    with open(output_json, 'w+') as outfile:
        json.dump(json_data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
