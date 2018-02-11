#!/usr/bin/env python3
import argparse, glob, json, os, subprocess

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_root_dir', help='Input dir with JPG images', dest='input_root_dir', required=True)
    parser.add_argument('--output_root_dir', help='Output dir', dest='output_root_dir', required=True)
    parser.add_argument('--previous_json', help='Previous json to get extra data from', dest='previous_json')
    args = parser.parse_args()
    return args

def calculate_dimensions(image, request_dimension, is_max):
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

def get_date(image):
    cmd = "exif {} | grep 'Date and Time (Orig' | head -n 1 | cut -f 2 -d '|'".format(image)
    date = subprocess.check_output(cmd, shell=True).strip()
    return date

def get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]

def main():
    args = parse_arguments()
    input_root_dir = args.input_root_dir
    output_root_dir = args.output_root_dir

    subdirectories = get_immediate_subdirectories(input_root_dir)
    print('subdirectories are:')
    print(subdirectories)

    for input_dir in subdirectories:
        images = glob.glob('{}/{}/*.jpg'.format(input_root_dir, input_dir))
        images.extend(glob.glob('{}/{}/*.JPG'.format(input_root_dir, input_dir)))

        print(images)
        json_data = {}

        for image in images:
            # Make downscaled but still large resolution image
            max_dimension = 2400
            downscaled_width, downscaled_height = calculate_dimensions(image, max_dimension, True)
            print('Downscaled image dimensions: {}x{}'.format(downscaled_width, downscaled_height))
            full_dir = os.path.join(output_root_dir, input_dir, 'full')
            os.makedirs(full_dir, exist_ok=True)
            downscaled_file = create_hires_file(image, full_dir, downscaled_width, downscaled_height)

            # Make thumbnail image
            min_dimension = 400
            thumbnail_width, thumbnail_height = calculate_dimensions(image, min_dimension, False)
            print('Thumbnail image dimensions: {}x{}'.format(thumbnail_width, thumbnail_height))
            thumbnail_dir = os.path.join(output_root_dir, input_dir)
            os.makedirs(thumbnail_dir, exist_ok=True)
            thumbnail_file = create_thumbnail_file(image, thumbnail_dir, thumbnail_width, thumbnail_height, min_dimension)

            print('downscaled file is: {}, thumbnail file is: {}'.format(downscaled_file, thumbnail_file))
            image_filename = os.path.basename(image)

            date = get_date(image)
            new_data =  {
                        'original_path': image_filename,
                        'full_image_path': downscaled_file,
                        'date': date.decode('utf-8'),
                        'thumbnail_path': thumbnail_file,
                        'caption': '',
                        'tags': []
                        }
            json_data[image_filename] = new_data

        # Preserve the captions and tags from previous data
        if(args.previous_json):
            print('previous json file is: {}'.format(args.previous_json))
            previous_data = None
            with open(args.previous_json) as data_file:
                previous_data = json.load(data_file)

            previous_data_set = set(previous_data)
            new_data_set = set(json_data)

            for key in previous_data_set.intersection(new_data_set):
                json_data[key]['tags'] = previous_data[key]['tags']
                json_data[key]['caption'] = previous_data[key]['caption']

        # Write out the file
        output_json = os.path.join(output_root_dir, input_dir, input_dir + '.json')
        with open(output_json, 'w+') as outfile:
            json.dump(json_data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
