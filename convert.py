from category import Category
from image import Image
import argparse
import glob
import os

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_root_dir', help='Input dir with JPG images', dest='input_root_dir', required=True)
    parser.add_argument('--output_root_dir', help='Output dir', dest='output_root_dir', required=True)
    args = parser.parse_args()
    return args

def get_all_images(directory):
    image_paths = glob.glob('{}/*.jpg'.format(directory))
    image_paths.extend(glob.glob('{}/*.JPG'.format(directory)))
    return image_paths

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
    args = parse_arguments()
    input_root_dir = args.input_root_dir
    output_root_dir = args.output_root_dir

    # Create the top-level directories for the images to go in
    full_dir = os.path.join(output_root_dir, 'full')
    os.makedirs(full_dir, exist_ok=True)
    thumbnail_dir = output_root_dir

    # Collect all the image paths
    image_paths = get_all_images(input_root_dir)
    images = []

    # Add all images to the list, and create downsampled and thumbnail images
    for image_path in image_paths:
        image = Image(image_path)
        image.create_downsampled_image(full_dir, 2400)
        image.create_thumbnail_image(thumbnail_dir, 400)
        images.append(image)

    # Create the categories
    categories = generate_categories(images)

    # --- Generate thumbnail folder and HTML pages for each category
    for category in categories:
        category.make_thumbnail_folder(thumbnail_dir)

        sorted_categories = sorted(categories, key=lambda x: x.pretty_name)
        category.generate_html(sorted_categories)

if __name__ == "__main__":
    main()
