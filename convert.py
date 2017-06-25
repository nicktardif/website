#!/usr/bin/env python
import argparse, glob, json, os, subprocess

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', help='Input dir with JPG images', dest='input_dir', required=True)
    parser.add_argument('--output_dir', help='Output dir', dest='output_dir', required=True)
    parser.add_argument('--previous_json', help='Previous json to get extra data from', dest='previous_json')
    parser.add_argument('--output_json', help='Output json file', dest='output_json', required=True)
    args = parser.parse_args()
    return args

def resize_file(image, output_dir, new_dimensions):
    _, extension = os.path.splitext(image)
    basename = os.path.splitext(os.path.basename(image))[0]
    downscaled_file = os.path.join(output_dir, basename + '_' + new_dimensions + extension)
    subprocess.check_output("convert {} -resize {} {}".format(image, new_dimensions, downscaled_file), shell=True)
    return downscaled_file

def get_date(image):
    cmd = "exif {} | grep 'Date and Time' | head -n 1 | cut -f 2 -d '|'".format(image)
    date = subprocess.check_output(cmd, shell=True).strip()
    return date

def main():
    args = parse_arguments()
    input_dir = args.input_dir
    output_dir = args.output_dir
    output_json = args.output_json

    images = glob.glob('{}/*.jpg'.format(input_dir))
    images.extend(glob.glob('{}/*.JPG'.format(input_dir)))

    print(images)
    json_data = {}

    for image in images:
        width = int(subprocess.check_output("identify -format '%w' {}".format(image), shell=True))
        height = int(subprocess.check_output("identify -format '%h' {}".format(image), shell=True))
        print('width is {}'.format(width))
        print('height is {}'.format(height))

        max_dimension = 2400
        new_dimensions = '{}x{}'.format(width, height)
        if width > max_dimension | height > max_dimension: # large image
            if width > height: # landscape
                new_dimensions = '2400x1600'
            elif width == height: # square
                new_dimensions = '2400x2400'
            else: # portrait
                new_dimensions = '1600x2400'

        downscaled_file = resize_file(image, output_dir, new_dimensions)

        thumbnail_dimensions = '150x150'
        if width > height: # landscape
            thumbnail_dimensions = '150x100'
        else: # portrait
            thumbnail_dimensions = '100x150'
        thumbnail_file = resize_file(image, output_dir, thumbnail_dimensions)

        print('downscaled file is: {}, thumbnail file is: {}'.format(downscaled_file, thumbnail_file))

        date = get_date(image)
        new_data =  {
                    'original_path': image,
                    'full_image_path': downscaled_file,
                    'date': date,
                    'thumbnail_path': thumbnail_file,
                    'caption': '',
                    'tags': []
                    }
        json_data[image] = new_data

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
    with open(output_json, 'w') as outfile:
        json.dump(json_data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    main()
