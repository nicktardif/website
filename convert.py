"""
Usage:
    convert.py (INPUT_DIR) [OUTPUT_DIR]
    convert.py (-h | --help)

Arguments:
    INPUT_DIR   Directory to retrieve input images
    OUTPUT_DIR  Directory to create the build in [default: build]

Options:
    -h --help  Show this screen
"""
from category import Category
from docopt import docopt
from image import Image
import datetime
import glob
import os
import shutil
import subprocess

def get_all_images(directory):
    image_paths = glob.glob('{}/*.jpg'.format(directory))
    image_paths.extend(glob.glob('{}/*.JPG'.format(directory)))
    return image_paths

def get_all_js(directory):
    return glob.glob('{}/*.js'.format(directory))

def get_all_css(directory):
    return glob.glob('{}/*.css'.format(directory))

def concat_files(input_files, output_file):
    with open(output_file, 'w') as outfile:
        for current_file in input_files:
            with open(current_file) as infile:
                for line in infile:
                    outfile.write(line)

def generate_categories(images):
    # Make a category for all of the images
    all_category = Category('all', 'All', images)

    # Make a category for each of the keywords
    keyword_categories = {}
    for image in images:
        for keyword in image.get_keywords():

            # All images have the Website keyword
            if keyword == 'Website':
                continue

            # If category already exists, add the image to the category
            if keyword in keyword_categories:
                keyword_categories[keyword].add_image(image)
            # Otherwise, make a new category with this image in it
            else:
                new_category = Category(keyword, keyword, image)
                keyword_categories[keyword] = new_category

    # Make a category for n most recent images - for homepage
    time_sorted_list = sorted(images, key=lambda x: x.get_date(), reverse=True)
    recent_count = 30
    recent_images = time_sorted_list[:recent_count]
    recent_category = Category('index', 'Recent', recent_images)

    categories = [all_category, recent_category]
    categories.extend(keyword_categories.values())
    print('categories are: {}'.format(categories))
    return categories

def main():
    args = docopt(__doc__)
    input_root_dir = args['INPUT_DIR']
    output_root_dir = args['OUTPUT_DIR'] or 'build'
    code_root_dir = os.getcwd()
    template_dir = os.path.join(code_root_dir, 'templates')

    # Ensure that the input and output paths are absolute
    if not os.path.isabs(input_root_dir):
        input_root_dir = os.path.join(os.getcwd(), input_root_dir)
    if not os.path.isabs(output_root_dir):
        output_root_dir = os.path.join(os.getcwd(), output_root_dir)

    # Cleanup and recreate the directory structure
    shutil.rmtree(output_root_dir, True)
    os.makedirs(output_root_dir)
    os.chdir(output_root_dir)

    full_dir = os.path.join(output_root_dir, 'full')
    tmp_full_dir = os.path.join(output_root_dir, '.tmp_full')
    shutil.rmtree(tmp_full_dir, True)
    sprites_dir = os.path.join(output_root_dir, 'sprites')
    thumbnail_dir = os.path.join(output_root_dir, 'thumbnails')
    css_dir = os.path.join(output_root_dir, 'css/categories')

    directories_to_create = [
            full_dir,
            sprites_dir,
            thumbnail_dir,
            css_dir]
    for directory in directories_to_create:
        os.makedirs(directory, exist_ok=True)

    convert_start = datetime.datetime.now()

    # Collect all the image paths
    image_paths = get_all_images(input_root_dir)
    images = []

    # Add all images to the list, and create downsampled and thumbnail images
    image_count = len(image_paths)
    for idx, image_path in enumerate(image_paths):
        image = Image(image_path)
        image.create_downsampled_image(full_dir, 2400)
        image.create_thumbnail_image(thumbnail_dir, 400)
        images.append(image)
        percent = ((idx + 1) / image_count) * 100.0
        print('Image Resizing: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

    # Create the categories
    categories = generate_categories(images)

    # --- Generate thumbnail folder and HTML pages for each category
    for category in categories:
        category.make_thumbnail_folder(thumbnail_dir)

        sorted_categories = sorted(categories, key=lambda x: x.pretty_name)
        category.generate_html(template_dir, sorted_categories)

    convert_end = datetime.datetime.now()

    # Move the full images into the expected location
    shutil.move(full_dir, tmp_full_dir)

    # Create the spritemaps
    glue_start = datetime.datetime.now()
    glue_cmd = 'glue {} --project --cachebuster-filename-only-sprites --img {} --css {} --ratios=2,1.5,1'.format(
            thumbnail_dir,
            sprites_dir,
            css_dir)
    print('Starting to generate the spritemaps')
    subprocess.check_output(glue_cmd, shell=True)
    print('Finished spritemap generation')
    glue_end = datetime.datetime.now()

    # Delete the images used to generate the spritemaps
    old_images = get_all_images(thumbnail_dir)
    for image in old_images:
        os.remove(image)

    # Compress the spritemaps
    compress_start = datetime.datetime.now()

    print('Starting to compress spritemaps')
    for idx, category in enumerate(categories):
        compress_2x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 25% -format jpg {}/{}@2x*.png'.format(sprites_dir, category.name)
        compress_1_5x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 45% -format jpg {}/{}@1.5x*.png'.format(sprites_dir, category.name)
        compress_1x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg {}/{}_*.png'.format(sprites_dir, category.name)
        sed_cmd = "sed -i -e 's/png/jpg/g' {}/{}.css".format(css_dir, category.name)
        rm_png_cmd = 'rm {}/{}*.png'.format(sprites_dir, category.name)

        subprocess.check_output(compress_2x_cmd, shell=True)
        subprocess.check_output(compress_1_5x_cmd, shell=True)
        subprocess.check_output(compress_1x_cmd, shell=True)
        subprocess.check_output(sed_cmd, shell=True)
        subprocess.check_output(rm_png_cmd, shell=True)
        print('Compressed {} category, ({} of {})'.format(category.name, idx + 1, len(categories)))

    compress_end = datetime.datetime.now()

    conversion_time = (convert_end - convert_start).total_seconds()
    glue_time = (glue_end - glue_start).total_seconds()
    compression_time = (compress_end - compress_start).total_seconds()
    print('\nConversion took  {} seconds'.format(conversion_time))
    print('Glue took        {} seconds'.format(glue_time))
    print('Compression took {} seconds'.format(compression_time))
    print('Total time       {} seconds'.format(conversion_time + glue_time + compression_time))

    # Move the full images into the expected location
    shutil.move(tmp_full_dir, full_dir)

    # Copy in the CSS and JS files
    js_dir = os.path.join(code_root_dir, 'js')
    js_files = get_all_js(js_dir)
    concat_files(js_files, 'nicktardif.min.js')

    css_dir = os.path.join(code_root_dir, 'css')
    css_files = get_all_css(css_dir)
    concat_files(css_files, 'nicktardif.min.css')

if __name__ == "__main__":
    main()
