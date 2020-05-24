from src.category import Category
from src.image import Image
from src.timer import Timer, timer_decorator
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

@timer_decorator
def generate_thumbnails(image_paths, images, thumbnail_dir, output_root_dir):
    # Add all images to the list, and create downsampled and thumbnail images
    image_count = len(image_paths)
    for idx, image_path in enumerate(image_paths):
        image = Image(image_path)
        image.create_thumbnail_image(thumbnail_dir, output_root_dir, 400)
        images.append(image)
        percent = ((idx + 1) / image_count) * 100.0
        print('Thumbnail Generation: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

@timer_decorator
def compress_fullsize_images(images, full_dir, output_root_dir):
    # Add all images to the list, and create downsampled and thumbnail images
    image_count = len(images)
    for idx, image in enumerate(images):
        image.create_downsampled_image(full_dir, output_root_dir, 2400)
        percent = ((idx + 1) / image_count) * 100.0
        print('Fullsize Compression: {:.2f}% - ({} of {})'.format(percent, idx + 1, image_count))

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

    # Sort the categories by name (useful for the sidebar)
    sorted_categories = sorted(categories, key=lambda x: x.pretty_name)
    print('categories are: {}'.format(sorted_categories))

    return sorted_categories

@timer_decorator
def create_spritemaps(thumbnail_dir, sprites_dir, css_categories_dir):
    glue_cmd = 'glue {} --project --cachebuster-filename-only-sprites --img {} --css {} --ratios=2,1.5,1'.format(
            thumbnail_dir,
            sprites_dir,
            css_categories_dir)
    print('Starting to generate the spritemaps')
    subprocess.check_output(glue_cmd, shell=True)
    print('Finished spritemap generation')

@timer_decorator
def compress_spritemaps(categories, sprites_dir, css_categories_dir):
    print('Starting to compress spritemaps')
    for idx, category in enumerate(categories):
        compress_2x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 25% -format jpg {}/{}@2x*.png'.format(sprites_dir, category.name)
        compress_1_5x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 45% -format jpg {}/{}@1.5x*.png'.format(sprites_dir, category.name)
        compress_1x_cmd = 'mogrify -define jpeg:fancy-upsampling=off -quality 65% -format jpg {}/{}_*.png'.format(sprites_dir, category.name)
        sed_cmd = "sed -i -e 's/png/jpg/g' {}/{}.css".format(css_categories_dir, category.name)
        rm_png_cmd = 'rm {}/{}*.png'.format(sprites_dir, category.name)

        subprocess.check_output(compress_2x_cmd, shell=True)
        subprocess.check_output(compress_1_5x_cmd, shell=True)
        subprocess.check_output(compress_1x_cmd, shell=True)
        subprocess.check_output(sed_cmd, shell=True)
        subprocess.check_output(rm_png_cmd, shell=True)
        print('Compressed {} category, ({} of {})'.format(category.name, idx + 1, len(categories)))

def generate_website(input_root_dir, output_root_dir):
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
    css_categories_dir = os.path.join(output_root_dir, 'css/categories')
    css_dir = os.path.join(output_root_dir, 'css')
    js_dir = os.path.join(output_root_dir, 'js')

    directories_to_create = [
            full_dir,
            sprites_dir,
            thumbnail_dir,
            css_categories_dir,
            css_dir,
            js_dir]
    for directory in directories_to_create:
        os.makedirs(directory, exist_ok=True)

    # Collect all the image paths
    image_paths = get_all_images(input_root_dir)
    images = []

    # Generat Thumbnails from the images
    generate_thumbnails(image_paths, images, thumbnail_dir, output_root_dir)

    # Compress the fullsize images
    compress_fullsize_images(images, full_dir, output_root_dir)

    # Generate thumbnail folder and HTML pages for each category
    categories = generate_categories(images)
    for category in categories:
        category.make_thumbnail_folder(thumbnail_dir)
        category.generate_html(template_dir, categories)

    # Create spritemaps from the thumbnails
    shutil.move(full_dir, tmp_full_dir) # Move the full images so they won't be spritemapped
    create_spritemaps(thumbnail_dir, sprites_dir, css_categories_dir)
    shutil.move(tmp_full_dir, full_dir) # Move the full images back
    shutil.rmtree(thumbnail_dir) # Delete the images used to generate the spritemaps

    # Compress the spritemaps
    compress_spritemaps(categories, sprites_dir, css_categories_dir)

    # Print out our runtimes
    Timer().print_times()

    # Copy in the CSS and JS files
    original_js_dir = os.path.join(code_root_dir, 'js')
    js_files = get_all_js(original_js_dir)
    concat_files(js_files, os.path.join(js_dir, 'nicktardif.min.js'))

    original_css_dir = os.path.join(code_root_dir, 'css')
    css_files = get_all_css(original_css_dir)
    concat_files(css_files, os.path.join(css_dir, 'nicktardif.min.css'))
    shutil.copy(os.path.join(original_css_dir, 'default-skin.svg'), css_dir)

    # Copy in the favicon file
    shutil.copy(os.path.join(code_root_dir, 'assets', 'favicon.ico'), output_root_dir)